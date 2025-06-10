import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from utils import process_ticket_file

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

logging.basicConfig(level=logging.INFO)

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Отправьте PDF билет.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == "application/pdf":
        tg_file = await file.get_file()
        path = f"/tmp/{file.file_name}"
        await tg_file.download_to_drive(path)

        result = process_ticket_file(path, SPREADSHEET_ID)
        msg = "✅ Файл обработан и добавлен в таблицу." if result else "❌ Ошибка при обработке файла."
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Отправьте, пожалуйста, PDF файл.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Document.PDF, handle_file))

# Flask Webhook
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Бот работает."

@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://expense-bot-1.onrender.com/webhook",
        flask_app=flask_app
    )
