#!/usr/bin/env python3

from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML


def generate(raw_text, secret_data, prompt, temperature=.5):
    if prompt == "":
        return "Задайте промпт"
    messages = [
        {
            "role": "system",
            "text":
                f"{prompt}"
                "обработай следующий текст:'"
                f"{raw_text}'",
        },
        # {
        #     "role": "user",
        #     "text": raw_text,
        # },
    ]
    sdk = YCloudML(
        folder_id=secret_data["folder_id"],
        auth=secret_data["auth"],
    )

    result = (
        sdk.models.completions("yandexgpt").configure(temperature=temperature).run(messages)
    )

    return result.alternatives[0].text
    # for alternative in result:
    #     return alternative
    #     print(alternative)
