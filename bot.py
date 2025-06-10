import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

from utils import process_ticket_file

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
bot = Bot(token=TOKEN)

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение
app = Flask(__name__)

# Dispatcher и обработчики
dispatcher = Dispatcher(bot, None, workers=2, use_context=True)

def start(update, context):
    update.message.reply_text("Бот запущен. Пришлите PDF файл с билетом.")

def handle_file(update, context):
    file = update.message.document
    if file and file.file_name.endswith(".pdf"):
        file_path = file.get_file().download()
        result = process_ticket_file(file_path, SPREADSHEET_ID)
        if result:
            update.message.reply_text("Файл обработан и добавлен в таблицу.")
        else:
            update.message.reply_text("Ошибка при обработке файла.")
    else:
        update.message.reply_text("Пожалуйста, отправьте PDF файл.")

# Регистрируем хендлеры
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.document.pdf, handle_file))

# Webhook маршрут
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Корневая страница (опционально)
@app.route('/')
def index():
    return "Бот работает!"

# Запуск приложения на Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
