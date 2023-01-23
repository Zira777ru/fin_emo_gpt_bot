import os
import openai
from aiogram import Dispatcher, Bot, types, executor
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aioschedule

from contextlib import suppress
import asyncio
import random
import string
from dotenv import load_dotenv

from modules.db import sql_start, base, cursor
from modules.expenses import exp_add, get_current_month_expenses
import markups as nav
from modules.horoscope import horoscope
from modules.chat_gpt import ask_chat_gpt

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

storage = MemoryStorage()
bot = Bot(token=os.getenv('TELEGRAM_TOKEN','default_token'))
dp = Dispatcher(bot, storage=storage)
openai.api_key = os.getenv('OPENAI_API_KEY')
ADMIN_ID = os.getenv('ADMIN_ID')

def log_message(message: types.Message, response_text):
    cursor.execute("INSERT INTO messages (text,username,user_id,response_text) VALUES (?,?,?,?)", (message.text, message.from_user.username, message.chat.id, response_text))
    base.commit()


def generate_random_password():
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    return password

# Функция удаления сообщения
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()

def is_authorized(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result and result[3] == 1:
        return True
    elif result and result[3] == 0:
        return 'denied'
    else:
        return 'not_registered'

class FSMexp(StatesGroup):
    expense = State()

class FSMemo(StatesGroup):
    emotion = State()
    desc_emo = State()

class FSMdairy(StatesGroup):
    dairy = State()

@dp.message_handler(commands=["start"])
async def register(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    access = is_authorized(user_id)
    if access == 'not_registered':
        # Send a message to the administrator with inline buttons
        keyboard = InlineKeyboardMarkup()
        add_button = InlineKeyboardButton("Add", callback_data=f"adduser_!{user_id}_!{username}")
        reject_button = InlineKeyboardButton("Reject", callback_data=f"reject_!{user_id}_!{username}")
        keyboard.add(add_button, reject_button)
        text = f"New user registered with username: {username}. Allow them to use the bot?"
        await bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=keyboard)
        await bot.send_message(chat_id=user_id, text='Your appeal has been accepted! The bot administrator will review your request.')
    elif access == 'denied':
        await message.reply("You are denied access! Goodbye!")
    else:
        await message.reply("You are already registered.", reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data.startswith("adduser_") or c.data.startswith("reject_"))
async def process_callback_add(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_!")
    user_id = data[1]
    username = data[2]
    password = generate_random_password()
    if callback_query.data.startswith("adduser"):
        cursor.execute("INSERT INTO users (user_id,username,password,authorized) VALUES (?,?,?,1)", (user_id,username,password))
        base.commit()
        await bot.send_message(chat_id=ADMIN_ID, text="User added.")
        await bot.send_message(chat_id=user_id, text=f"Congratulations!💥\nYou are added.🤝\nNow you can use the bot.\nUse the menu or write your question to the bot.\nStart the message with the words \"Bot or Бот <your question>\".\nGood luck!🤘\nYour login: {user_id}\nYour password: {password}")
        message = await bot.send_message(chat_id=user_id,text='<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)
        await bot.pin_chat_message(chat_id=user_id, message_id=message.message_id)
    else:
        cursor.execute("INSERT INTO users (user_id,username,password,authorized) VALUES (?,?,?,0)", (user_id,username,password))
        base.commit()
        await bot.send_message(chat_id=ADMIN_ID, text=f"User rejected {user_id}.")
        await bot.send_message(chat_id=user_id, text=f"You are denied access! Goodbye!")


@dp.callback_query_handler(Text(startswith="btn_"), state=None)
async def bot_call(call: types.callback_query):
    cmd = call.data.split("_")[1]
    if cmd == nav.BACK[0]:
        await call.message.answer('<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)
    if cmd == nav.MAIN[0]:
        await call.message.answer('<b>💲Expenses Menu:</b>', reply_markup=nav.expense_menu, parse_mode=types.ParseMode.HTML)
    if cmd == nav.EXP_MENU[0]: #Add Expense
        await call.message.answer('<b>⬇️Enter the payment amount and for what. For example, Beer 160:</b>', reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
        await FSMexp.expense.set()  # Вход в машину состояний
    if cmd == nav.EXP_MENU[1]: # Show Exp
        await call.message.answer('<b>📚Show Expenses</b>', reply_markup=nav.show_expense_menu, parse_mode=types.ParseMode.HTML)
    if cmd in nav.SHOW_EXP.keys():
        results = nav.SHOW_EXP[cmd](call.from_user.id)
        message = f"<b>{cmd}:</b>\n"
        for result in results:
            message += f"{result[0]} - {result[1]}\n"
        await call.message.answer(message, reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
        # await call.message.answer(f'<b>{cmd}:</b>\n{nav.SHOW_EXP[cmd](call.from_user.id)}', reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
    if cmd == nav.MAIN[2]: # Emotion
        await call.message.answer(f'<b>Choose an Emotion</b>', reply_markup=nav.emotion_menu, parse_mode=types.ParseMode.HTML)
        await FSMemo.emotion.set()
    if cmd == nav.MAIN[3]: # Zodiac Menu
        await call.message.answer(f'<b>Choose your Zodiac sign</b>', reply_markup=nav.zodiac_menu, parse_mode=types.ParseMode.HTML)
    if cmd in nav.ZODIAC_SINGS: # Zodiac Chose
        await call.message.answer(f'<b>Horoscope for {cmd}</b>\n + {horoscope(cmd)}', reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
    await call.message.delete()
    if cmd == nav.MAIN[1]: # Dairy
        await call.message.answer('<b>📝Write down your diary today:</b>', reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
        await FSMdairy.dairy.set()  # Вход в машину состояний


@dp.message_handler(state=FSMexp.expense)
async def expense_add(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['expense'] = str(message.text)
    result = await exp_add(state, message.from_user.id)
    current_month_exp = get_current_month_expenses(message.from_user.id)
    await state.finish()
    await message.answer('<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)
    msg = await message.answer(
        f'<b>👍Done! You are great!🥇</b>\n{result}\n<b>Current month expenses: {current_month_exp[0]}</b>\n<i>Message will be delete after 60 seconds.</i>',
        parse_mode=types.ParseMode.HTML)
    asyncio.create_task(delete_message(msg, 60))


# First state
@dp.callback_query_handler(Text(startswith="btn_"), state=FSMemo.emotion)
async def emo_add(call: types.callback_query, state: FSMContext):
    cmd = call.data.split("_")[1]
    if cmd in nav.EMOTIONS:
        async with state.proxy() as data:
            data['emotion'] = str(cmd)
        await FSMemo.next()
        await call.message.answer(f'<b>Why do you feel the emotion of {cmd}??</b>', reply_markup=nav.cancel_menu, parse_mode=types.ParseMode.HTML)
        await call.message.delete()
    if cmd not in nav.EMOTIONS:
        await call.message.answer("Use keyboard")
        return
    
@dp.message_handler(state=FSMemo.desc_emo)
async def desc_emo_add(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc_emo'] = message.text
        desc_emo = data['desc_emo']
        emotion = data['emotion']
    user_id = message.from_user.id
    cursor.execute("INSERT INTO emotion (user_id, emotion, desc_emo) VALUES (?,?,?)", (user_id, emotion, desc_emo))
    base.commit()
    result = f"Emotion <b>{emotion}</b> added to the database successfully"
    await state.finish()
    await message.answer('<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)
    msg = await message.answer(
        f'<b>👍Done! You are great!🥇</b>\n{result}\n<i>Message will be delete after 60 seconds.</i>',
        parse_mode=types.ParseMode.HTML)
    asyncio.create_task(delete_message(msg, 60))


@dp.message_handler(state=FSMdairy.dairy)
async def expense_add(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dairy'] = str(message.text)
        dairy = data['dairy']
    user_id = message.from_user.id
    message_id = message.message_id
    cursor.execute("INSERT INTO dairy (user_id, text, message_id) VALUES (?,?,?)", (user_id, dairy, message_id))
    base.commit()
    await state.finish()
    await message.answer('<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(startswith=["Bot", "Бот", "/"]))
async def generate_response(message: types.Message):
    user_id = message.from_user.id
    if not is_authorized(user_id) == True:
        await message.reply("You are not authorized to use this bot. Use /start .")
        return
    response = ask_chat_gpt(message.text)
    log_message(message, response)
    await message.reply(response)

async def alert_exp():
    await bot.send_message(f"🖐 Привет, напоминаю ввести расходы за сегодня!",
                           reply_markup=nav.main_menu,
                           parse_mode=types.ParseMode.HTML)

async def scheduler():
    aioschedule.every().day.at("21:00").do(alert_exp)
    # aioschedule.every().day.at("7:30").do(morning)
    # aioschedule.every().hour.do(cm_start)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())
    sql_start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
