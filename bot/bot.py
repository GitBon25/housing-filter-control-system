from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import TELEGRAM_TOKEN
from nlp_processor import HousingCriteriaExtractor
import logging
from url import find_flats

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
rooms, location, price, area = "", "", "", ""


class HousingBot:
    def __init__(self):
        self.nlp_processor = HousingCriteriaExtractor()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "🏠 Добро пожаловать в бота для поиска жилья во Владивостоке!\n\n"
            "Просто напишите ваши критерии, например:\n"
            "• 'Ищу 2-комнатную квартиру во Владивостоке до 10 млн рублей площадью 60 м²'"
        )
        await update.message.reply_text(welcome_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            criteria = self.nlp_processor.extract_criteria(update.message.text)
            flats = self._format_response(criteria)

            if isinstance(flats, list) and isinstance(flats[0], dict):
                for flat in flats:
                    photo = flat["photo_url"]
                    caption = flat["caption"]

                    safe_caption = caption[:1020] + \
                        "…" if len(caption) > 1024 else caption

                    if photo:
                        await update.message.reply_photo(photo=photo, caption=safe_caption)
                    else:
                        await update.message.reply_text(safe_caption)
            else:
                for msg in flats:
                    await update.message.reply_text(msg)

        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")
            await update.message.reply_text(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте сформулировать иначе."
            )

    def _format_response(self, criteria: dict) -> list[dict]:
        """Форматирование ответа"""
        global rooms, location, price, area
        rooms = criteria['rooms']
        location = criteria['location']
        price = criteria['price']
        area = criteria['area']
        return find_flats(rooms, price, area)


def main():
    """Запуск бота"""
    bot = HousingBot()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, bot.handle_message))

    # Запуск
    logging.info("-----------------------Бот запущен-----------------------")
    app.run_polling()


if __name__ == "__main__":
    main()
