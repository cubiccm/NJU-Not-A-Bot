import requests
import os

bot_token = os.environ.get("_TG_BOT_TOKEN")
chat_id = os.environ.get("_TG_CHAT_ID")

def send(mes):
  if not bot_token or not chat_id:
    return
  url = "https://api.telegram.org/bot" + bot_token + "/"
  params = {
    "chat_id": chat_id,
    "text": mes,
    "parse_mode": "HTML",
    "disable_notification": "true"
  }
  requests.get(url + "sendMessage", params)