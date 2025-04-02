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

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        welcome_text = (
            "=== ВХОДЯЩЕЕ СООБЩЕНИЕ ОДОБРЕНО ===\n"
            "Гражданин.\n\n"
            "Ваше подключение к Системе ЖилРаспределения зарегистрировано.\n"
            "Для активации поиска жилплощади укажите параметры в утверждённом формате.\n\n"
            "Пример корректного запроса:\n"
            "• Требуется: 2-комнатная жилплощадь. Локация: Москва. Максимальная стоимость: 10 000 000 рублей. Площадь: 60 м².\n\n"
            "Несанкционированные запросы приравниваются к саботажу.\n"
            "Министерство Благосостояния следит за вашей лояльностью.\n"
            "=== СООБЩЕНИЕ ЗАВЕРШЕНО ==="
        )
        await update.message.reply_text(welcome_text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = (
            "=== ИНФОРМАЦИЯ УТВЕРЖДЕНА ===\n"
            "Гражданин.\n\n"
            "Вам предоставлен доступ к директивам Системы ЖилРаспределения:\n"
            "• /start — Инициализация поиска жилплощади\n"
            "• /reset — Обнуление текущих параметров (по приказу Министерства)\n"
            "• /help — Перечень утверждённых команд\n"
            "• /sale — Чек-лист для покупки (утверждён Министерством Изобилия)\n"
            "• /rent — Чек-лист для аренды (утверждён Министерством Благосостояния)\n"
            "• /lastresults — Просмотр последних данных поиска\n\n"
            "Любое отклонение от директив фиксируется.\n"
            "Министерство Правды наблюдает.\n"
            "=== КОНЕЦ ПЕРЕДАЧИ ==="
        )
        await update.message.reply_text(help_text)

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        self.user_contexts[user_id] = {}
        reset_text = (
            "=== ПЕРЕЗАГРУЗКА ОДОБРЕНА ===\n"
            "Гражданин.\n\n"
            "Ваши параметры поиска аннулированы по приказу Системы.\n"
            "Для продолжения укажите новые данные в установленном формате.\n\n"
            "Министерство Благосостояния подтверждает вашу лояльность.\n"
            "=== ОПЕРАЦИЯ ЗАВЕРШЕНА ==="
        )
        await update.message.reply_text(reset_text)

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
            no_results_text = (
                "=== РЕЗУЛЬТАТЫ ПОИСКА: НУЛЕВЫЕ ===\n"
                "Гражданин.\n\n"
                "Ваши предыдущие запросы не содержат данных.\n"
                "Повторное обращение без параметров расценивается как нарушение.\n\n"
                "Министерство Правды напоминает:\n"
                "\"Отсутствие результата — ваша ответственность.\"\n"
                "=== СОЕДИНЕНИЕ ПРЕРВАНО ==="
            )
            await update.message.reply_text(no_results_text)
            return

        for flat in flats:
            caption = flat.get("caption", "Нет описания")
            safe_caption = caption[:1020] + "…" if len(caption) > 1024 else caption
            location = flat.get("location", "Локация не указана")
            price = flat.get("price", "Неизвестно")
            area = flat.get("area", "Неизвестно")
            rooms = flat.get("rooms", "Неизвестно")
            floor_info = flat.get("floor_info", "Неизвестно")
            flat_text = (
                "=== ОБЪЕКТ НАЙДЕН ===\n\n"
                f"📍 Локация:\n{location}\n\n"
                f"💰 Стоимость:\n{price} рублей (утверждено Министерством Изобилия)\n\n"
                f"📐 Параметры:\nПлощадь: {area} м²  Комнат: {rooms}\nЭтаж: {floor_info}\n\n"
                f"🏢 Описание объекта (одобрено ЖилПравдой):\n{safe_caption}\n\n"
                "⚠️ Предупреждение:\nНесанкционированный доступ к данным вне Системы запрещён.\n\n"
                "Министерство Благосостояния подтверждает соответствие.\n"
                "=== КОНЕЦ ПЕРЕДАЧИ ==="
            )
            try:
                if flat.get("photo_url"):
                    await update.message.reply_photo(photo=flat["photo_url"], caption=flat_text)
                else:
                    await update.message.reply_text(flat_text)
            except Exception as e:
                logger.error(f"Ошибка при отправке результата: {e}")
                await update.message.reply_text(
                    "=== СИСТЕМНЫЙ СБОЙ ===\n"
                    "Гражданин.\n\n"
                    "Обработка данных прервана по техническим причинам.\n\n"
                    "Ваше поведение зафиксировано.\n"
                    "Министерство Правды наблюдает.\n"
                    "=== СОЕДИНЕНИЕ ПРЕРВАНО ==="
                )

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
                    criteria_text = (
                        "=== КРИТЕРИИ ЗАФИКСИРОВАНЫ ===\n"
                        "Гражданин.\n\n"
                        f"Ваши параметры зарегистрированы в Системе:\n{summary}\n\n"
                        "Уточните данные или подтвердите поиск.\n"
                        "Несанкционированное бездействие недопустимо.\n\n"
                        "Министерство Благосостояния ожидает вашего решения.\n"
                        "=== ОЖИДАНИЕ ПОДТВЕРЖДЕНИЯ ==="
                    )
                    keyboard = [[InlineKeyboardButton("🔍 Активировать поиск", callback_data="search_now")]]
                    await update.message.reply_text(criteria_text, reply_markup=InlineKeyboardMarkup(keyboard))
                return

            await self._send_flats(update, new_context)

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения от {user_id}: {e}", exc_info=True)
            error_text = (
                "=== ОШИБКА ОБНАРУЖЕНА ===\n"
                "Гражданин.\n\n"
                "Ваш запрос признан несоответствующим стандартам ЖилПравды.\n"
                "Причина: Техническое нарушение протокола.\n\n"
                "Рекомендация:\n"
                "Повторите ввод в утверждённом формате.\n\n"
                "Пример:\n"
                "• Требуется: 1-комнатная жилплощадь. Локация: Москва. Максимальная стоимость: 5 000 000 рублей.\n\n"
                "Повторные сбои приведут к пересмотру вашего статуса.\n"
                "Министерство Правды следит за вами.\n"
                "=== КОНЕЦ ДИАГНОСТИКИ ==="
            )
            await update.message.reply_text(error_text)

    def _build_criteria_summary(self, criteria: dict) -> str:
        parts = []
        if criteria.get("location"):
            parts.append(f"Локация: {criteria['location'].capitalize()}")
        if criteria.get("rooms"):
            parts.append(f"Комнат: {criteria['rooms'] if criteria['rooms'] != 0 else 'Студия'}")
        if criteria.get("price"):
            parts.append(f"Максимальная стоимость: {criteria['price']:,} рублей")
        if criteria.get("area"):
            parts.append(f"Площадь: {criteria['area']} м²")
        if criteria.get("deal"):
            self.DEAL = criteria["deal"]
            parts.append(f"Тип: {'Аренда' if criteria['deal'] == 'rent' else 'Покупка'}")
        return "\n".join(parts) if parts else ""

    async def _send_flats(self, target, criteria: dict) -> None:
        if isinstance(target, Update):
            user_id = target.message.from_user.id
            reply_method = target.message.reply_text
        else:
            user_id = target.from_user.id
            reply_method = target.message.reply_text

        current_context = self.user_contexts.get(user_id, {}).copy()
        current_context.update(criteria)

        logger.info(f"Sending flats for user {user_id}. Criteria: {criteria}")

        if not criteria.get("location"):
            no_location_text = (
                "=== ОШИБКА ОБНАРУЖЕНА ===\n"
                "Гражданин.\n\n"
                "Ваш запрос признан неполным.\n"
                "Причина: Отсутствие данных о локации.\n\n"
                "Рекомендация:\n"
                "Укажите утверждённую локацию.\n\n"
                "Пример:\n"
                "• Требуется: 2-комнатная жилплощадь. Локация: Москва.\n\n"
                "Нарушение директивы приведёт к ограничению доступа.\n"
                "Министерство Правды фиксирует.\n"
                "=== КОНЕЦ ДИАГНОСТИКИ ==="
            )
            await reply_method(no_location_text)
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

            current_context["flats"] = valid_flats
            self.user_contexts[user_id] = current_context
            logger.info(f"Context updated with flats for user {user_id}: {self.user_contexts[user_id]}")

            if not valid_flats:
                no_flats_text = (
                    "=== ЖИЛПЛОЩАДЬ НЕ ОБНАРУЖЕНА ===\n"
                    "Гражданин.\n\n"
                    "По указанным параметрам объекты отсутствуют в реестре ЖилРаспределения.\n\n"
                    "Рекомендация:\n"
                    "Расширьте параметры поиска или дождитесь обновления квот.\n\n"
                    "Министерство Изобилия напоминает:\n"
                    "Желание превыше возможностей — путь к диссидентству.\n"
                    "=== ПОИСК ПРЕРВАН ==="
                )
                await reply_method(no_flats_text)
                return

            for flat in valid_flats:
                caption = flat.get("caption", "Нет описания")
                safe_caption = caption[:1020] + "…" if len(caption) > 1024 else caption
                flat_text = (
                    "=== ОБЪЕКТ НАЙДЕН ===\n\n"
                    f"🏢 Описание объекта (одобрено ЖилПравдой):\n{safe_caption}\n\n"
                    "⚠️ Предупреждение:\nНесанкционированный доступ к данным вне Системы запрещён.\n\n"
                    "Министерство Благосостояния подтверждает соответствие.\n"
                    "=== КОНЕЦ ПЕРЕДАЧИ ==="
                )
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
            logger.error(f"Ошибка в _send_flats для user {user_id}: {e}", exc_info=True)
            error_text = (
                "=== СИСТЕМНЫЙ СБОЙ ===\n"
                "Гражданин.\n\n"
                "Обработка запроса прервана по техническим причинам.\n\n"
                "Ваше поведение зафиксировано.\n"
                "Повторите попытку для подтверждения лояльности.\n\n"
                "Министерство Правды наблюдает.\n"
                "=== СОЕДИНЕНИЕ ПРЕРВАНО ==="
            )
            await reply_method(error_text)

    async def _send_map(self, target, flats: list) -> None:
        coords = [f"{flat['lon']},{flat['lat']},pm2rdl{i+1}"
                  for i, flat in enumerate(flats)
                  if flat.get("lat") and flat.get("lon")]
        if coords:
            points = "~".join(coords)
            map_url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={points}"
            caption = f"🗺 Карта с {len(coords)} объектов (утверждено ЖилПравдой)"
            try:
                await target.message.reply_photo(photo=map_url, caption=caption)
            except Exception as e:
                logger.error(f"Ошибка отправки карты: {e}")

    async def _send_flat_selection_keyboard(self, target, flats: list) -> None:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"{i+1}", callback_data=f"flat_{i}")
            for i in range(len(flats))
        ]])
        selection_text = (
            "=== ВЫБОР УТВЕРЖДЁН ===\n"
            "Гражданин.\n\n"
            "Для получения расширенных данных выберите номер объекта:\n"
            "Отказ от выбора приравнивается к мыслепреступлению.\n\n"
            "Министерство Благосостояния ждёт.\n"
            "=== ОЖИДАНИЕ РЕШЕНИЯ ==="
        )
        await target.message.reply_text(selection_text, reply_markup=keyboard)

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
                    full_details = (
                        "=== ПОВТОРНЫЙ ДОСТУП УТВЕРЖДЁН ===\n\n"
                        "Гражданин.\n"
                        "Ваш запрос на повторное рассмотрение объекта обработан.\n\n"
                        f"🏢 Данные объекта (переутверждено ЖилПравдой):\n{details}\n\n"
                        f"{self.RENT_TEXT if self.DEAL == 'rent' else self.SALE_TEXT}\n\n"
                        "! Внимание !\n"
                        "Частые запросы фиксируются как избыточная активность.\n"
                        "Министерство Благосостояния контролирует вашу дисциплину.\n"
                        "=== ПЕРЕДАЧА ЗАВЕРШЕНА ==="
                    )
                    await query.message.reply_text(full_details, parse_mode="HTML")
                else:
                    not_found_text = (
                        "=== ОШИБКА ОБНАРУЖЕНА ===\n"
                        "Гражданин.\n\n"
                        "Запрошенный объект отсутствует в реестре ЖилПравды.\n\n"
                        "Рекомендация:\n"
                        "Проверьте номер объекта.\n\n"
                        "Повторные ошибки приведут к пересмотру вашего статуса.\n"
                        "Министерство Правды фиксирует.\n"
                        "=== КОНЕЦ ДИАГНОСТИКИ ==="
                    )
                    await query.message.reply_text(not_found_text)
        except Exception as e:
            logger.error(f"Ошибка в callback для {user_id}: {e}", exc_info=True)
            error_text = (
                "=== СИСТЕМНЫЙ СБОЙ ===\n"
                "Гражданин.\n\n"
                "Обработка запроса прервана по техническим причинам.\n\n"
                "Ваше поведение зафиксировано.\n"
                "Повторите попытку для подтверждения лояльности.\n\n"
                "Министерство Правды наблюдает.\n"
                "=== СОЕДИНЕНИЕ ПРЕРВАНО ==="
            )
            await query.message.reply_text(error_text)

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