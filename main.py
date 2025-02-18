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


BLOCK_IDS = [
    "block-views-hien-thi-bai-viet-moi-block",  # Thong bao chung
    "block-views-tin-noi-bat-block",  # Tin noi bat
]


def get_latest_notification(block_id=BLOCK_IDS):
    print("[SCANNING]", end="  ")
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

    # for new in tbao_chung:
    #     print(new)

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
        text = "🌟 Thông báo chung 🌟\n"
    else:
        text = "🔥 Tin nổi bật 🔥 \n"
    for new in news:
        text += f"<b>{new['content']}</b>\n"
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
        last_notification = {}
    tbao_chung = latest_notification.get("tbao_chung", [])
    tin_noi_bat = latest_notification.get("tin_noi_bat", [])
    old_tbao_chung = last_notification.get("tbao_chung", [])
    old_tin_noi_bat = last_notification.get("tin_noi_bat", [])

    sent = []
    if tbao_chung != old_tbao_chung:
        news = [x for x in tbao_chung if x not in old_tbao_chung]
        message = create_message(news, type="tbao_chung")
        response, url = send_telegram_message(message)
        # print(f"Found new tbao_chung  - {datetime.now()}")
        if not response["ok"]:
            print(f"\t- Error sent ❌")
            print(f"\t- {response}")
            print(f"\t- url: {url}")
        else:
            sent.append("tbao_chung")
            # print(f"\t- Sent to telegram ✅")

    if tin_noi_bat != old_tin_noi_bat:
        news = [x for x in tin_noi_bat if x not in old_tin_noi_bat]
        message = create_message(news, type="tin_noi_bat")
        response, url = send_telegram_message(message)
        # print(f"Found new tin_noi_bat  - {datetime.now()}")
        if not response["ok"]:
            print(f"\t- Error sent ❌")
            print(f"\t- {response}")
            print(f"\t- url: {url}")
        else:
            sent.append("tin_noi_bat")
            # print(f"\t- Sent to telegram ✅")

    # for debug: check if any new noti sent
    if len(sent) == 0:
        print(f"No new notis found. - {datetime.now()}")
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": "Nothing new! ✔ ", "parse_mode": "HTML"}
        response = requests.post(url, json=payload)
        print(f"\t- sent: {response}")
    else:
        print(f"Found new {', '.join(sent)} - {datetime.now()}")
        save_last_notification(latest_notification)
        print(f"\t- Sent to telegram ✅")


if __name__ == "__main__":
    while True:
        try:
            work_flow()
        except Exception as e:
            print(f"🚨🚨🚨 Error: {e}")
            print(f"\t- Retrying in 5 minutes")
            time.sleep(300)
            continue

        next_scan_time = datetime.now() + timedelta(hours=8)
        print(f"\t- Next scan in {next_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

        time.sleep(3600 * 8)
