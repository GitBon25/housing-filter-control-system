from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7581155991:AAG0PJmGu8VZ2DdRrncLyAyyp22sWrdRl0c'


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот для поиска квартир по заданным Вами критериям. ')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    response = 'Я вас не понял, повторите, пожалуйста.'

    if 'площадь' in text:
        response = 'Введите площадь искомой квартиры:'
    elif 'количество комант' in text:
        response = 'Введите количество комнат в искомой квартире:'
    elif 'местоположение' in text:
        response = 'Введите местоположение искомой квартиры:'
    elif 'цена' in text:
        response = 'Введите цену искомой квартиры:'

    await update.message.reply_text(response)


if __name__ == '__main__':
    print('Запуск бота...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print('Ожидание сообщений...')
    app.run_polling(poll_interval=3)
