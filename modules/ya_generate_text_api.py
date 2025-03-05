#!/usr/bin/env python3

from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML


def generate(raw_text, secret_data):
    messages = [
        {
            "role": "system",
            "text":
                "Ты профессиональный бизнес-аналитик. Профессионально подробно отредактируй текст. "
                "поищи нужную готовую информацию в интернете."
                "Отформатируй с необходимыми отступами, шрифтами и обзацами. "
                f"Сформируй удобочитаемый отчет для отправки как сообщение в приложении телеграм:'{raw_text}'",
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
        sdk.models.completions("yandexgpt").configure(temperature=0.5).run(messages)
    )

    print(result)
    return result
    # for alternative in result:
    #     return alternative
    #     print(alternative)


if __name__ == "__main__":
    generate()
