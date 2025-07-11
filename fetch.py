from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from datetime import datetime
import asyncio

def fetch_all_messages(config):
    api_id = config["api_id"]
    api_hash = config["api_hash"]
    session_name = config["session_name"]
    channel_ids = config["channel_ids"]

    collected = []

    async def fetch():
        async with TelegramClient(session_name, api_id, api_hash) as client:
            for username in channel_ids:
                try:
                    entity = await client.get_entity(username)
                    async for msg in client.iter_messages(entity, limit=100):
                        if msg.text:
                            collected.append({
                                "channel": username,
                                "text": msg.text,
                                "date": msg.date
                            })
                except Exception as e:
                    print(f"خطا در دریافت پیام از {username}: {e}")

    asyncio.run(fetch())
    return collected
