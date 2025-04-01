from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from config import TELEGRAM_TOKEN
from nlp_processor import HousingCriteriaExtractor
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.url import find_flats


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class HousingBot:
    sale_text = (
            "📋 <b>Чек-лист покупателя квартиры</b>\n\n"
            "🔹 <b>До просмотра:</b>\n"
            "• Проверить квартиру онлайн, сравнить с похожими\n"
            "• Уточнить владельца, тип собственности, торг\n\n"
            "🔹 <b>На просмотре:</b>\n"
            "• Осмотреть подъезд, дом, двор\n"
            "• Внутри — техника, мебель, возможные дефекты\n"
            "• Узнать причину продажи\n\n"
            "🔹 <b>Документы:</b>\n"
            "• Выписка из ЕГРН, паспорт продавца\n"
            "• Основание права собственности (ДКП, дарение...)\n"
            "• Согласие супруга, доверенности, если нужно\n\n"
            "🔹 <b>На сделке:</b>\n"
            "• Договор с суммой, акт, условия оплаты и передачи\n"
            "• Лучше через ячейку, аккредитив или эскроу\n\n"
            "🔹 <b>После сделки:</b>\n"
            "• Выписка из ЕГРН с вами как собственником\n"
            "• Переоформление ЖКХ, счётчики"
        )
    rent_text = (
            "📋 <b>Чек-лист арендатора квартиры</b>\n\n"
            "🔹 <b>При звонке:</b>\n"
            "• Уточните актуальность и адрес\n"
            "• Цена, кто платит коммуналку\n"
            "• Есть ли залог, можно ли с детьми/животными\n"
            "• Когда можно посмотреть квартиру\n\n"
            "🔹 <b>При осмотре:</b>\n"
            "• Подъезд: запах, мусор, состояние\n"
            "• Краны, техника, мебель, потолок — всё ли в порядке\n\n"
            "🔹 <b>Документы:</b>\n"
            "• Паспорт владельца, выписка из ЕГРН\n"
            "• Доверенности, если несколько собственников\n"
            "• У риелтора — доверенность от владельца\n\n"
            "🔹 <b>Безопасность:</b>\n"
            "• Деньги — только после подписания договора и акта\n"
            "• Зафиксируйте показания счётчиков\n"
            "• Проверьте долги за ЖКУ, квартиру на сайте ФССП"
        )
    def __init__(self):
        self.nlp_processor = HousingCriteriaExtractor()
        self.user_contexts = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = (
            "🏠 Добро пожаловать в бота для поиска жилья!",
            "\n\nПросто напишите ваши критерии, например:\n",
            "• 'Ищу 2-комнатную квартиру в Москве до 10 млн рублей площадью 60 м²'",
            "\nМожно отправлять частями: сначала город, потом цену и т.д."
        )
        await update.message.reply_text("\n".join(welcome_text))

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "ℹ️ Команды бота:",
            "/start - Начать работу с ботом",
            "/reset - Сбросить введённые критерии",
            "/help - Что умеет бот"
        )
        await update.message.reply_text("\n".join(help_text))

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        self.user_contexts[user_id] = {}
        await update.message.reply_text("🔄 Контекст очищен. Вы можете начать с начала.")

    async def sale(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.sale_text, parse_mode="HTML")
    
    async def rent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.rent_text, parse_mode="HTML")


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        user_input = update.message.text

        try:
            prev_context = self.user_contexts.get(user_id, {})
            new_context = self.nlp_processor.extract_criteria(
                user_input, prev_context)
            self.user_contexts[user_id] = new_context

            if new_context.get("location") and not all([
                new_context.get("rooms"),
                new_context.get("price"),
                new_context.get("area")
            ]):
                summary_parts = []
                if new_context.get("location"):
                    summary_parts.append(
                        f"Город: {(new_context['location']).capitalize()}")
                if new_context.get("rooms"):
                    summary_parts.append(
                        f"Комнат: {new_context['rooms'] if new_context['rooms'] != 0 else 'Студия'}")
                if new_context.get("price"):
                    summary_parts.append(
                        f"Бюджет до: {new_context['price']:,} ₽")
                if new_context.get("area"):
                    summary_parts.append(
                        f"Площадь до: {new_context['area']} м²")
                if new_context.get("deal"):
                    summary_parts.append(
                        f"Тип: {'Аренда' if new_context['deal'] == 'rent' else 'Покупка'}"
                    )

                if summary_parts:
                    summary_text = "📋 Текущие критерии поиска:\n" + \
                        "\n".join(summary_parts)
                    await update.message.reply_text(summary_text)

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔍 Найти с текущими параметрами",
                            callback_data="search_now"
                        )
                    ]
                ]
                await update.message.reply_text(
                    "Устраивают ли вас текущие параметры или хотите добавить что-то ещё?",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return

            await self._send_flats(update, new_context)

        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")
            await update.message.reply_text(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте сформулировать иначе."
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id

        if query.data == "search_now":
            criteria = self.user_contexts.get(user_id, {})
            await self._send_flats(query, criteria)
            self.user_contexts[user_id] = {}

    async def _send_flats(self, target, criteria: dict):
        summary_parts = []
        if criteria.get("location"):
            summary_parts.append(f"Город: {criteria['location']}")
        if criteria.get("rooms"):
            summary_parts.append(f"Комнат: {criteria['rooms']}")
        if criteria.get("price"):
            summary_parts.append(f"Бюджет до: {criteria['price']:,} ₽")
        if criteria.get("area"):
            summary_parts.append(f"Площадь до: {criteria['area']} м²")
        if criteria.get("deal"):
            summary_parts.append(
                f"Тип: {'Аренда' if criteria['deal'] == 'rent' else 'Покупка'}"
            )

        if summary_parts:
            summary_text = "📋 Текущие критерии поиска:\n" + \
                "\n".join(summary_parts)
            await target.message.reply_text(summary_text)

        location = criteria.get("location")
        if not location:
            await target.message.reply_text("⚠️ Пожалуйста, укажите хотя бы город.")
            return

        rooms = criteria.get("rooms")
        price = criteria.get("price")
        area = criteria.get("area")
        deal = criteria.get("deal") or "sale"

        flats = find_flats(rooms, price, area, location, deal=deal)
        valid_flats = [f for f in flats if isinstance(f, dict)]

        # Отправка квартир
        for flat in valid_flats:
            photo = flat["photo_url"]
            caption = flat["caption"]
            safe_caption = caption[:1020] + \
                "…" if len(caption) > 1024 else caption
            if photo:
                await target.message.reply_photo(photo=photo, caption=safe_caption)
            else:
                await target.message.reply_text(safe_caption)

        # Отправка карты после квартир
        coords = []
        for i, flat in enumerate(valid_flats):
            lat = flat.get("lat")
            lon = flat.get("lon")
            if lat and lon:
                coords.append(f"{lon},{lat},pm2rdl{i+1}")

        if coords:
            points = "~".join(coords)
            map_url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={points}"
            caption = f"🗺 Карта с {len(coords)} квартир{'ой' if len(coords) == 1 else 'ами'}"
            await target.message.reply_photo(photo=map_url, caption=caption)

        # Сброс контекста пользователя
        user_id = target.message.from_user.id if hasattr(
            target, "message") else target.from_user.id
        self.user_contexts[user_id] = {}


def main():
    bot = HousingBot()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("reset", bot.reset))
    app.add_handler(CommandHandler("help", bot.help))
    app.add_handler(CommandHandler("sale", bot.sale))
    app.add_handler(CommandHandler("rent", bot.rent))
    app.add_handler(CallbackQueryHandler(bot.handle_callback))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, bot.handle_message))

    logging.info("----------------------- Бот запущен -----------------------")
    app.run_polling()


if __name__ == "__main__":
    main()