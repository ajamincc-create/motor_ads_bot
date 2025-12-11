import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Text
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    year = State()
    vehicle_id = State()
    model = State()
    additional_info = State()

# استارت و کیبورد اصلی
@dp.message(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="شروع ثبت اطلاعات")],
        ],
        resize_keyboard=True
    )
    await message.answer("سلام! برای شروع ثبت اطلاعات روی دکمه زیر بزن.", reply_markup=kb)

# پاسخ به دکمه شروع
@dp.message(Text(text="شروع ثبت اطلاعات"))
async def start_form(message: types.Message, state: FSMContext):
    await Form.year.set()
    await message.answer("لطفاً سال ساخت را وارد کنید:", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await Form.next()
    await message.answer("آیدی وسیله نقلیه را وارد کنید:")

@dp.message(Form.vehicle_id)
async def process_vehicle_id(message: types.Message, state: FSMContext):
    await state.update_data(vehicle_id=message.text)
    await Form.next()
    await message.answer("مدل وسیله نقلیه را وارد کنید:")

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await Form.next()
    await message.answer("در صورت داشتن توضیحات اضافه وارد کنید یا /skip بزنید:")

@dp.message(Form.additional_info)
async def process_additional_info(message: types.Message, state: FSMContext):
    await state.update_data(additional_info=message.text)
    data = await state.get_data()
    text = (
        f"اطلاعات ثبت شده:\n"
        f"سال ساخت: {data['year']}\n"
        f"آیدی: {data['vehicle_id']}\n"
        f"مدل: {data['model']}\n"
        f"توضیحات: {data.get('additional_info', '-')}"
    )
    await bot.send_message(OWNER_CHAT_ID, text)
    await message.answer("اطلاعات شما ثبت شد ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(commands=["skip"])
async def skip_additional_info(message: types.Message, state: FSMContext):
    await state.update_data(additional_info="-")
    data = await state.get_data()
    text = (
        f"اطلاعات ثبت شده:\n"
        f"سال ساخت: {data['year']}\n"
        f"آیدی: {data['vehicle_id']}\n"
        f"مدل: {data['model']}\n"
        f"توضیحات: -"
    )
    await bot.send_message(OWNER_CHAT_ID, text)
    await message.answer("اطلاعات شما ثبت شد ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
