from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os, json
from datetime import datetime
# from langchain_community.llms import LlamaCpp
# from langchain.prompts import PromptTemplate

from modules.ya_generate_text_api import generate
from modules.whisper_lib import wisp_recognize

# from modules.speech_rec import recognize

with open("secret_data.json", "r") as secret_file:
    secret_data = json.loads(secret_file.read())

TOKEN = secret_data["BOT_TOKEN"]
SAVE_PATH = os.path.abspath("") + "\\voice_messages"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


async def save_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.voice
    user_id = update.effective_user.id
    user_dir = os.path.join(SAVE_PATH, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    if voice:
        print("Начало работы")
        file = await context.bot.get_file(voice.file_id)
        fileName = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_path = os.path.join(user_dir, f"{fileName}.ogg")
        text_path_to_llm = os.path.join(user_dir, f"{fileName}.txt")
        text_path_from_llm = os.path.join(user_dir, f"{fileName}.md")
        await file.download_to_drive(file_path)

        # text_to_llm = recognize(SAVE_PATH=SAVE_PATH, filename=file.file_id)
        text_to_llm = wisp_recognize(filename=file_path, model="turbo")
        with open(text_path_to_llm, "w", encoding="utf-8") as text_file:
            text_file.write(text_to_llm)
        print("Голос преобразован в текст. Передача в LLM")

        # text_from_llm = get_formated_text(text=text_to_llm)
        llm_res = generate(raw_text=text_to_llm, secret_data=secret_data["YCloudML"])
        text_from_llm = llm_res.alternatives[0].text
        print("LLM вернула обработанный текст. Отвечаем им в ТГ и записываем с локальный файл.")
        await update.message.reply_text(f"Обработанный с LLM текст: {text_from_llm}")
        with open(text_path_from_llm, "w", encoding="utf-8") as text_file:
            text_file.write(text_from_llm)

        print(f"Ответ LLM сохранен: {text_path_from_llm}")
    else:
        await update.message.reply_text("Не удалось получить голосовое сообщение.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Новая идея"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите кнопку:", reply_markup=reply_markup)


async def button_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Новая идея":
        await update.message.reply_text("Кнопка нажата!")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, save_voice))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_response))

app.run_polling()
