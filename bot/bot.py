from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
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
import aiohttp  # Для асинхронных HTTP-запросов к Yandex API

# Корректное добавление пути к модулям
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.url import find_flats

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HousingBot:
    SALE_TEXT = (
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

    RENT_TEXT = (
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

    DEAL = ""

    def __init__(self):
        self.nlp_processor = HousingCriteriaExtractor()
        self.user_contexts = {}
        self.yandex_api_key = "cb7b3954-781a-4f71-bcd7-57248fcb586b"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        welcome_text = (
            "🏠 Добро пожаловать в бота для поиска жилья!\n\n"
            "Просто напишите ваши критерии, например:\n"
            "• 'Ищу 2-комнатную квартиру в Москве до 10 млн рублей площадью 60 м²'"
        )
        await update.message.reply_text(welcome_text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = (
            "ℹ️ Команды бота:\n"
            "/start - Начать работу с ботом\n"
            "/reset - Сбросить введённые критерии\n"
            "/help - Что умеет бот\n"
            "/sale - Чек-лист покупателя\n"
            "/rent - Чек-лист арендатора\n"
            "/lastresults - Показать последние результаты"
        )
        await update.message.reply_text(help_text)

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        self.user_contexts[user_id] = {}
        await update.message.reply_text("🔄 Контекст очищен. Вы можете начать с начала.")

    async def sale(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(self.SALE_TEXT, parse_mode="HTML")

    async def rent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(self.RENT_TEXT, parse_mode="HTML")

    async def last_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        user_context = self.user_contexts.get(user_id, {})
        flats = user_context.get("flats", [])

        logger.info(f"Last results requested by user {user_id}. Context: {user_context}")

        if not flats:
            await update.message.reply_text("❌ Нет сохранённых результатов.")
            return

        for flat in flats:
            caption = flat.get("caption", "Нет описания")
            safe_caption = caption[:1020] + "…" if len(caption) > 1024 else caption
            try:
                if flat.get("photo_url"):
                    await update.message.reply_photo(photo=flat["photo_url"], caption=safe_caption)
                else:
                    await update.message.reply_text(safe_caption)
            except Exception as e:
                logger.error(f"Ошибка при отправке результата: {e}")
                await update.message.reply_text("⚠️ Ошибка при отображении результата.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        user_input = update.message.text.strip()

        try:
            prev_context = self.user_contexts.get(user_id, {})
            new_context = self.nlp_processor.extract_criteria(user_input, prev_context)
            new_context["flats"] = prev_context.get("flats", [])
            self.user_contexts[user_id] = new_context

            logger.info(f"Updated context for user {user_id}: {new_context}")

            if new_context.get("location") and not all([
                new_context.get("rooms"),
                new_context.get("price"),
                new_context.get("area")
            ]):
                summary = self._build_criteria_summary(new_context)
                if summary:
                    await update.message.reply_text(summary)
                    keyboard = [[InlineKeyboardButton(
                        "🔍 Найти с текущими параметрами", callback_data="search_now")]]
                    await update.message.reply_text(
                        "Устраивают ли вас текущие параметры или хотите добавить что-то ещё?",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                return

            await self._send_flats(update, new_context)

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения от {user_id}: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при обработке запроса. Попробуйте ещё раз.")

    def _build_criteria_summary(self, criteria: dict) -> str:
        parts = []
        if criteria.get("location"):
            parts.append(f"Город: {criteria['location'].capitalize()}")
        if criteria.get("rooms"):
            parts.append(f"Комнат: {criteria['rooms'] if criteria['rooms'] != 0 else 'Студия'}")
        if criteria.get("price"):
            parts.append(f"Бюджет до: {criteria['price']:,} ₽")
        if criteria.get("area"):
            parts.append(f"Площадь до: {criteria['area']} м²")
        if criteria.get("deal"):
            self.DEAL = criteria['deal']
            parts.append(f"Тип: {'Аренда' if criteria['deal'] == 'rent' else 'Покупка'}")
        return "📋 Текущие критерии поиска:\n" + "\n".join(parts) if parts else ""

    async def _get_nearby_infrastructure(self, lon: float, lat: float) -> str:
        categories = ["магазин", "больница", "школа"]
        nearby = []
        
        for category in categories:
            url = (
                f"https://search-maps.yandex.ru/v1/?text={category}&ll={lon},{lat}"
                f"&spn=0.01,0.01&lang=ru_RU&apikey={self.yandex_api_key}"
            )
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            features = data.get("features", [])
                            if features:
                                # Берем ближайший объект для каждой категории
                                feature = features[0]
                                name = feature["properties"].get("name", "Без названия")
                                desc = feature["properties"].get("description", "")
                                nearby.append(f"• {category.capitalize()}: {name} ({desc})")
                        else:
                            logger.error(f"Yandex API вернул ошибку для {category}: {response.status}")
            except Exception as e:
                logger.error(f"Ошибка запроса к Yandex API для {category}: {e}")

        if not nearby:
            return "🏬 Ближайшая инфраструктура: ничего не найдено."
        return "🏬 Ближайшая инфраструктура:\n" + "\n".join(nearby)

    async def _send_flats(self, target, criteria: dict) -> None:
        # Корректное определение user_id
        if isinstance(target, Update):  # Обычное сообщение
            user_id = target.message.from_user.id
            reply_method = target.message.reply_text
        else:  # CallbackQuery
            user_id = target.from_user.id
            reply_method = target.message.reply_text

        # Получаем текущий контекст и обновляем его
        current_context = self.user_contexts.get(user_id, {}).copy()
        current_context.update(criteria)
        
        logger.info(f"Sending flats for user {user_id}. Criteria: {criteria}")

        if not criteria.get("location"):
            await reply_method("⚠️ Пожалуйста, укажите хотя бы город.")
            return

        try:
            flats = find_flats(
                criteria.get("rooms"),
                criteria.get("price"),
                criteria.get("area"),
                criteria["location"],
                deal=criteria.get("deal", "sale")
            )
            valid_flats = [f for f in flats if isinstance(f, dict)]
            
            # Сохраняем квартиры в контекст перед отправкой
            current_context["flats"] = valid_flats
            self.user_contexts[user_id] = current_context
            logger.info(f"Context updated with flats for user {user_id}: {self.user_contexts[user_id]}")

            if not valid_flats:
                await reply_method("🔍 По вашим критериям ничего не найдено.")
                return

            for flat in valid_flats:
                caption = flat.get("caption", "Нет описания")
                safe_caption = caption[:1020] + "…" if len(caption) > 1024 else caption
                try:
                    if flat.get("photo_url"):
                        await target.message.reply_photo(photo=flat["photo_url"], caption=safe_caption)
                    else:
                        await target.message.reply_text(safe_caption)
                except Exception as e:
                    logger.error(f"Ошибка отправки квартиры: {e}")

            await self._send_map(target, valid_flats)
            await self._send_flat_selection_keyboard(target, valid_flats)

        except Exception as e:
            logger.error(f"Ошибка в _send_flats для user {user_id}: {e}", exc_info=True)
            await reply_method("⚠️ Ошибка при поиске квартир.")

    async def _send_map(self, target, flats: list) -> None:
        coords = [f"{flat['lon']},{flat['lat']},pm2rdl{i+1}" 
                 for i, flat in enumerate(flats) 
                 if flat.get("lat") and flat.get("lon")]
        if coords:
            points = "~".join(coords)
            map_url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={points}"
            caption = f"🗺 Карта с {len(coords)} квартир{'ой' if len(coords) == 1 else 'ами'}"
            try:
                await target.message.reply_photo(photo=map_url, caption=caption)
            except Exception as e:
                logger.error(f"Ошибка отправки карты: {e}")

    async def _send_flat_selection_keyboard(self, target, flats: list) -> None:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{i+1}", callback_data=f"flat_{i}")
            for i in range(len(flats))
        ]])
        await target.message.reply_text("Выберите номер квартиры для подробностей:", reply_markup=keyboard)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_context = self.user_contexts.get(user_id, {})

        logger.info(f"Callback received for user {user_id}. Context: {user_context}")

        try:
            if query.data == "search_now":
                await self._send_flats(query, user_context)
            elif query.data.startswith("flat_"):
                idx = int(query.data.split("_")[1])
                flats = user_context.get("flats", [])
                if 0 <= idx < len(flats):
                    flat = flats[idx]
                    details = flat.get("details") or flat.get("caption", "Информация недоступна")
                    infra = await self._get_nearby_infrastructure(flat["lon"], flat["lat"])
                    full_details = f"{details}\n\n{infra}\n\n{self.RENT_TEXT if self.DEAL == 'rent' else self.SALE_TEXT}"
                    await query.message.reply_text(f"Подробности:\n{full_details}", parse_mode="HTML")
                else:
                    await query.message.reply_text("⚠️ Квартира не найдена.")
        except Exception as e:
            logger.error(f"Ошибка в callback для {user_id}: {e}", exc_info=True)
            await query.message.reply_text("⚠️ Ошибка при обработке запроса.")

def main() -> None:
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
            MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message)
        ]

        for handler in handlers:
            app.add_handler(handler)

        logger.info("----------------------- Бот запущен -----------------------")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)

if __name__ == "__main__":
    main()