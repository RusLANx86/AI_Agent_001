import speech_recognition as sr
import soundfile as sf  # pip install pysoundfile
import os


def recognize(SAVE_PATH: str, filename):
    # Конвертация в WAV
    wav_path = os.path.join(SAVE_PATH, f"{filename}.wav")
    file_path = os.path.join(SAVE_PATH, f"{filename}.ogg")

    data, samplerate = sf.read(file_path)
    sf.write(wav_path, data, samplerate)

    # subprocess.run(["ffmpeg", "-i", file_path, wav_path, "-y"], stdout=subprocess.DEVNULL,
    #                stderr=subprocess.DEVNULL)

    # Распознавание речи
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language="ru-RU")
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ("Не удалось распознать голосовое сообщение.")


if __name__ == "__main__":
    filename = ("D:/Users/Ruslan/Documents/PyCharm_Projects/sunday_currywurst_speeche/bot/voice_messages/"
                "AwACAgIAAxkBAAMqZ7rkuPIWmeYMG1E3Zjd3hSAAAVrTAALiXwACMtDZSUiN27ibx6YrNgQ")
    text = recognize(
        SAVE_PATH="voice_messages",
        filename=filename
    )
    with open(f"{filename}.txt", "w", encoding="utf-8") as text_file:
        text_file.write(text)
