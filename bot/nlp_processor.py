from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, Doc
import re
import pymorphy2
import logging
from typing import Dict, List, Optional, Tuple, Union


logger = logging.getLogger(__name__)


class HousingCriteriaExtractor:
    """Извлекает критерии поиска жилья из текста с использованием NLP."""

    def __init__(self) -> None:
        """Инициализирует инструменты Natasha и паттерны для обработки текста."""
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)
        self.morph = pymorphy2.MorphAnalyzer()

        self.city_aliases = {
            "спб": "Санкт-Петербург",
            "мск": "Москва",
            "нск": "Новосибирск",
        }

        self.price_patterns = [
            r"(?:до|за|не больше|не выше|ценой)\s*([\d\s.,]+)[\s]*(?:млн|миллион|тыс|тысяч|руб|р)",
            r"цена\s*[:]?[\s]*([\d\s.,]+)[\s]*(?:млн|миллион|тыс|тысяч|руб|р)",
            r"([\d\s.,]+)[\s]*(?:млн|миллион|тыс|тысяч|руб|р)",
        ]

        self.rooms_patterns = [
            r"(\d+)[\s-]*(?:комнатн[аяую]|комн|комнат|комнаты)",
            r"(?:одно|двух|тр[её]х|четыр[её]х|пяти)(?:комнатн[аяую]|комнатной|комнатную)",
            r"(однушк[ау]|двушк[ау]|тр[её]шк[ау]|четыр[её]хкомнатн[аяую])",
            r"(студия|студию|студийка)",
        ]

        self.area_patterns = [
            r"(?:до|не больше|площадью)\s*(\d+)[\s]*(?:м²|кв\.?м\.?|м\.?|квадратных?|метр|квадратов?)",
            r"(\d+)[\s]*(?:м²|кв\.?м\.?|м\.?|квадратных?|метр|квадратов?)",
        ]

        self.intent_patterns = {
            "rent": [r"снять", r"аренд[ауовать]*", r"аренду", r"сда[её]тся", r"в аренду"],
            "sale": [r"купить", r"покупк[ау]", r"продаж[ауы]", r"прода[её]тся", r"нужна"],
        }

    def extract_criteria(self, text: str, context: Optional[Dict] = None) -> Dict:
        """Извлекает критерии поиска из текста и обновляет контекст."""
        if context is None:
            context = {}
        try:
            doc = self._process_text(text)
            spans = self._get_normalized_spans(doc)
            text_lower = text.lower()

            price, price_match = self._extract_price(text_lower)
            area = self._extract_area(text_lower, price_match)
            rooms = self._extract_rooms(text_lower)
            location = self._extract_location(spans, text_lower)
            deal = (
                self._extract_deal_type(text_lower)
                if self._has_deal_intent(text_lower)
                else context.get("deal", "sale")
            )

            new_context = context.copy()
            for key, value in {
                "rooms": rooms,
                "location": location,
                "price": price,
                "area": area,
                "deal": deal,
            }.items():
                if value is not None:
                    new_context[key] = value

            return new_context
        except Exception as e:
            logger.error(f"Ошибка при извлечении критериев: {e}")
            return context.copy()

    def _has_deal_intent(self, text: str) -> bool:
        """Проверяет наличие намерения аренды или покупки."""
        for patterns in self.intent_patterns.values():
            for pattern in patterns:
                if re.search(pattern, text):
                    return True
        return False

    def _process_text(self, text: str) -> Doc:
        """Обрабатывает текст с помощью Natasha."""
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)
        return doc

    def _get_normalized_spans(self, doc: Doc) -> List[Dict]:
        """Нормализует именованные сущности."""
        spans = []
        for span in doc.spans:
            span.normalize(self.morph_vocab)
            if span.type == "LOC":
                span.normal = self._normalize_city_name(span.normal)
            spans.append(
                {"text": span.text, "normal": span.normal, "type": span.type})
        return spans

    def _normalize_city_name(self, city: str) -> str:
        """Нормализует название города."""
        try:
            if "-" in city:
                parts = [self.morph.parse(
                    part)[0].normal_form for part in city.split("-")]
                normalized = "-".join(parts)
            else:
                normalized = self.morph.parse(city)[0].normal_form

            normalized_lower = normalized.lower()
            return self.city_aliases.get(
                normalized_lower, normalized.capitalize()
            ) or next(
                (full_name for alias, full_name in self.city_aliases.items()
                 if full_name.lower() == normalized_lower),
                normalized.capitalize()
            )
        except Exception:
            logger.warning(f"Ошибка нормализации города: {city}")
            return city

    def _extract_rooms(self, text: str) -> Union[int, str, None]:
        """Извлекает количество комнат или тип 'студия'."""
        word_to_num = {
            "одно": 1, "однушка": 1, "однушку": 1,
            "двух": 2, "двушка": 2, "двушку": 2,
            "трех": 3, "трёх": 3, "трёшка": 3, "трёшку": 3,
            "четырех": 4, "четырёх": 4, "четырёхкомнатную": 4,
            "пяти": 5,
            "студия": "st", "студию": "st", "студийка": "st",
        }

        for word, value in word_to_num.items():
            if word in text:
                return value

        for pattern in self.rooms_patterns:
            match = re.search(pattern, text)
            if match:
                matched_text = match.group(0)
                following_text = text[match.end():match.end() + 10].lower()
                if not any(unit in following_text for unit in ["м²", "кв.м", "м.", "квадрат", "метр"]):
                    if matched_text in word_to_num:
                        return word_to_num[matched_text]
                    if match.group(1) and match.group(1).isdigit():
                        return int(match.group(1))
        return None

    def _extract_location(self, spans: List[Dict], text: str) -> Optional[str]:
        """Извлекает местоположение."""
        for span in spans:
            if span["type"] == "LOC":
                return span["normal"]

        for alias, city in self.city_aliases.items():
            if alias in text:
                return city

        if "москв" in text:
            return "Москва"
        if "петербург" in text or "спб" in text:
            return "Санкт-Петербург"
        if "новосибирск" in text:
            return "Новосибирск"
        if "владивосток" in text:
            return "Владивосток"
        return None

    def _extract_price(self, text: str) -> Tuple[Optional[int], Optional[re.Match]]:
        """Извлекает цену и её позицию."""
        for pattern in self.price_patterns:
            match = re.search(pattern, text)
            if match:
                digits = match.group(1).replace(
                    " ", "").replace(".", "").replace(",", "")
                try:
                    amount = float(digits)
                    if "млн" in match.group(0) or "миллион" in match.group(0):
                        return int(amount * 1_000_000), match
                    if "тыс" in match.group(0) or "тысяч" in match.group(0):
                        return int(amount * 1_000), match
                    if "руб" in match.group(0) or "р" in match.group(0):
                        return int(amount), match
                    return int(amount), match
                except ValueError:
                    continue
        return None, None

    def _extract_area(self, text: str, price_match: Optional[re.Match]) -> Optional[int]:
        """Извлекает площадь, исключая пересечения с ценой."""
        for pattern in self.area_patterns:
            match = re.search(pattern, text)
            if match:
                if price_match and match.start() <= price_match.end() and match.end() <= price_match.end():
                    continue
                if any(unit in text[match.start():match.end() + 10] for unit in ["м²", "кв.м", "м.", "квадратных", "метр", "квадратов"]):
                    return int(match.group(1))
        return None

    def _extract_deal_type(self, text: str) -> str:
        """Определяет тип сделки."""
        for deal_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return deal_type
        return "sale"
