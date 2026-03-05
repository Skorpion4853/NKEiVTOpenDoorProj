import requests
import qrcode
from conf import *
from time import time
from Logger import write_error, write_info
from os import makedirs, path
import smtplib
from email.message import EmailMessage
import mimetypes

def send_photo_email(recipient_email, image_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Ваше сгенерированное фото"                                                          #Тема сообщения
        msg["From"] = sender_email                                                                            #Почта отправителя
        msg["To"] = recipient_email                                                                           #Почта получателя
        msg.set_content("Вот ваше сгенерированное фото, спасибо что выбрали нас! \nС уважением nke.team.")    #Текст сообщения

        mime_type, _ = mimetypes.guess_type(image_path)
        maintype, subtype = mime_type.split("/")

        #Открываем изображение и прикрепляем его
        with open(image_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=path.basename(image_path),
            )

        #Сама отправка
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        write_info("200 ImageDelivered", f"Image {image_path} has been sent to {recipient_email}")
        return True
    except smtplib.SMTPAuthenticationError as r:
        write_error("Authentication Error", r)
        return False
    except TimeoutError:
        write_error("Timeout Error", "Unknow error, it's may be cuz ur email incorrect, or our mail didn't work")
        return False

def check_request(image_path, CHAT_ID, response):
    if response.status_code == 200:
        write_info("200 ImageDelivered", f"Image {image_path} has been sent to {CHAT_ID}")
        return True
    elif response.status_code == 400:
        write_error("400 Bad Request", response)
        return False
    elif response.status_code == 401:
        write_error("401 Unauthorized", "Token didn't correct")
        return False
    elif response.status_code == 403:
        write_error("403 Forbidden", "bot was blocked by the user")
        return False
    elif response.status_code == 404:
        write_error("404 Not Found", "image url not found or method work bad")
        return False
    elif response.status_code == 429:
        write_error("429 Too Many Requests", "flood control")
        return False
    elif response.status_code in [500, 502, 503]:
        write_error("500 Internal Server Error", "server error")
        return False
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


def send_img_to_user(image_path, CHAT_ID=MY_USER_ID, mode=0, email=sender_email):
    """
    mode can take 3 args
    0: only qr
    1: only tg
    2: tg + or
    3: Почта
    """
    if check_internet():
        if mode != 3:
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
            if (mode == 0 or mode == 2) and corrupted:
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

                return file
        else:
            res = send_photo_email(email, image_path)
            return res
    else:
        write_error("ConnectionError", "Device haven't internet connection")
        return False