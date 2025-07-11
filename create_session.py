from telethon.sync import TelegramClient

api_id = 23271411
api_hash = "bad26363f0418cc541dbca6db599242f"

with TelegramClient("session", api_id, api_hash) as client:
    print("✔️ Login successful. Session saved.")
