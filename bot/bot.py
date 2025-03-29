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
import logging, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.url import find_flats

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class HousingBot:
    def __init__(self):
        self.nlp_processor = HousingCriteriaExtractor()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = (
            "🏠 Добро пожаловать в бота для поиска жилья!",
            "\n\nПросто напишите ваши критерии, например:\n",
            "• 'Ищу 2-комнатную квартиру в Москве до 10 млн рублей площадью 60 м²'",
            "\nМожно отправлять частями: сначала город, потом цену и т.д."
        )
        await update.message.reply_text("\n".join(welcome_text))

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.nlp_processor.context.clear()
        await update.message.reply_text("🔄 Контекст очищен. Вы можете начать с начала.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            criteria = self.nlp_processor.extract_criteria(update.message.text)
            flats = self._format_response(criteria)

            if isinstance(flats, list) and flats and isinstance(flats[0], dict):
                for flat in flats:
                    photo = flat["photo_url"]
                    caption = flat["caption"]

                    safe_caption = caption[:1020] + "…" if len(caption) > 1024 else caption

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

    def _format_response(self, criteria: dict) -> list[dict | str]:
        required_fields = {
            "rooms": "количество комнат",
            "location": "город",
            "price": "максимальная цена",
            "area": "максимальная площадь"
        }

        missing = [name for key, name in required_fields.items() if criteria.get(key) is None]
        if missing:
            return [
                f"⚠️ Пожалуйста, укажите: {', '.join(missing)}",
                f"📋 Уже указано:" + ",".join([
                    f"{name}: {criteria.get(key)}" for key, name in required_fields.items() if criteria.get(key) is not None
                ])
            ]

        rooms = criteria["rooms"]
        location = criteria["location"]
        price = criteria["price"]
        area = criteria["area"]
        deal = criteria.get("deal", "sale")

        self.nlp_processor.context.clear()
        return find_flats(rooms, price, area, location, deal=deal)
        
    

def main():
    bot = HousingBot()
    bot.nlp_processor.context.clear()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("reset", bot.reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    logging.info("----------------------- Бот запущен -----------------------")
    app.run_polling()


if __name__ == "__main__":
    main()
