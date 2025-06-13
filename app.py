from telethon import TelegramClient, events
import os
import asyncio

# Read from environment or hardcode here (not recommended)
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = "session"

# Source and target
SOURCE_CHANNELS = [
    'https://t.me/c/123456789/0',
    'https://t.me/c/987654321/0'
]

TARGET_CHANNEL = 'https://t.me/your_target_channel'

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
