import whisper


def wisp_recognize(filename: str, model: str):
    model = whisper.load_model(model)
    result = model.transcribe(filename, fp16=False)
    return result["text"]
