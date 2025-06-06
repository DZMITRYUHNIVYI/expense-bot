from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utils import process_ticket_file, process_voice

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь PDF билет или голосовое сообщение.")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    if not document or document.mime_type != "application/pdf":
        await update.message.reply_text("Пожалуйста, отправьте PDF файл.")
        return

    file_obj = await context.bot.get_file(document.file_id)
    file_path = file_obj.file_path

    result = await process_ticket_file(file_path, SPREADSHEET_ID)

    if result:
        await update.message.reply_text("Файл обработан и добавлен в таблицу.")
    else:
        await update.message.reply_text("Ошибка при обработке файла.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        return

    voice_file = await voice.get_file()
    voice_path = voice_file.file_path

    result = await process_voice(voice_path, SPREADSHEET_ID)

    if result:
        await update.message.reply_text("Голосовое сообщение обработано.")
    else:
        await update.message.reply_text("Ошибка при обработке голосового сообщения.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()


if __name__ == "__main__":
    main()
