import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from modules.db import base, cursor
from main import dp, delete_message, FSMemo
import markups as nav




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
    result = f"Emotion {emotion} added to the database successfully"
    await state.finish()
    await message.answer('<b>📚Menu:</b>', reply_markup=nav.main_menu, parse_mode=types.ParseMode.HTML)
    msg = await message.answer(
        f'<b>👍Done! You are great!🥇</b>\n{result}\n<i>Message will be delete after 60 seconds.</i>',
        parse_mode=types.ParseMode.HTML)
    asyncio.create_task(delete_message(msg, 60))