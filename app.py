import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNELS = [c.strip() for c in os.getenv("SOURCE_CHANNELS", "").split(",") if c.strip()]
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient("bot", API_ID, API_HASH)

valid_source_ids = set()
target_channel_entity = None

@user_client.on(events.NewMessage())
async def handler(event):
    if event.chat_id not in valid_source_ids:
        return
    try:
        await bot_client.send_message(target_channel_entity, event.message)
        print(f"✅ Forwarded from: {event.chat.title}")
    except Exception as e:
        print(f"[ERROR] Could not forward: {e}")

async def startup():
    global target_channel_entity, valid_source_ids

    print("🔐 Starting clients...")
    await user_client.connect()
    await bot_client.start(bot_token=BOT_TOKEN)

    # Resolve target channel (must be int)
    try:
        target_channel_entity = await bot_client.get_entity(TARGET_CHANNEL)
        print(f"✅ Target channel resolved: {getattr(target_channel_entity, 'title', 'unnamed')}")
    except Exception as e:
        print(f"[WARNING] Could not resolve TARGET_CHANNEL: {e}")
        return

    # Resolve source channels
    for ch in SOURCE_CHANNELS:
        try:
            entity = await user_client.get_entity(int(ch))
            valid_source_ids.add(entity.id)
            print(f"✅ Listening to source: {entity.title}")
        except Exception as e:
            print(f"[WARNING] Could not resolve source {ch}: {e}")

    if not valid_source_ids:
        print("❌ No valid source channels.")
        return

    print("🚀 Listening...")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
