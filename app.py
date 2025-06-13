import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import ChannelInvalidError

# Load from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNELS = [c.strip() for c in os.getenv("SOURCE_CHANNELS", "").split(",") if c.strip()]
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

# Clients
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient("bot", API_ID, API_HASH)

valid_source_ids = set()
target_channel_entity = None

async def resolve_entity_safe(client, identifier):
    try:
        return await client.get_entity(identifier)
    except Exception as e:
        print(f"[WARNING] Cannot resolve '{identifier}': {e}")
        return None

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

    print("🔐 Starting both clients...")
    await user_client.connect()
    await bot_client.start(bot_token=BOT_TOKEN)

    if not await user_client.is_user_authorized():
        print("❌ User session is not authorized.")
        return

    # Resolve target channel with bot (bot must be member)
    target_channel_entity = await resolve_entity_safe(bot_client, TARGET_CHANNEL)
    if not target_channel_entity:
        print("❌ Bot can't access target channel. Is it added and admin?")
        return

    print(f"✅ Target channel found: {getattr(target_channel_entity, 'title', TARGET_CHANNEL)}")

    # Resolve source channels with user
    for ch in SOURCE_CHANNELS:
        entity = await resolve_entity_safe(user_client, ch)
        if entity:
            valid_source_ids.add(entity.id)
            print(f"✅ Listening to source: {entity.title} ({entity.id})")
        else:
            print(f"⚠️ Skipped: {ch}")

    if not valid_source_ids:
        print("❌ No valid source channels found. Exiting.")
        return

    print("🚀 Ready and listening...")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
