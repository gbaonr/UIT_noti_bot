from dotenv import load_dotenv
import os
import requests

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


# bot = Bot(token="YOUR_BOT_TOKEN")
# chat_id = "CHAT_ID_CUA_BAN"
# message = "[Nhấn vào đây để truy cập Google](https://www.google.com)"
# bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    return response.json(), url


# Sử dụng hàm với liên kết
link = "https://example.com/very/long/url"
display_text = "Nhấn vào đây để xem chi tiết"
message = f'<a href="{link}">{display_text}</a>'
send_telegram_message(message)
