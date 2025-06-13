import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import ChannelInvalidError, ChatAdminRequiredError

# Load from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SOURCE_CHANNELS_RAW = os.getenv("SOURCE_CHANNELS", "")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")

# Parse channels from env (expecting -100xxx or usernames)
SOURCE_CHANNELS = [c.strip() for c in SOURCE_CHANNELS_RAW.split(',') if c.strip()]

# Init Telethon client with session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def resolve_channel(client, identifier: str):
    try:
        entity = await client.get_entity(identifier)
        return entity
    except Exception as e:
        print(f"[WARNING] Could not resolve {identifier}: {e}")
        return None

@client.on(events.NewMessage())
async def handler(event):
    # Only forward if from valid source
    if event.chat_id not in valid_source_ids:
        return
    try:
        await client.send_message(target_channel_entity, event.message)
        print(f"✅ Forwarded from {event.chat.title}")
    except Exception as e:
        print(f"[ERROR] Could not forward message: {e}")

async def main():
    global target_channel_entity, valid_source_ids
    await client.start()
    print("🔐 Client started.")

    # Step 1: Resolve and validate target channel
    target_channel_entity = await resolve_channel(client, TARGET_CHANNEL)
    if not target_channel_entity:
        print("❌ Target channel not accessible. Exiting.")
        return

    # Step 2: Resolve & filter source channels
    valid_source_ids = set()
    for ch in SOURCE_CHANNELS:
        entity = await resolve_channel(client, ch)
        if entity:
            valid_source_ids.add(entity.id)
            print(f"✅ Listening to source: {entity.title} ({entity.id})")
        else:
            print(f"⚠️ Skipping inaccessible source: {ch}")

    if not valid_source_ids:
        print("❌ No valid source channels. Exiting.")
        return

    print("🚀 Bot running. Waiting for new messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
