import logging
import asyncio
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from bot.settings import (BOT_TOKEN, HEROKU_APP_NAME, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT)
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as md

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

users = {}
class start(StatesGroup):
    first_name = State()
    last_name = "None"
    username = "None"
    user_id = State()
    phone = State()
    location = State()
    lat = State()
    long = State()
    menu = State()

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]

@dp.message_handler(commands="start", state="*")
async def phone_handler(message: types.Message):
    await message.answer(text='Welcome to bot\nTo use it, you need to sign up')
    button = KeyboardButton("Sign up")
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    reply_markup.add(button)
    await message.answer(text='Click button',reply_markup=reply_markup)
    await start.first_name.set()
    
@dp.message_handler(state=start.first_name, content_types=CONTENT_TYPES)
async def first_name_step(message: types.Message, state: FSMContext):
    try:
        message.text
        if message.text != "Sign up":
            raise "Error"
    except:
        button = KeyboardButton("Sign up")
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        reply_markup.add(button)
        await message.answer("Please click button",reply_markup=reply_markup)
        return
    await state.update_data(first_name = message.from_user.first_name)
    await state.update_data(last_name = message.from_user.last_name)
    await state.update_data(username = message.from_user.username)
    await state.update_data(user_id = message.from_user.id)
    button = KeyboardButton("Share contact",request_contact=True)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    reply_markup.add(button)
    await message.answer(text='Contact: ',reply_markup=reply_markup)
    await start.phone.set()

@dp.message_handler(state=start.phone, content_types=CONTENT_TYPES)
async def location_step(message: types.Message, state: FSMContext):
    try:
        message.contact.phone_number
    except:
        button = KeyboardButton("Share contact",request_contact=True)
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        reply_markup.add(button)
        await message.answer("Please send contact",reply_markup=reply_markup)
        return
    await state.update_data(phone=str(message.contact.phone_number))
    button = KeyboardButton("Share location",request_location=True)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    reply_markup.add(button)
    await message.answer(text='Location: ',reply_markup=reply_markup)
    await start.location.set()
   
@dp.message_handler(state=start.location, content_types=CONTENT_TYPES)
async def finish_step(message: types.Message, state: FSMContext):
    try:
        message.location.latitude
    except:
        button = KeyboardButton("Share location",request_location=True)
        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
        reply_markup.add(button)
        await message.answer("Please send location",reply_markup=reply_markup)
        return
    await state.update_data(lat=message.location.latitude)
    await state.update_data(long=message.location.longitude)
    user_data = await state.get_data()
    users[message.chat.id]=user_data
    await message.answer("Signed up")
    button = KeyboardButton("Firstname")
    button1 = KeyboardButton("Lastname")
    button2 = KeyboardButton("Username")
    button3 = KeyboardButton("ID")
    button4 = KeyboardButton("Location")
    button5 = KeyboardButton("Phone")
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(button, button1)
    reply_markup.add(button2, button3)
    reply_markup.add(button4, button5)
    await message.answer("Menu",reply_markup=reply_markup)
    await start.menu.set()
    
@dp.message_handler(state=start.menu, content_types={"text"})
async def menu_step(message: types.Message, state: FSMContext):
    user_data = users[message.chat.id]
    try:
        if message.text == "Firstname":
            await message.answer(user_data['first_name'])
        elif message.text == "Lastname":
            await message.answer(user_data['last_name'])
        elif message.text == "Username":
            await message.answer(user_data['username'])
        elif message.text == "Phone":
            await message.answer(user_data['phone'])
        elif message.text == "ID":
            await message.answer(user_data['user_id'])
        elif message.text == "Location":
            await bot.send_location(message.chat.id, latitude=user_data["lat"], longitude=user_data["long"])
    except:
        await message.answer("None")


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
