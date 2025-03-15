import os

from telegram import Update
from telegram.ext import ContextTypes

from modules import global_data


def set_prompt(path_file, content):
    with open(path_file, "w", encoding="utf-8") as promptFile:
        promptFile.write(content)


def get_prompt(path_file):
    if not os.path.exists(path_file):
        set_prompt(path_file, "")
    with open(path_file, "r", encoding="utf-8") as promptFile:
        content = promptFile.read()
    return content
