from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    Doc
)
import re
import pymorphy2
import logging


class HousingCriteriaExtractor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)
        self.morph = pymorphy2.MorphAnalyzer()

        self.city_aliases = {
            'спб': 'Санкт-Петербург',
            'мск': 'Москва',
            'нск': 'Новосибирск'
        }

        self.price_patterns = [
            r'(?:до|за|не больше|не выше)\s*([\d\s]+)[\s]*(?:млн|миллион|тыс|тысяч)',
            r'цена\s*[:]??\s*([\d\s]+)[\s]*(?:млн|миллион|тыс|тысяч)',
            r'([\d\s]+)[\s]*(?:млн|миллион|тыс|тысяч)[\s]*(?:руб|р)?'
        ]

        self.rooms_patterns = [
            r'(\d+)[\s-]*(?:комнатн|к|комн|комнат|комнаты)',
            r'(?:одно|двух|тр[её]х|четыр[её]х|пяти)(?:комнатн|комнатной|комнатную)',
            r'(однушк[ау]|двушк[ау]|тр[её]шк[ау]|четыр[её]хкомнатн[ау])',
            r'(студия|студию|студийка)'
        ]

        self.intent_patterns = {
            'rent': [
                r'снять', r'аренд[ауовать]*', r'аренду', r'сда[её]тся', r'в аренду'
            ],
            'sale': [
                r'купить', r'покупк[ау]', r'продаж[ауы]', r'прода[её]тся'
            ]
        }

    def extract_criteria(self, text: str, context: dict | None = None) -> dict:
        if context is None:
            context = {}
        try:
            doc = self._process_text(text)
            spans = self._get_normalized_spans(doc)

            result = {
                'rooms': self._extract_rooms(text),
                'location': self._extract_location(spans, text),
                'price': self._extract_price(text),
                'area': self._extract_area(text),
                'deal': self._extract_deal_type(text) if self._has_deal_intent(text) else None
            }

            for key, value in result.items():
                if value is not None:
                    context[key] = value

            return context.copy()
        except Exception as e:
            logging.error(f"Ошибка при извлечении критериев: {e}")
            return context.copy()

    def _has_deal_intent(self, text: str) -> bool:
        text = text.lower()
        for patterns in self.intent_patterns.values():
            for pattern in patterns:
                if re.search(pattern, text):
                    return True
        return False

    def _process_text(self, text: str) -> Doc:
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)
        return doc

    def _get_normalized_spans(self, doc: Doc) -> list:
        spans = []
        for span in doc.spans:
            span.normalize(self.morph_vocab)
            if span.type == "LOC":
                span.normal = self._normalize_city_name(span.normal)
            spans.append({
                'text': span.text,
                'normal': span.normal,
                'type': span.type
            })
        return spans

    def _normalize_city_name(self, city: str) -> str:
        try:
            if '-' in city:
                parts = [self.morph.parse(part)[0].normal_form for part in city.split('-')]
                normalized = '-'.join(parts)
            else:
                parsed = self.morph.parse(city)[0]
                normalized = parsed.normal_form

            normalized_lower = normalized.lower()
            for alias, full_name in self.city_aliases.items():
                if alias == normalized_lower or full_name.lower() == normalized_lower:
                    return full_name

            return normalized
        except Exception:
            logging.warning(f"Ошибка нормализации города: {city}")
            return city

    def _extract_rooms(self, text: str) -> int | str:
        text_lower = text.lower()

        word_to_num = {
            'одно': 1, 'однушка': 1, 'однушку': 1,
            'двух': 2, 'двушка': 2, 'двушку': 2,
            'трех': 3, 'трёшка': 3, 'трёшку': 3,
            'четырех': 4, 'четырёхкомнатную': 4,
            'пяти': 5,
            'студия': 'st', 'студию': 'st', 'студийка': 'st'
        }

        for word, value in word_to_num.items():
            if word in text_lower:
                return value

        for pattern in self.rooms_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if match.group(1).isdigit():
                    return int(match.group(1))

        return None

    def _extract_location(self, spans: list, text: str) -> str:
        for span in spans:
            if span['type'] == 'LOC':
                return span['normal']

        text_lower = text.lower()
        for alias, city in self.city_aliases.items():
            if alias in text_lower:
                return city

        if 'москв' in text_lower:
            return 'Москва'
        if 'петербург' in text_lower or 'спб' in text_lower:
            return 'Санкт-Петербург'
        if 'новосибирск' in text_lower:
            return 'Новосибирск'

        return None

    def _extract_price(self, text: str) -> int:
        text_lower = text.lower()
        for pattern in self.price_patterns:
            match = re.search(pattern, text_lower)
            if match:
                digits = match.group(1).replace(" ", "")
                amount = float(digits)
                if 'млн' in match.group(0) or 'миллион' in match.group(0):
                    return int(amount * 1_000_000)
                elif 'тыс' in match.group(0) or 'тысяч' in match.group(0):
                    return int(amount * 1_000)
                return int(amount)

        match = re.search(r'(\d+)\s*(?:руб|р)', text_lower)
        if match:
            return int(match.group(1))

        return None

    def _extract_area(self, text: str) -> int:
        match = re.search(r'(?:до\s*)?(\d+)\s*(?:м²|кв\.?м\.|м\.|квадратных|метр|квадратов)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_deal_type(self, text: str) -> str:
        text = text.lower()
        for deal_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return deal_type
        return None
