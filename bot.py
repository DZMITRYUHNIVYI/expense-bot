import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from utils import process_ticket_file
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Отправьте PDF файл билета.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == "application/pdf":
        file_path = await file.get_file()
        local_path = await file_path.download_to_drive()
        logger.info(f"Получен PDF: {local_path}")
        success = process_ticket_file(local_path, SPREADSHEET_ID)
        await update.message.reply_text("Файл обработан." if success else "Ошибка при обработке файла.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте PDF файл.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()
