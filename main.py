import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
# TOKEN = os.getenv("TOKEN")
# CHAT_ID = os.getenv("CHAT_ID")
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
URL = "https://student.uit.edu.vn/"
DATA_FILE = "last_notification.json"


def get_latest_notification():
    print("[Scanning new notifications]", end="  ")
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    latest_notifications = soup.find(
        "div", id="block-views-hien-thi-bai-viet-moi-block"
    )

    if latest_notifications:
        notis = latest_notifications.find_all("li")
        notis_table = []
        for noti in notis:
            text = noti.text.strip()
            content = text.split("-")[0].strip()
            date = text.split("-")[1].strip()
            hour_minute = text.split("-")[2].strip()
            link = noti.find("a")["href"]
            notis_table.append(
                {
                    "content": content,
                    "date": date,
                    "hour_minute": hour_minute,
                    "link": link,
                }
            )
        return notis_table

    return None


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


def create_message(news):
    text = "🔔🔔🔔🔔🔔\n"
    for new in news:
        text += f"<b>{new['content']}</b>\n"
        text += f"Time: {new['date']} - {new['hour_minute']}\n"
        text += f"Link: https://student.uit.edu.vn/{new['link']}\n"
        text += "-" * 20 + "\n"
    return text


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    return response.json(), url


def work_flow():
    latest_notification = get_latest_notification()
    last_notification = load_last_notification()

    if not last_notification:
        last_notification = []
    if latest_notification and latest_notification != last_notification:
        news = [x for x in latest_notification if x not in last_notification]
        message = create_message(news)
        response, url = send_telegram_message(message)
        print(f"Found new noti(s)  - {datetime.now()}")
        if not response["ok"]:
            print(f"\t- Error sent ❌")
            print(f"\t- {response}")
            print(f"\t- url: {url}")
            if not CHAT_ID:
                print(f"\t- CHAT_ID not found")
            if not TOKEN:
                print(f"\t- TOKEN not found")
        else:
            save_last_notification(latest_notification)
            print(f"\t- Sent to telegram ✅")
    else:
        print(f"No new notis found. - {datetime.now()}")
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": "Nothing new! ✔ ", "parse_mode": "HTML"}
        response = requests.post(url, json=payload)
        print(f"\t- sent: {response}")


if __name__ == "__main__":
    while True:
        try:
            work_flow()
        except Exception as e:
            print(f"🚨🚨🚨 Error: {e}")
            print(f"\t- Retrying in 5 minutes")
            time.sleep(300)
            continue

        next_scan_time = datetime.now() + timedelta(hours=12)
        print(f"\t- Next scan in {next_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

        time.sleep(3600 * 12)
