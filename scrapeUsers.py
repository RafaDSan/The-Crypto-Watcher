from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
import json
from dotenv import load_dotenv 
import os 


load_dotenv()  

CONFIG = {  
"telegram_api_id": int(os.getenv("TG_API_ID")),  
"telegram_hash": os.getenv("TG_API_HASH"),  
"telegram_session": os.getenv("TG_SESSION_NAME"),
}  

client = TelegramClient(CONFIG["telegram_session"],CONFIG["telegram_api_id"],CONFIG["telegram_hash"])

chat_id = -1001650766110

async def main():
 
 await client.start()
 
 users = []

 async for user in client.iter_participants(chat_id, limit=1000):
  
  user_full = await client(GetFullUserRequest(user.username))
  
  if user_full.full_user.about is not None:
    bio_links = user_full.full_user.about.split(',')
    bio = [{"link": link.strip()} for link in bio_links]
  
  user_data = {
      "username": user.username,
      "name": user.first_name + " " + user.last_name if user.last_name else user.first_name,
      "bio": bio
  }
  
 users.append(user_data)
 
 with open('users.json', 'w') as f:
  json.dump(users, f)

with client:
 client.loop.run_until_complete(main())