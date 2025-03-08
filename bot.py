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

cur_dir = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(cur_dir, "voice_messages")
text_instruction = """
Этот бот может оформлять ваши мысли касательно бизнес-идеи в фортированного вида отчет.
Бот поддерживает контекст общения. 
Для очистки контекста просто нажмите кнопку "Очистить контекст"
"""

user_info = {}

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def set_user_info(user_id):
    if user_id not in user_info:
        user_info[user_id] = {}
        user_info[user_id]["user_dir"] = os.path.join(SAVE_PATH, str(user_id))
        os.makedirs(user_info[user_id]["user_dir"], exist_ok=True)
        user_info[user_id]["file_context"] = os.path.join(user_info[user_id]["user_dir"], f"context.txt")


async def save_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_user_info(user_id=update.effective_user.id)  # TODO Нужна ли эта строка?
    voice = update.message.voice
    user_id = update.effective_user.id
    user_dir = user_info[user_id]["user_dir"]
    os.makedirs(user_dir, exist_ok=True)

    if voice:
        print("Начало работы")
        file = await context.bot.get_file(voice.file_id)
        fileName = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_path = os.path.join(user_dir, f"{fileName}.ogg")
        text_path_to_llm = os.path.join(user_dir, f"{fileName}.txt")
        text_path_from_llm = os.path.join(user_dir, f"{fileName}.md")
        file_context = user_info[user_id]["file_context"]
        await file.download_to_drive(file_path)

        # text_to_llm = recognize(SAVE_PATH=SAVE_PATH, filename=file.file_id)
        text_to_llm = wisp_recognize(filename=file_path, model="turbo")

        print("Голос преобразован в текст. Передача в LLM")

        with open(text_path_to_llm, "w", encoding="utf-8") as text_file:
            text_file.write(text_to_llm)
        # обновление контекста
        with open(file_context, "a", encoding="utf-8") as text_file:
            text_file.write('\n' + text_to_llm)
        # считывание всего контекста для передачи в llm
        with open(file_context, "r", encoding="utf-8") as text_file:
            text_to_llm = text_file.read()

        # text_from_llm = get_formated_text(text=text_to_llm)
        llm_res = generate(raw_text=text_to_llm, secret_data=secret_data["YCloudML"])
        text_from_llm = llm_res.alternatives[0].text
        print("LLM вернула обработанный текст. Отвечаем им в ТГ и записываем с локальный файл.")
        with open(text_path_from_llm, "w", encoding="utf-8") as text_file:
            text_file.write(text_from_llm)

        chunk_size = 4000
        for i in range(0, len(text_from_llm), chunk_size):
            await update.message.reply_text(f"Обработанный с LLM текст: {text_from_llm[i:i+chunk_size]}")

        print(f"Ответ LLM сохранен: {text_path_from_llm}")
    else:
        await update.message.reply_text("Не удалось получить голосовое сообщение.")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_user_info(user_id=update.effective_user.id)
    keyboard = [["Показать контекст", "Очистить контекст", "инструкция"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text_instruction, reply_markup=reply_markup)


async def button_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    set_user_info(user_id)
    text = update.message.text
    if text == "Очистить контекст":
        with open(user_info[user_id]["file_context"], "w") as f:
            pass
        await update.message.reply_text("Контекст забыт. Начинайте обсуждать новую идею")
    if text == "инструкция":
        await update.message.reply_text(text_instruction)
    if text == "Показать контекст":

        with open(user_info[user_id]["file_context"], "r", encoding="utf-8") as f:
            context_file = f.read()
        if context_file == "":
            await update.message.reply_text("Контекст пустой")
        else:
            await update.message.reply_text(context_file)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE, save_voice))
app.add_handler(CommandHandler("start", cmd_start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_response))

app.run_polling()
