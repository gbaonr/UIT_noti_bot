import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
import time

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
TOKEN = os.environ.get("TOKEN")

URL = "https://student.uit.edu.vn/"
DATA_FILE = "last_notification.json"
BLOCK_IDS = [
    "block-views-hien-thi-bai-viet-moi-block",  # Thong bao chung
    "block-views-tin-noi-bat-block",  # Tin noi bat
]


# load registered users
def load_registered_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except Exception as e:
        return []


# save new registered users
def save_registered_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)


def get_latest_notification(block_id=BLOCK_IDS):
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # thong bao chung
    latest_notifications = soup.find("div", id=block_id[0])
    if latest_notifications:
        notis = latest_notifications.find_all("li")
        tbao_chung = []
        for noti in notis:
            text = noti.text.strip().replace("\n", "")
            link = noti.find("a")["href"]
            tbao_chung.append(
                {
                    "content": text,
                    "link": link,
                }
            )
    # tin noi bat
    latest_notifications = soup.find("div", id=block_id[1])
    if latest_notifications:
        notis = latest_notifications.find_all("tr")
        tin_noi_bat = []
        for noti in notis:
            noti_ = noti.find("td")
            text = noti_.text.strip().replace("\n", "")
            link = noti.find("a")["href"]
            tin_noi_bat.append(
                {
                    "content": text,
                    "link": link,
                }
            )
    return {"tbao_chung": tbao_chung, "tin_noi_bat": tin_noi_bat}


def load_last_notification():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            file = json.load(f)
            return file
    except FileNotFoundError:
        return None


def save_last_notification(notification):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notification, f, ensure_ascii=False, indent=4)


def create_message(news, type="tbao_chung"):
    if type == "tbao_chung":
        text = f"<b>🌟 THÔNG BÁO CHUNG 🌟 </b>\n"
    else:
        text = f"<b>🔥 TIN NỔI BẬT 🔥 </b>\n"
    for new in news:
        text += f"{new['content']}\n"
        link = f"https://student.uit.edu.vn/{new['link']}"
        display_text = "See more"
        message = f'<a href="{link}">{display_text}</a>'
        text += f"{message}\n"
        text += "-" * 20 + "\n"
    return text


def bot_scan_noti():
    """
    - Check for new noti,if there is any, create the messages and return
    --> Return: [message1, message2] with message1 is for tbao_chung and message2 is for tin_noi_bat

    """
    latest_notification = get_latest_notification()
    last_notification = load_last_notification()
    if not last_notification:
        last_notification = {}
    tbao_chung = latest_notification.get("tbao_chung", [])
    tin_noi_bat = latest_notification.get("tin_noi_bat", [])
    old_tbao_chung = last_notification.get("tbao_chung", [])
    old_tin_noi_bat = last_notification.get("tin_noi_bat", [])

    messages = ["Nothing new", "Nothing new"]

    if tbao_chung != old_tbao_chung:
        news = [x for x in tbao_chung if x not in old_tbao_chung]
        messages[0] = create_message(news, type="tbao_chung")
    if tin_noi_bat != old_tin_noi_bat:
        news = [x for x in tin_noi_bat if x not in old_tin_noi_bat]
        messages[1] = create_message(news, type="tin_noi_bat")

    if messages[0] != "Nothing new" or messages[1] != "Nothing new":
        save_last_notification(latest_notification)
    return messages


async def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # message = "From local bot: \n" + message
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    return response.json(), url


# function to send message to all users
async def send_to_all(message):
    users = load_registered_users()
    for user in users:
        await send_message(user, message)


# check for new noti and send
async def background_task():
    global TOKEN
    while True:
        try:
            users = load_registered_users()
            print("\n- Sending messages to: ", ", ".join(map(str, users)))
            messages = bot_scan_noti()
            if messages[0] != "Nothing new":
                # await send_message(user, messages[0])
                await send_to_all(messages[0])
            if messages[1] != "Nothing new":
                # await send_message(user, messages[1])
                await send_to_all(messages[1])
            if messages[0] == messages[1]:
                # await send_message(user, messages[0])
                await send_to_all(messages[1])

        except Exception as e:
            print(f"🚨🚨🚨 Error: {e}")
            print(f"\t- Retrying in 5 minutes")
            await asyncio.sleep(300)
            continue

        time_gap = 8
        next_scan_time = datetime.now() + timedelta(hours=time_gap)
        print(f"\t- Next scan in {next_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(3600 * time_gap)


def is_user(user_id):
    users = load_registered_users()
    if user_id in users:
        return True
    return False
