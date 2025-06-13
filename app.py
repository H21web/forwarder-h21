from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import asyncio

# Load all from environment
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

SOURCE_CHANNELS = [c.strip() for c in os.getenv('SOURCE_CHANNELS', '').split(',') if c.strip()]
TARGET_CHANNEL_REF = os.getenv('TARGET_CHANNEL')

# Use StringSession instead of file-based session
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_handler(event):
    try:
        await client.send_message(target_channel_entity, event.message)
    except Exception as e:
        print(f"Error forwarding message: {e}")

async def main():
    global target_channel_entity
    await client.start()

    # Resolve the target channel entity (private/public)
    try:
        target_channel_entity = await client.get_entity(TARGET_CHANNEL_REF)
        print(f"Forwarding to: {target_channel_entity.title}")
    except Exception as e:
        print(f"Error resolving target channel: {e}")
        return

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
