import sys

import config_controller
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from services.forChat.BuilderState import BuilderState
from services.forChat.UserState import UserState
from services.forChat.Response import Response
import os
import services.testing.Logger as log



#tokkey = '6338019607:AAGprZFmi9nT7GZqIWnbRQly8vs1A2jquqU'


#tokkey = '6729587033:AAESDJSwGSgA8zxfLLEW1sOvg6HPF68LzB4'

tokkey = os.environ.get('BOT_TOKEN')

bot = AsyncTeleBot(tokkey)

state_list = {}

@bot.message_handler(commands=['off'])
async def off(message):
    await bot.send_message(chat_id=message.chat.id, text="Вимикаю...")
    sys.exit()

@bot.message_handler(commands=['clear_post'])
async def off(message):
    config_controller.LIST_POSTS = {}
    config_controller.write_ini()
    await bot.send_message(chat_id=message.chat.id, text="Стираю...")

@bot.message_handler(commands=['get_log'])
async def off(message):
    with open(log.get_log(), 'rb') as file:
        await bot.send_document(chat_id=message.chat.id, document=file)

@bot.message_handler(commands=['passwordadmin','help', 'passwordmoder', 'helpadmin', 'log', 'textafter', 'start', 'texthelp', 'texthello', 'textcontact','menu'])
async def passwordadmin(message):
    await handle_message(message)

@bot.callback_query_handler(func= lambda call: True)
async def callback(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    chat_id = str(call.message.chat.id)
    try:
        user_name = str(call.from_user.username)
    except:
        user_name = None
    text = call.data
    id_list = user_id+chat_id
    if state_list.get(id_list, None) != None:
        state: UserState = state_list[id_list]
        res: Response = await state.next_btn_clk(text)
        await chek_response(chat_id, user_id, id_list, res, user_name)
    else:
        builder = BuilderState(bot)
        if not text.startswith("/geturl"):
            state = builder.create_state(text, user_id, chat_id, bot, user_name)
        else:
            state = builder.create_state("/geturl", user_id, chat_id, bot, user_name)
        state_list[id_list] = state
        if not text.startswith("/geturl"):
            res: Response = await state.start_msg()
            await chek_response(chat_id, user_id, id_list, res, user_name)
        else:
            res: Response = await state.next_btn_clk_message(text, call.message)
            await chek_response(chat_id, user_id, id_list, res, user_name)
    if not text.startswith("/geturl"):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

@bot.message_handler(func=lambda message: True, content_types=['text'])
async def comand(message: types.Message):
    await handle_message(message)

@bot.message_handler(func=lambda message: True, content_types=["photo", "video"])
async def comand(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id + user_chat_id
    if state_list.get(id_list, None) == None:
        return
    else:
        state: UserState = state_list[id_list]
        res: Response = await state.next_msg_photo_and_video(message)
        await chek_response(user_chat_id, user_id, id_list, res, user_name)


@bot.message_handler(func=lambda message: True, content_types=["document"])
async def comand(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id + user_chat_id
    if state_list.get(id_list, None) == None:
        return
    else:
        state: UserState = state_list[id_list]
        res: Response = await state.next_msg_document(message)
        await chek_response(user_chat_id, user_id, id_list, res, user_name)

async def chek_response(user_chat_id, user_id, id_list, res: Response = None, user_name: str = None):
    if res != None:
        await res.send(user_chat_id, bot)
        if res.is_end:
            state_list.pop(id_list)
        if res.redirect != None:
            builder = BuilderState(bot)
            state = builder.create_state(res.redirect, user_id, user_chat_id, bot, user_name)
            state_list[id_list] = state
            res: Response = await state.start_msg()
            await chek_response(user_chat_id, user_id, id_list, res, user_name)
    else:
        state_list.pop(id_list)
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id+user_chat_id
    text = message.text
    if state_list.get(id_list, None) == None:
        builder = BuilderState(bot)
        state = builder.create_state(text, user_id, user_chat_id, bot, user_name)
        state_list[id_list] = state
        res: Response = await state.start_msg()
        await chek_response(user_chat_id, user_id, id_list, res, user_name)
    else:
        state: UserState = state_list[id_list]
        res: Response = await state.next_msg(text)
        await chek_response(user_chat_id, user_id, id_list, res, user_name)

config_controller.preload_config()

import asyncio
asyncio.run(bot.polling(non_stop=True))






