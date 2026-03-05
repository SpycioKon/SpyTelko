import os
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH, SESSION_NAME, BASE_DOWNLOAD_PATH
from database import Database
import asyncio


class TelegramCrawler:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.db = Database()

    async def start(self):
        await self.client.start()
        print("Connected to Telegram.")

    async def crawl_group(self, group_username_or_link):
        entity = await self.client.get_entity(group_username_or_link)
        group_id = entity.id
        group_name = entity.title.replace(" ", "_")

        last_id = self.db.get_last_message_id(group_id)
        print(f"Last message id: {last_id}")

        base_path = os.path.join(BASE_DOWNLOAD_PATH, group_name)
        os.makedirs(base_path, exist_ok=True)

        max_id_seen = last_id

        async for message in self.client.iter_messages(entity, min_id=last_id, reverse=True):
            if message.id <= last_id:
                continue

            year = message.date.strftime("%Y")
            month = message.date.strftime("%m")
            day = message.date.strftime("%d")

            day_folder = os.path.join(
                base_path,
                year,
                month,
                day
            )

            os.makedirs(day_folder, exist_ok=True)
            os.makedirs(day_folder, exist_ok=True)

            message_data = {
                "message_id": message.id,
                "date": str(message.date),
                "sender_id": message.sender_id,
                "text": message.text,
                "forwarded_from": str(message.forward.sender_id) if message.forward else None
            }
          
            json_file = os.path.join(day_folder, "messages.json")
            with open(json_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(message_data, ensure_ascii=False) + "\n")

            # Download media
            if message.media:
                media_folder = self.get_media_folder(day_folder, message)
                os.makedirs(media_folder, exist_ok=True)

                try:
                    await message.download_media(file=media_folder)
                except FloodWaitError as e:
                    print(f"Rate limit hit. Sleeping {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    await message.download_media(file=media_folder)

            if message.id > max_id_seen:
                max_id_seen = message.id

        if max_id_seen > last_id:
            self.db.update_last_message_id(group_id, group_name, max_id_seen)
            print(f"Updated last_message_id to {max_id_seen}")

    def get_media_folder(self, day_folder, message):
        if message.photo:
            return os.path.join(day_folder, "images")
        elif message.video:
            return os.path.join(day_folder, "videos")
        elif message.audio:
            return os.path.join(day_folder, "audio")
        elif message.voice:
            return os.path.join(day_folder, "voice")
        elif message.document:
            return os.path.join(day_folder, "documents")
        else:
            return os.path.join(day_folder, "others")
