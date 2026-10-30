import hashlib
import hmac
from unittest.mock import patch

import bot

REPLIES = {
    "rules": [{"keywords": ["salam"], "reply": "Salam!"}],
    "default": "Standart cavab",
}

PAYLOAD = {
    "entry": [{"changes": [{"value": {"messages": [
        {"id": "wamid.1", "from": "994501234567", "type": "text", "text": {"body": "SALAM dost"}},
        {"id": "wamid.2", "from": "994501234567", "type": "image", "image": {}},
    ]}}]}]
}


def test_choose_reply_matches_keyword_case_insensitive():
    assert bot.choose_reply("Salam, necəsən?", REPLIES) == "Salam!"


def test_choose_reply_falls_back_to_default():
    assert bot.choose_reply("bilmirəm", REPLIES) == "Standart cavab"


def test_extract_only_text_messages():
    msgs = bot.extract_text_messages(PAYLOAD)
    assert msgs == [{"id": "wamid.1", "from": "994501234567", "text": "SALAM dost"}]


def test_real_replies_file_loads():
    replies = bot.load_replies()
    assert replies["default"] and replies["rules"]


def test_webhook_verification(monkeypatch):
    monkeypatch.setattr(bot, "VERIFY_TOKEN", "gizli")
    client = bot.app.test_client()
    ok = client.get("/webhook?hub.mode=subscribe&hub.verify_token=gizli&hub.challenge=123")
    assert ok.status_code == 200 and ok.data == b"123"
    bad = client.get("/webhook?hub.mode=subscribe&hub.verify_token=sehv&hub.challenge=123")
    assert bad.status_code == 403


def test_incoming_message_gets_reply_once(monkeypatch):
    monkeypatch.setattr(bot, "APP_SECRET", "")
    monkeypatch.setattr(bot, "load_replies", lambda: REPLIES)
    bot._seen_message_ids.clear()
    client = bot.app.test_client()
    with patch.object(bot, "send_text") as send:
        client.post("/webhook", json=PAYLOAD)
        client.post("/webhook", json=PAYLOAD)  # təkrar çatdırılma
    send.assert_called_once_with("994501234567", "Salam!")


def test_signature_check(monkeypatch):
    monkeypatch.setattr(bot, "APP_SECRET", "sirr")
    body = b'{"entry": []}'
    good = "sha256=" + hmac.new(b"sirr", body, hashlib.sha256).hexdigest()
    assert bot.signature_is_valid(body, good)
    assert not bot.signature_is_valid(body, "sha256=yanlis")
    assert not bot.signature_is_valid(body, None)
