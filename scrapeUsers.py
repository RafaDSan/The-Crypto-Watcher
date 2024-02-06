import configparser
import json
import asyncio

from telethon.tl.functions.users import GetFullUserRequest
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
    PeerChannel
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

# Define the gather_with_concurrency function
async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = input("enter entity(telegram URL or entity id):")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

   # Fetch all participants
    offset = 0
    limit = 100
    all_participants = []
    count = 0

    while True:
        participants = await client(GetParticipantsRequest(my_channel, 
    ChannelParticipantsSearch(''), offset, limit,hash=0))
        if not participants.users or offset >= 1000:
            break
        all_participants.extend(participants.users)
        count +=1
        offset += len(participants.users)
        print(f'Fetched {offset} users')
    print("Finisehd fetching users!")

    # Process the participants as needed
    all_user_details = []
    tasks = []
    for participant in all_participants:
        tasks.append(client(GetFullUserRequest(participant.id)))  # No need for asyncio.create_task
        print(f"Fetching users details: #{count}")  # Add this line to print the user being fetched
        count += 1
    print("Finisehd fetching user details!")

    # Limit the concurrency using gather_with_concurrency
    MAX_CONCURRENT_REQUESTS = 10
    results = await gather_with_concurrency(MAX_CONCURRENT_REQUESTS, *tasks)
    all_user_details = [{"username": participant.username, "name": f"{participant.first_name} {participant.last_name}", "bio": user_full.full_user.about, "foto_de_perfil": user_full.full_user.profile_photo} for participant, user_full in zip(all_participants, results)]
    
    with open('user_data.json', 'w') as outfile:
        json.dump(all_user_details, outfile)

asyncio.run(main(phone))


