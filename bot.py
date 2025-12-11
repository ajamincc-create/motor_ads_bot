import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InputFile
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv
import os

# بارگذاری توکن و آیدی ادمین
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# تعریف States برای فرم مرحله‌ای
class AdForm(StatesGroup):
    photo = State()
    model = State()
    year = State()
    color = State()
    price = State()
    location = State()
    contact = State()

# استارت ربات
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("سلام! برای ایجاد آگهی موتور، دستور /newad را بفرست.")

# شروع فرم آگهی
@dp.message_handler(commands=['newad'])
async def new_ad(message: types.Message):
    await AdForm.photo.set()
    await message.answer("لطفاً عکس موتور را ارسال کنید:")

# دریافت عکس
@dp.message_handler(content_types=['photo'], state=AdForm.photo)
async def get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await AdForm.next()
    await message.answer("مدل موتور را وارد کنید:")

# دریافت مدل
@dp.message_handler(state=AdForm.model)
async def get_model(message: types.Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("مدل نمی‌تواند خالی باشد. لطفاً دوباره وارد کنید:")
        return
    await state.update_data(model=message.text.strip())
    await AdForm.next()
    await message.answer("سال ساخت موتور را وارد کنید:")

# دریافت سال
@dp.message_handler(state=AdForm.year)
async def get_year(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("سال باید عدد باشد. دوباره وارد کنید:")
        return
    await state.update_data(year=message.text)
    await AdForm.next()
    await message.answer("رنگ موتور را وارد کنید:")

# دریافت رنگ
@dp.message_handler(state=AdForm.color)
async def get_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text.strip())
    await AdForm.next()
    await message.answer("قیمت موتور را وارد کنید:")

# دریافت قیمت
@dp.message_handler(state=AdForm.price)
async def get_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text.strip())
    await AdForm.next()
    await message.answer("محل فروش را وارد کنید:")

# دریافت محل فروش
@dp.message_handler(state=AdForm.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    await AdForm.next()
    await message.answer("شماره تماس یا آیدی تلگرام را وارد کنید:")

# دریافت تماس و ارسال نهایی
@dp.message_handler(state=AdForm.contact)
async def get_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    data = await state.get_data()
    # ساخت متن آگهی
    caption = f"""
📌 آگهی موتور
مدل: {data['model']}
سال ساخت: {data['year']}
رنگ: {data['color']}
قیمت: {data['price']}
محل فروش: {data['location']}
تماس: {data['contact']}
"""
    # ارسال آگهی به ادمین
    await bot.send_photo(chat_id=OWNER_CHAT_ID, photo=data['photo'], caption=caption)
    await message.answer("آگهی شما با موفقیت ثبت شد ✅")
    await state.finish()

# هر پیام دیگر
@dp.message_handler()
async def unknown_message(message: types.Message):
    await message.answer("لطفاً از دستور /newad برای ثبت آگهی استفاده کنید.")

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()
    executor.start_polling(dp, skip_updates=True)