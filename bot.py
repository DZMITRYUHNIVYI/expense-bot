import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from utils import process_ticket_file

# Конфигурация
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Telegram Bot и Application
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Flask приложение
flask_app = Flask(__name__)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Отправьте PDF билет.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file and file.mime_type == "application/pdf":
        tg_file = await file.get_file()
        path = f"/tmp/{file.file_name}"
        await tg_file.download_to_drive(path)
        result = process_ticket_file(path, SPREADSHEET_ID)
        msg = "✅ Файл обработан." if result else "❌ Не удалось обработать файл."
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Поддерживаются только PDF файлы.")

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.PDF, handle_file))

# Webhook обработчик
@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

@flask_app.route("/", methods=["GET"])
def index():
    return "Бот работает."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    PORT = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=PORT)
