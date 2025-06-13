import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerChannel
from telethon.errors import ChannelInvalidError
from telethon.tl.functions.messages import ForwardMessagesRequest

# Load from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNELS = [c.strip() for c in os.getenv("SOURCE_CHANNELS", "").split(",") if c.strip()]
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

# Clients
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

valid_source_ids = set()
target_channel_entity = None

async def resolve_entity_safe(client, identifier):
    try:
        entity = await client.get_entity(identifier)
        return entity
    except Exception as e:
        print(f"[WARNING] Cannot resolve '{identifier}': {e}")
        return None

@user_client.on(events.NewMessage())
async def handler(event):
    if event.chat_id not in valid_source_ids:
        return
    try:
        # Forward via user to bot
        await bot_client.send_message(target_channel_entity, event.message)
        print(f"✅ Forwarded to target from: {event.chat.title}")
    except Exception as e:
        print(f"[ERROR] Forwarding failed: {e}")

async def main():
    global target_channel_entity, valid_source_ids

    await user_client.start()
    await bot_client.start()
    print("🔐 Clients started.")

    # Resolve target via bot (since bot sends the message)
    target_channel_entity = await resolve_entity_safe(bot_client, TARGET_CHANNEL)
    if not target_channel_entity:
        print("❌ ERROR: Bot could not access target channel. Is it added as admin?")
        return

    # Resolve source channels via user
    for ch in SOURCE_CHANNELS:
        entity = await resolve_entity_safe(user_client, ch)
        if entity:
            valid_source_ids.add(entity.id)
            print(f"✅ Listening to source: {entity.title} ({entity.id})")
        else:
            print(f"⚠️ Skipping source: {ch}")

    if not valid_source_ids:
        print("❌ No valid source channels. Exiting.")
        return

    print("🚀 Bot is running. Waiting for new messages...")
    await user_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
