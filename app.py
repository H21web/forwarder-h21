import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import ChannelInvalidError, UsernameNotOccupiedError

# Load config from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SOURCE_CHANNELS_RAW = os.getenv("SOURCE_CHANNELS", "")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")  # can be username or ID

# Parse source channels (comma-separated)
SOURCE_CHANNELS = [ch.strip() for ch in SOURCE_CHANNELS_RAW.split(',') if ch.strip()]

# Global variables
valid_source_ids = set()
target_channel_entity = None

# Telethon client using session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def resolve_entity_safe(identifier):
    """Resolve a channel or user safely"""
    try:
        return await client.get_entity(identifier)
    except (ChannelInvalidError, UsernameNotOccupiedError, ValueError) as e:
        print(f"[WARNING] Cannot resolve '{identifier}': {e}")
        return None

@client.on(events.NewMessage())
async def forward_handler(event):
    if event.chat_id not in valid_source_ids:
        return
    try:
        await client.send_message(target_channel_entity, event.message)
        print(f"✅ Forwarded message from: {event.chat.title}")
    except Exception as e:
        print(f"[ERROR] Failed to forward: {e}")

async def main():
    global target_channel_entity, valid_source_ids

    await client.start()
    print("🔐 Client started with session.")

    # Try resolving target channel
    target_channel_entity = await resolve_entity_safe(TARGET_CHANNEL)
    if not target_channel_entity:
        print("❌ ERROR: Target channel not found. Ensure you are the owner or a member.")
        return

    print(f"✅ Found target channel: {getattr(target_channel_entity, 'title', str(TARGET_CHANNEL))}")

    # Resolve source channels
    for ch in SOURCE_CHANNELS:
        entity = await resolve_entity_safe(ch)
        if entity:
            valid_source_ids.add(entity.id)
            print(f"✅ Listening to source: {entity.title} ({entity.id})")
        else:
            print(f"⚠️ Skipping source: {ch}")

    if not valid_source_ids:
        print("❌ No valid source channels found. Exiting.")
        return

    print("🚀 Bot is running. Waiting for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
