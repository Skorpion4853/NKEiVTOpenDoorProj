import requests
import qrcode
from conf import BOT_TOKEN, MY_USER_ID
from time import time
from Logger import write_error, write_info
from os import makedirs


def check_request(image_path, CHAT_ID, response):
    if response.status_code == 200:
        write_info("200 ImageDelivered", f"Image {image_path} has been sent to {CHAT_ID}")
    elif response.status_code == 400:
        write_error("400 Bad Request", response)
    elif response.status_code == 401:
        write_error("401 Unauthorized", "Token didn't correct")
    elif response.status_code == 403:
        write_error("403 Forbidden", "bot was blocked by the user")
    elif response.status_code == 404:
        write_error("404 Not Found", "image url not found or method work bad")
    elif response.status_code == 429:
        write_error("429 Too Many Requests", "flood control")
        return True
    elif response.status_code in [500, 502, 503]:
        write_error("500 Internal Server Error", "server error")
        return True
    else:
        write_error("Unknow Error", "I rly don't know what is error!")
    return False


def check_internet(host="8.8.8.8", port=53, timeout=3):
    import socket

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


def send_img_to_user(image_path, CHAT_ID = MY_USER_ID, mode = 0):
    """
    mode can take 3 args
    0: only qr
    1: only tg
    2: tg + or
    """
    if check_internet():
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        if mode != 0:
            updates = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            ).json()
            i = len(updates["result"])
            CHAT_ID = updates["result"][i-1]['message']['chat']['id']

        with open(image_path, "rb") as f:
            response = requests.post(
                url,
                data={"chat_id": CHAT_ID},
                files={"photo": f}
            )
        corrupted = check_request(image_path=image_path, CHAT_ID=CHAT_ID, response=response)
        if mode == 0 or mode == 2:
            data = response.json()
            file_id = data["result"]["photo"][-1]["file_id"]

            # получаем file_path
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
                params={"file_id": file_id}
            ).json()

            file_path = r["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

            img = qrcode.make(file_url)
            makedirs("source/qrcodes", exist_ok=True)
            file = f"source/qrcodes/qr_{int(time())}.jpg"
            img.save(file)
            write_info("QR Successfully Generated", f"QR {file[14:]} has been save to {file}")
    else:
        write_error("ConnectionError", "Device haven't internet connection")