import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN در متغیرهای محیطی یافت نشد!")
    raise ValueError("توکن ربات تنظیم نشده است.")

if OWNER_CHAT_ID:
    OWNER_CHAT_ID = int(OWNER_CHAT_ID)
else:
    logger.warning("⚠️ OWNER_CHAT_ID تنظیم نشده. اطلاعات به مالک ارسال نمی‌شود.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    year = State()
    vehicle_id = State()
    model = State()
    additional_info = State()

# استارت و کیبورد اصلی
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="شروع ثبت اطلاعات")],
        ],
        resize_keyboard=True
    )
    await message.answer("سلام! برای شروع ثبت اطلاعات روی دکمه زیر بزن.", reply_markup=kb)

# پاسخ به دکمه شروع - CORRECTED LINE
@dp.message(F.text == "شروع ثبت اطلاعات")
async def start_form(message: types.Message, state: FSMContext):
    # FIX: استفاده از set_state به جای set
    await state.set_state(Form.year)
    await message.answer("لطفاً سال ساخت را وارد کنید:", reply_markup=ReplyKeyboardRemove())

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    # FIX: استفاده از set_state به جای next
    await state.set_state(Form.vehicle_id)
    await message.answer("آیدی وسیله نقلیه را وارد کنید:")

@dp.message(Form.vehicle_id)
async def process_vehicle_id(message: types.Message, state: FSMContext):
    await state.update_data(vehicle_id=message.text)
    # FIX: استفاده از set_state به جای next
    await state.set_state(Form.model)
    await message.answer("مدل وسیله نقلیه را وارد کنید:")

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    # FIX: استفاده از set_state به جای next
    await state.set_state(Form.additional_info)
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
    
    if OWNER_CHAT_ID:
        try:
            await bot.send_message(OWNER_CHAT_ID, text)
            logger.info(f"✅ اطلاعات به مالک (ID: {OWNER_CHAT_ID}) ارسال شد.")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال به مالک: {e}")
    else:
        logger.info("ℹ️ OWNER_CHAT_ID تنظیم نشده. اطلاعات در لاگ ثبت شد:")
        logger.info(text)
    
    await message.answer("اطلاعات شما ثبت شد ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(Command("skip"))
async def skip_additional_info(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state != Form.additional_info:
        await message.answer("شما در مرحله‌ای نیستید که بتوانید این دستور را استفاده کنید.")
        return
    
    await state.update_data(additional_info="-")
    data = await state.get_data()
    text = (
        f"اطلاعات ثبت شده:\n"
        f"سال ساخت: {data['year']}\n"
        f"آیدی: {data['vehicle_id']}\n"
        f"مدل: {data['model']}\n"
        f"توضیحات: -"
    )
    
    if OWNER_CHAT_ID:
        try:
            await bot.send_message(OWNER_CHAT_ID, text)
            logger.info(f"✅ اطلاعات به مالک (ID: {OWNER_CHAT_ID}) ارسال شد.")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال به مالک: {e}")
    else:
        logger.info("ℹ️ OWNER_CHAT_ID تنظیم نشده. اطلاعات در لاگ ثبت شد:")
        logger.info(text)
    
    await message.answer("اطلاعات شما ثبت شد ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()

async def main():
    logger.info("🚀 ربات در حال شروع...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ خطای بحرانی: {e}")
    finally:
        await bot.session.close()
        logger.info("👋 ربات متوقف شد.")

if __name__ == "__main__":
    asyncio.run(main())
