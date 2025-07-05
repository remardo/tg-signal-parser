import os
import re
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import requests

api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
channel_username = os.getenv('TG_CHANNEL')
webhook_url = os.getenv('WEBHOOK_URL')

client = TelegramClient('session', api_id, api_hash)

signal_pattern = re.compile(
    r"(?P<symbol>[A-Z]{3,10})\s*(long|short)?[\s\S]*?entry[:\-]?\s*(?P<entry>\d+(\.\d+)?)[\s\S]*?sl[:\-]?\s*(?P<sl>\d+(\.\d+)?)([\s\S]*?tp\d*[:\-]?\s*(?P<tp1>\d+(\.\d+)?))?([\s\S]*?tp\d*[:\-]?\s*(?P<tp2>\d+(\.\d+)?))?([\s\S]*?tp\d*[:\-]?\s*(?P<tp3>\d+(\.\d+)?))?",
    re.IGNORECASE
)

async def main():
    await client.start()
    print(f"Connected to channel: {channel_username}")
    channel = await client.get_entity(channel_username)

    async for message in client.iter_messages(channel, limit=20):
        if message.text:
            match = signal_pattern.search(message.text)
            if match:
                groups = match.groupdict()
                data = {
                    "symbol": groups.get("symbol", "") + "USDT",
                    "entry": float(groups["entry"]),
                    "sl": float(groups["sl"]),
                    "tp1": float(groups["tp1"] or 0),
                    "tp2": float(groups["tp2"] or 0),
                    "tp3": float(groups["tp3"] or 0),
                    "text": message.text,
                    "timestamp": message.date.isoformat()
                }
                print("Parsed Signal:", data)
                try:
                    r = requests.post(webhook_url, json=data, timeout=5)
                    print("Sent to webhook:", r.status_code)
                except Exception as e:
                    print("Failed to send:", e)

with client:
    client.loop.run_until_complete(main())