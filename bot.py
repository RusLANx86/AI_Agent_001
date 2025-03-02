from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

from modules.ya_generate_text_api import generate
from modules.whisper_lib import wisp_recognize

# from modules.speech_rec import recognize

TOKEN = "8115806824:AAHfyqz0lN4L1F0nanIFuSkwAKmDzroVirk"
SAVE_PATH = os.path.abspath("") + "\\voice_messages"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

path_ai_model_3b = "F:\huggingface\models--Qwen--Qwen2.5-Coder-3B-Instruct-GGUF\snapshots\qwen2.5-coder-3b-instruct-q8_0.gguf"
path_ai_model_7b = r"D:\Users\Ruslan\Documents\PyCharm_Projects\llama_ccp_python\src\models\llama-2-7b.Q8_0.gguf"

llm = LlamaCpp(model_path=path_ai_model_3b, n_ctx=1024)


# async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def get_formated_text(text):
    prompt = PromptTemplate.from_template("{text}")
    formatted_prompt = prompt.format(text=text)
    print("Prompt:")
    print(formatted_prompt)
    llm_answer_txt = llm(formatted_prompt)
    return llm_answer_txt


async def save_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice = update.message.voice
    if voice:
        print("Начало работы")
        file = await context.bot.get_file(voice.file_id)
        file_path = os.path.join(SAVE_PATH, f"{voice.file_id}.ogg")
        text_path = os.path.join(SAVE_PATH, f"{voice.file_id}.md")
        await file.download_to_drive(file_path)

        # text = recognize(SAVE_PATH=SAVE_PATH, filename=file.file_id)
        text = wisp_recognize(filename=file_path, model="turbo")

        print("Голос преобразован в текст. Передача в LLM")

        # llm_txt = get_formated_text(text=text)
        llm_res = generate(raw_text=text)
        llm_txt = llm_res.alternatives[0].text
        print("LLM вернула обработанный текст. Отвечаем им в ТГ и записываем с локальный файл.")
        await update.message.reply_text(f"Обработанный с LLM текст: {llm_txt}")
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(llm_txt)

        print(f"Ответ LLM сохранен: {text_path}")
    else:
        await update.message.reply_text("Не удалось получить голосовое сообщение.")


app = ApplicationBuilder().token(TOKEN).build()
# app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.VOICE, save_voice))

app.run_polling()
