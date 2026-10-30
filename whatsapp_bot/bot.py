"""WhatsApp avtomatik cavab botu (WhatsApp Business Cloud API).

İşə salmaq:
    pip install -r requirements.txt
    cp .env.example .env   # və dəyərləri doldurun
    python bot.py
"""

import hashlib
import hmac
import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, abort, request

load_dotenv()

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
APP_SECRET = os.getenv("APP_SECRET", "")  # boşdursa imza yoxlanmır
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v23.0")
REPLIES_FILE = Path(os.getenv("REPLIES_FILE", Path(__file__).with_name("replies.json")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("whatsapp_bot")

app = Flask(__name__)

# WhatsApp eyni mesajı bəzən iki dəfə göndərir; artıq cavab verdiklərimizi yadda saxlayırıq.
_seen_message_ids: set[str] = set()


def load_replies(path: Path = REPLIES_FILE) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def choose_reply(text: str, replies: dict) -> str:
    """Mesajda açar söz varsa ona uyğun cavabı, yoxdursa standart cavabı qaytarır."""
    lowered = text.lower()
    for rule in replies.get("rules", []):
        if any(keyword.lower() in lowered for keyword in rule["keywords"]):
            return rule["reply"]
    return replies["default"]


def signature_is_valid(body: bytes, header: str | None) -> bool:
    """Sorğunun həqiqətən Meta-dan gəldiyini yoxlayır (X-Hub-Signature-256)."""
    if not APP_SECRET:
        return True
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def send_text(to: str, body: str) -> None:
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    resp = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        timeout=10,
    )
    if resp.ok:
        log.info("Cavab göndərildi -> %s", to)
    else:
        log.error("Göndərmə xətası %s: %s", resp.status_code, resp.text)


def extract_text_messages(data: dict) -> list[dict]:
    """Webhook məlumatından yalnız mətn mesajlarını çıxarır."""
    messages = []
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                if msg.get("type") == "text":
                    messages.append(
                        {"id": msg["id"], "from": msg["from"], "text": msg["text"]["body"]}
                    )
    return messages


@app.get("/webhook")
def verify_webhook():
    """Meta webhook-u qoşarkən bu ünvanı bir dəfə yoxlayır."""
    if (
        request.args.get("hub.mode") == "subscribe"
        and request.args.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return request.args.get("hub.challenge", ""), 200
    abort(403)


@app.post("/webhook")
def receive_message():
    if not signature_is_valid(request.get_data(), request.headers.get("X-Hub-Signature-256")):
        abort(403)

    replies = load_replies()  # faylı dəyişəndə botu yenidən başlatmaq lazım deyil
    for msg in extract_text_messages(request.get_json(silent=True) or {}):
        if msg["id"] in _seen_message_ids:
            continue
        _seen_message_ids.add(msg["id"])
        log.info("Mesaj %s: %s", msg["from"], msg["text"])
        send_text(msg["from"], choose_reply(msg["text"], replies))

    # Meta-ya tez "200 OK" qaytarmaq vacibdir, yoxsa mesajı təkrar göndərir.
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
