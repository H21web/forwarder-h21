from telethon import TelegramClient, events
import os
import asyncio

# Load API credentials from environment
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = "session"

# Load and parse source channels (comma-separated)
raw_channels = os.getenv('SOURCE_CHANNELS', '')
SOURCE_CHANNELS = [c.strip() for c in raw_channels.split(',') if c.strip()]

# Load target channel
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')

# Initialize the client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_handler(event):
    await client.send_message(TARGET_CHANNEL, event.message)

async def main():
    print("Starting Telethon client...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
