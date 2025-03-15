import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
SAVE_PATH = os.path.join(parent_dir, "voice_messages")

user_info = {}


def user_exists(user_id):
    return user_id in user_info


def set_user_info(user_id):
    if not user_exists(user_id):
        user_info[user_id] = {}
        user_info[user_id]["user_dir"] = os.path.join(SAVE_PATH, str(user_id))
        user_info[user_id]["file_context"] = os.path.join(user_info[user_id]["user_dir"], f"context.txt")
        user_info[user_id]["file_prompt"] = os.path.join(user_info[user_id]["user_dir"], f"prompt.txt")

        if not os.path.exists(user_info[user_id]["user_dir"]):
            os.makedirs(user_info[user_id]["user_dir"])
            with open(user_info[user_id]["file_context"], "w", encoding="utf-8") as f:
                f.write("")
            with open(user_info[user_id]["file_prompt"], "w", encoding="utf-8") as f:
                f.write("")
            user_info[user_id]["prompt"] = ""
        else:
            try:
                with open(user_info[user_id]["file_prompt"], "r", encoding="utf-8") as f:
                    user_info[user_id]["prompt"] = f.read().strip()
            except:
                user_info[user_id]["prompt"] = ""
