from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    year = State()
    model = State()
    color = State()
    docs = State()
    phone = State()
    photos = State()

@dp.message_handler(commands='start')
async def start_cmd(msg: types.Message):
    await msg.answer("سلام ✌️ مشخصات موتور رو بفرست.\nسال ساخت؟")
    await Form.year.set()

@dp.message_handler(state=Form.year)
async def get_year(msg: types.Message, state: FSMContext):
    await state.update_data(year=msg.text)
    await msg.answer("مدل؟")
    await Form.model.set()

@dp.message_handler(state=Form.model)
async def get_model(msg: types.Message, state: FSMContext):
    await state.update_data(model=msg.text)
    await msg.answer("رنگ؟")
    await Form.color.set()

@dp.message_handler(state=Form.color)
async def get_color(msg: types.Message, state: FSMContext):
    await state.update_data(color=msg.text)
    await msg.answer("مدارک؟")
    await Form.docs.set()

@dp.message_handler(state=Form.docs)
async def get_docs(msg: types.Message, state: FSMContext):
    await state.update_data(docs=msg.text)
    await msg.answer("شماره یا آیدی تماس؟")
    await Form.phone.set()

@dp.message_handler(state=Form.phone)
async def get_phone(msg: types.Message, state: FSMContext):
    await state.update_data(phone=msg.text)
    await msg.answer("عکس‌های موتور رو بفرست. وقتی تموم شد بگو: پایان")
    await state.update_data(photos=[])
    await Form.photos.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.photos)
async def get_photos(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data['photos']
    photos.append(msg.photo[-1].file_id)
    await state.update_data(photos=photos)

@dp.message_handler(lambda msg: msg.text.lower() == "پایان", state=Form.photos)
async def finish(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    text = f"""
موتور جدید 🚨

سال ساخت: {data['year']}
مدل: {data['model']}
رنگ: {data['color']}
مدارک: {data['docs']}
تماس: {data['phone']}
"""
    await bot.send_message(OWNER_ID, text)
    media = []
    for p in data['photos']:
        media.append(types.InputMediaPhoto(p))
    if media:
        await bot.send_media_group(OWNER_ID, media)
    await msg.answer("تموم شد، برای بررسی ارسال شد 😊")
    await state.finish()

executor.start_polling(dp)

