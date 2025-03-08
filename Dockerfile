FROM python:3.12
WORKDIR /app
COPY linx_require.txt .
RUN pip install --upgrade pip
RUN pip install setuptools-rust
RUN pip install git+https://github.com/openai/whisper.git
RUN apt update && apt install -y ffmpeg 
RUN pip install -r linx_require.txt
CMD ["python", "bot.py"]