import os
import asyncio
import threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from fastapi import FastAPI
import uvicorn

# ENV Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNELS = [c.strip() for c in os.getenv("SOURCE_CHANNELS", "").split(",") if c.strip()]
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

# Clients
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient("bot", API_ID, API_HASH)

# State
valid_source_ids = set()
target_channel_entity = None

# Web server for Koyeb health check
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "running"}

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8080)

@user_client.on(events.NewMessage())
async def forward_handler(event):
    if event.chat_id not in valid_source_ids:
        return
    try:
        await bot_client.send_message(target_channel_entity, event.message)
        print(f"✅ Forwarded message from {event.chat_id}")
    except Exception as e:
        print(f"[ERROR] Failed to forward: {e}")

async def startup():
    global target_channel_entity, valid_source_ids

    print("🔐 Connecting clients...")
    await user_client.connect()
    await bot_client.start(bot_token=BOT_TOKEN)

    # Get target channel
    try:
        target_channel_entity = await bot_client.get_entity(TARGET_CHANNEL)
        print(f"🎯 Target channel: {getattr(target_channel_entity, 'title', TARGET_CHANNEL)}")
    except Exception as e:
        print(f"[WARNING] Could not resolve target: {e}")
        return

    # Get source channels
    for ch in SOURCE_CHANNELS:
        try:
            entity = await user_client.get_entity(int(ch))
            valid_source_ids.add(entity.id)
            print(f"📡 Listening to: {getattr(entity, 'title', ch)}")
        except Exception as e:
            print(f"[WARNING] Could not resolve source {ch}: {e}")

    if not valid_source_ids:
        print("❌ No valid source channels found. Exiting.")
        return

    print("🚀 Bot is now running...")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
