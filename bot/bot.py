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
            "🏠 Добро пожаловать в бота для поиска жилья!\n\n"
            "Просто напишите ваши критерии, например:\n"
            "• 'Ищу 2-комнатную квартиру в Москве до 10 млн рублей площадью 60 м²'\n"
            "• 'Студия в СПб за 5 млн'"
        )
        await update.message.reply_text(welcome_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        try:
            criteria = self.nlp_processor.extract_criteria(update.message.text)
            response = self._format_response(criteria)
        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")
            response = "⚠️ Произошла ошибка при обработке запроса. Попробуйте сформулировать иначе."

        await update.message.reply_text(response)

    def _format_response(self, criteria: dict) -> str:
        """Форматирование ответа"""
        global rooms, location, price, area
        rooms = criteria['rooms']
        location = criteria['location']
        price = criteria['price']
        area = criteria['area']
        return (
            "🔍 Найдены критерии:\n"
            f"• Комнат: {rooms or 'не указано'}\n"
            f"• Локация: {location.capitalize() or 'не указана'}\n"
            f"• Цена: {price or 'не указана'}\n"
            f"• Площадь: {area or 'не указана'}"
        )


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
