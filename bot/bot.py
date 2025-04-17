import psycopg2
import json
import os
import logging
import sys
import requests
import ffmpeg
import speech_recognition as sr
from typing import Dict, List, Any
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from messages import (
    SALE_TEXT, RENT_TEXT, START_MESSAGE, HELP_MESSAGE, RESET_MESSAGE,
    LAST_RESULTS_NO_FLATS, LAST_RESULTS_FLAT_TEXT, LAST_RESULTS_ERROR,
    VOICE_PROCESSING, VOICE_RECOGNIZED, VOICE_UNRECOGNIZED, VOICE_ERROR,
    CRITERIA_CONFIRMED, CRITERIA_INVALID, TEXT_PROCESSING_ERROR,
    NO_LOCATION, NO_FLATS_FOUND, SEND_FLATS_ERROR,
    MAP_CAPTION, FLAT_SELECTION,
    CALLBACK_FLAT_DETAILS, CALLBACK_INVALID_FLAT, CALLBACK_ERROR
)
from config import TELEGRAM_TOKEN, DATABASE_URL
from services.url import find_flats
from nlp_processor import HousingCriteriaExtractor


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HousingBot:
    """Основной класс бота для поиска жилья."""

    def __init__(self):
        self.nlp_processor = HousingCriteriaExtractor()
        self.user_contexts = {}
        self.recognizer = sr.Recognizer()
        self.conn_str = DATABASE_URL
        self.init_db()

    def init_db(self) -> None:
        """Инициализирует базу данных PostgreSQL."""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        requests JSONB
                    )
                """)
                conn.commit()
            logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Получает данные пользователя из базы."""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT username, requests FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        "username": result[0],
                        "requests": result[1] if result[1] else []
                    }
                return {"username": None, "requests": []}
        except Exception as e:
            logger.error(
                f"Ошибка получения данных пользователя {user_id}: {e}")
            return {"username": None, "requests": []}

    def save_user(self, user_id: int, username: str, requests: List[str]) -> None:
        """Сохраняет данные пользователя в базу."""
        try:
            with psycopg2.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (user_id, username, requests)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET username = EXCLUDED.username, requests = EXCLUDED.requests
                """, (user_id, username, json.dumps(requests)))
                conn.commit()
        except Exception as e:
            logger.error(
                f"Ошибка сохранения данных пользователя {user_id}: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /start."""
        user_id = update.effective_user.id
        username = update.effective_user.username
        user_data = self.get_user(user_id)
        if not user_data["requests"]:
            self.save_user(user_id, username, user_data["requests"])
        await update.message.reply_text(START_MESSAGE)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /help."""
        await update.message.reply_text(HELP_MESSAGE)

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /reset."""
        user_id = update.message.from_user.id
        self.user_contexts[user_id] = {}
        user_data = self.get_user(user_id)
        self.save_user(user_id, user_data["username"], user_data["requests"])
        await update.message.reply_text(RESET_MESSAGE)

    async def sale(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /sale."""
        await update.message.reply_text(SALE_TEXT, parse_mode="HTML")

    async def rent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /rent."""
        await update.message.reply_text(RENT_TEXT, parse_mode="HTML")

    async def last_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /lastresults."""
        user_id = update.message.from_user.id
        user_context = self.user_contexts.get(user_id, {})
        flats = user_context.get("flats", [])
        user_data = self.get_user(user_id)

        logger.info(
            f"Last results requested by user {user_id}. Context: {user_context}")

        if not flats:
            await update.message.reply_text(LAST_RESULTS_NO_FLATS)
            return

        for flat in flats:
            caption = flat.get("caption", "Нет описания")
            safe_caption = caption[:1020] + \
                "…" if len(caption) > 1024 else caption
            flat_text = LAST_RESULTS_FLAT_TEXT.format(caption=safe_caption)
            try:
                if flat.get("photo_url"):
                    await update.message.reply_photo(photo=flat["photo_url"], caption=flat_text)
                else:
                    await update.message.reply_text(flat_text)
            except Exception as e:
                logger.error(f"Ошибка при отправке результата: {e}")
                await update.message.reply_text(LAST_RESULTS_ERROR)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает текстовые и голосовые сообщения."""
        user_id = update.message.from_user.id
        username = update.effective_user.username
        user_data = self.get_user(user_id)

        if update.message.text:
            user_input = update.message.text.strip()
            user_data["requests"].append(user_input)
            self.save_user(user_id, username, user_data["requests"])
            await self._process_text_input(update, user_id, user_input)

        elif update.message.voice:
            await update.message.reply_text(VOICE_PROCESSING, parse_mode=None)
            try:
                file = await update.message.voice.get_file()
                file_url = file.file_path
                audio_data = requests.get(file_url).content

                with open("temp_voice.ogg", "wb") as f:
                    f.write(audio_data)

                ffmpeg.input("temp_voice.ogg").output(
                    "temp_voice.wav").run(quiet=True)

                with sr.AudioFile("temp_voice.wav") as source:
                    audio = self.recognizer.record(source)
                    user_input = self.recognizer.recognize_google(
                        audio, language="ru-RU")

                logger.info(
                    f"Voice message from user {user_id} recognized as: {user_input}")
                await update.message.reply_text(VOICE_RECOGNIZED.format(text=user_input))

                user_data["requests"].append(user_input)
                self.save_user(user_id, username, user_data["requests"])
                await self._process_text_input(update, user_id, user_input)

            except sr.UnknownValueError:
                await update.message.reply_text(VOICE_UNRECOGNIZED)
            except Exception as e:
                logger.error(
                    f"Ошибка распознавания голоса для user {user_id}: {e}")
                await update.message.reply_text(VOICE_ERROR)
            finally:
                for temp_file in ["temp_voice.ogg", "temp_voice.wav"]:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

    async def _process_text_input(self, update: Update, user_id: int, user_input: str) -> None:
        """Обрабатывает текстовый ввод пользователя."""
        try:
            prev_context = self.user_contexts.get(user_id, {})
            if "deal" not in prev_context:
                prev_context["deal"] = "sale"
            new_context = self.nlp_processor.extract_criteria(
                user_input, prev_context)
            new_context["flats"] = prev_context.get("flats", [])
            self.user_contexts[user_id] = new_context

            logger.info(f"Updated context for user {user_id}: {new_context}")

            summary = self._build_criteria_summary(new_context)
            if summary:
                criteria_text = CRITERIA_CONFIRMED.format(summary=summary)
                keyboard = [[InlineKeyboardButton(
                    "🔍 Активировать поиск", callback_data="search_now")]]
                await update.message.reply_text(criteria_text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await update.message.reply_text(CRITERIA_INVALID)

        except Exception as e:
            logger.error(
                f"Ошибка обработки сообщения от {user_id}: {e}", exc_info=True)
            await update.message.reply_text(TEXT_PROCESSING_ERROR)

    def _build_criteria_summary(self, criteria: dict) -> str:
        """Формирует текстовое описание критериев поиска."""
        parts = []
        if criteria.get("location"):
            parts.append(f"Локация: {criteria['location'].capitalize()}")
        if criteria.get("rooms"):
            parts.append(
                f"Комнат: {criteria['rooms'] if criteria['rooms'] != 'st' else 'Студия'}")
        if criteria.get("price"):
            parts.append(f"Максимальная стоимость: {criteria['price']:,} ₽")
        if criteria.get("area"):
            parts.append(f"Площадь: {criteria['area']} м²")
        if criteria.get("deal"):
            parts.append(
                f"Тип: {'Аренда' if criteria['deal'] == 'rent' else 'Покупка'}")
        return "\n".join(parts) if parts else ""

    async def _send_flats(self, target, criteria: dict) -> None:
        """Отправляет пользователю список найденных квартир."""
        if isinstance(target, Update):
            user_id = target.message.from_user.id
            reply_method = target.message.reply_text
        else:
            user_id = target.from_user.id
            reply_method = target.message.reply_text

        current_context = self.user_contexts.get(user_id, {}).copy()
        if "deal" not in current_context:
            current_context["deal"] = "sale"
        current_context.update(criteria)

        logger.info(
            f"Sending flats for user {user_id}. Criteria: {current_context}")

        if not current_context.get("location"):
            await reply_method(NO_LOCATION)
            return

        try:
            flats = find_flats(
                current_context.get("rooms"),
                current_context.get("price"),
                current_context.get("area"),
                current_context["location"],
                deal=current_context.get("deal", "sale")
            )
            valid_flats = [f for f in flats if isinstance(f, dict)]

            if (not valid_flats or
                (len(valid_flats) == 1 and
                 valid_flats[0].get("caption", "") == "🔍 Квартиры не найдены по заданным параметрам." and
                 valid_flats[0].get("photo_url", "") == "")):
                current_context["flats"] = []
                self.user_contexts[user_id] = current_context
                await reply_method(NO_FLATS_FOUND)
                return

            current_context["flats"] = valid_flats
            self.user_contexts[user_id] = current_context
            logger.info(
                f"Context updated with flats for user {user_id}: {self.user_contexts[user_id]}")

            for flat in valid_flats:
                caption = flat.get("caption", "Нет описания")
                safe_caption = caption[:1020] + \
                    "…" if len(caption) > 1024 else caption
                flat_text = LAST_RESULTS_FLAT_TEXT.format(caption=safe_caption)
                try:
                    if flat.get("photo_url"):
                        await target.message.reply_photo(photo=flat["photo_url"], caption=flat_text)
                    else:
                        await target.message.reply_text(flat_text)
                except Exception as e:
                    logger.error(f"Ошибка отправки квартиры: {e}")

            await self._send_map(target, valid_flats)
            await self._send_flat_selection_keyboard(target, valid_flats)

        except Exception as e:
            logger.error(
                f"Ошибка в _send_flats для user {user_id}: {e}", exc_info=True)
            await reply_method(SEND_FLATS_ERROR)

    async def _send_map(self, target, flats: list) -> None:
        """Отправляет карту с метками квартир."""
        coords = [f"{flat['lon']},{flat['lat']},pm2rdl{i+1}"
                  for i, flat in enumerate(flats)
                  if flat.get("lat") and flat.get("lon")]
        if coords:
            points = "~".join(coords)
            map_url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={points}"
            count = len(coords)
            ending = "ой" if count == 1 else "ами"
            caption = MAP_CAPTION.format(count=count, ending=ending)
            try:
                await target.message.reply_photo(photo=map_url, caption=caption)
            except Exception as e:
                logger.error(f"Ошибка отправки карты: {e}")

    async def _send_flat_selection_keyboard(self, target, flats: list) -> None:
        """Отправляет клавиатуру для выбора квартиры."""
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{i+1}", callback_data=f"flat_{i}")
                                        for i in range(len(flats))]])
        await target.message.reply_text(FLAT_SELECTION, reply_markup=keyboard)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает callback-запросы."""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_context = self.user_contexts.get(user_id, {})
        user_data = self.get_user(user_id)
        self.save_user(user_id, user_data["username"], user_data["requests"])

        logger.info(
            f"Callback received for user {user_id}. Context: {user_context}")

        try:
            if query.data == "search_now":
                await self._send_flats(query, user_context)
            elif query.data.startswith("flat_"):
                idx = int(query.data.split("_")[1])
                flats = user_context.get("flats", [])
                if 0 <= idx < len(flats):
                    flat = flats[idx]
                    details = flat.get("details") or flat.get(
                        "caption", "Информация недоступна")
                    deal_type = user_context.get("deal", "sale")
                    checklist = RENT_TEXT if deal_type == "rent" else SALE_TEXT
                    await query.message.reply_text(
                        CALLBACK_FLAT_DETAILS.format(
                            details=details, checklist=checklist),
                        parse_mode="HTML"
                    )
                else:
                    await query.message.reply_text(CALLBACK_INVALID_FLAT)
        except Exception as e:
            logger.error(
                f"Ошибка в callback для {user_id}: {e}", exc_info=True)
            await query.message.reply_text(CALLBACK_ERROR)

def main() -> None:
    """Запускает бота."""
    try:
        bot = HousingBot()
        app = Application.builder().token(TELEGRAM_TOKEN).build()

        handlers = [
            CommandHandler("start", bot.start),
            CommandHandler("reset", bot.reset),
            CommandHandler("help", bot.help),
            CommandHandler("sale", bot.sale),
            CommandHandler("rent", bot.rent),
            CommandHandler("lastresults", bot.last_results),
            CallbackQueryHandler(bot.handle_callback),
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           bot.handle_message),
            MessageHandler(filters.VOICE, bot.handle_message),
        ]

        for handler in handlers:
            app.add_handler(handler)

        logger.info(
            "----------------------- Бот запущен -----------------------")
        app.run_polling()
    except Exception as e:
        logger.critical(
            f"Критическая ошибка при запуске бота: {e}", exc_info=True)

if __name__ == "__main__":
    main()