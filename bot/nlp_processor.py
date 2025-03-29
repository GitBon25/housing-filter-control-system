from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    Doc
)
import re
import pymorphy2


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
            r'(?:до|за)\s*(\d+)\s*(?:млн|миллион|тыс|тысяч)',
            r'цена\s*[:]??\s*(\d+)\s*(?:млн|миллион|тыс|тысяч)',
            r'(\d+)\s*(?:млн|миллион|тыс|тысяч)\s*(?:руб|р)'
        ]

        self.rooms_patterns = [
            r'(\d+)[\s-]*(?:комнатн|к|комн|комнат|комнаты)',
            r'(?:одно|двух|трех|четырех|пяти)(?:комнатн|комнатной|комнатную)',
            r'(?:студи[юя]|однушк[ау])'
        ]

        self.intent_patterns = {
            'rent': [
                r'снять', r'аренд[ауовать]*', r'аренду', r'сда[её]тся', r'в аренду'
            ],
            'sale': [
                r'купить', r'покупк[ау]', r'продаж[ауы]', r'прода[её]тся'
            ]
        }

    def extract_criteria(self, text: str) -> dict:
        doc = self._process_text(text)
        spans = self._get_normalized_spans(doc)

        return {
            'rooms': self._extract_rooms(text),
            'location': self._extract_location(spans, text),
            'price': self._extract_price(text),
            'area': self._extract_area(text),
            'deal': self._extract_deal_type(text)
        }

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
            return city

    def _extract_rooms(self, text: str) -> int | str:
        text_lower = text.lower()

        if any(word in text_lower for word in ['однушку', 'однушка']):
            return 1

        if any(word in text_lower for word in ['студию', 'студия']):
            return "st"

        for pattern in self.rooms_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if match.group(1):
                    return int(match.group(1))
                else:
                    text_num = match.group(0)
                    if 'одно' in text_num: return 1
                    if 'двух' in text_num: return 2
                    if 'трех' in text_num: return 3
                    if 'четырех' in text_num: return 4
                    if 'пяти' in text_num: return 5
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
                amount = float(match.group(1))
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
        match = re.search(r'(\d+)\s*(?:м²|кв\.?м\.|м\.|квадратных|метр)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_deal_type(self, text: str) -> str:
        text = text.lower()
        for deal_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return deal_type
        return 'sale'
