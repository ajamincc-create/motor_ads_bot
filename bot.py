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
    OWNER_CHAT_ID = None
    logger.warning("⚠️ OWNER_CHAT_ID تنظیم نشده. اطلاعات فقط به کاربر نمایش داده می‌شود.")

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

# پاسخ به دکمه شروع
@dp.message(F.text == "شروع ثبت اطلاعات")
async def start_form(message: types.Message, state: FSMContext):
    await state.set_state(Form.year)
    await message.answer("🔸 **مرحله ۱ از ۴**\nلطفاً سال ساخت را وارد کنید:", 
                         reply_markup=ReplyKeyboardRemove())

@dp.message(Form.year)
async def process_year(message: types.Message, state: FSMContext):
    year = message.text
    await state.update_data(year=year)
    await state.set_state(Form.vehicle_id)
    
    # نمایش فوری اطلاعات وارد شده
    await message.answer(f"✅ سال ساخت ثبت شد: **{year}**")
    await message.answer("🔸 **مرحله ۲ از ۴**\nآیدی وسیله نقلیه را وارد کنید:")

@dp.message(Form.vehicle_id)
async def process_vehicle_id(message: types.Message, state: FSMContext):
    vehicle_id = message.text
    await state.update_data(vehicle_id=vehicle_id)
    await state.set_state(Form.model)
    
    # نمایش فوری اطلاعات وارد شده
    data = await state.get_data()
    await message.answer(f"✅ آیدی ثبت شد: **{vehicle_id}**")
    await message.answer(f"📋 اطلاعات فعلی:\nسال: {data['year']}\nآیدی: {vehicle_id}")
    await message.answer("🔸 **مرحله ۳ از ۴**\nمدل وسیله نقلیه را وارد کنید:")

@dp.message(Form.model)
async def process_model(message: types.Message, state: FSMContext):
    model = message.text
    await state.update_data(model=model)
    await state.set_state(Form.additional_info)
    
    # نمایش فوری اطلاعات وارد شده
    data = await state.get_data()
    summary = (
        f"📋 اطلاعات تا اینجا:\n"
        f"• سال: {data['year']}\n"
        f"• آیدی: {data['vehicle_id']}\n"
        f"• مدل: {model}"
    )
    await message.answer(summary)
    await message.answer("🔸 **مرحله ۴ از ۴**\nدر صورت داشتن توضیحات اضافه وارد کنید یا /skip بزنید:")

@dp.message(Form.additional_info)
async def process_additional_info(message: types.Message, state: FSMContext):
    additional_info = message.text
    await state.update_data(additional_info=additional_info)
    data = await state.get_data()
    
    # متن نهایی کامل
    final_text = (
        "✅ **ثبت اطلاعات کامل شد**\n\n"
        f"📋 **خلاصه اطلاعات شما:**\n"
        f"• سال ساخت: {data['year']}\n"
        f"• آیدی وسیله: {data['vehicle_id']}\n"
        f"• مدل: {data['model']}\n"
        f"• توضیحات: {data.get('additional_info', 'بدون توضیح')}\n\n"
        "از مشارکت شما سپاسگزاریم."
    )
    
    # ۱. حتماً به کاربر نمایش داده می‌شود (در چت ربات)
    await message.answer(final_text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    
    # ۲. تلاش برای ارسال نسخه کامل به مالک
    owner_text = (
        "🚨 **اطلاعات جدید ثبت شد**\n\n"
        f"👤 از کاربر: {message.from_user.full_name} (@{message.from_user.username or 'بدون یوزرنیم'})\n"
        f"🆔 User ID: `{message.from_user.id}`\n\n"
        f"📦 **محتوا:**\n"
        f"• سال ساخت: {data['year']}\n"
        f"• آیدی وسیله: {data['vehicle_id']}\n"
        f"• مدل: {data['model']}\n"
        f"• توضیحات: {data.get('additional_info', '-')}"
    )
    
    if OWNER_CHAT_ID:
        try:
            await bot.send_message(OWNER_CHAT_ID, owner_text, parse_mode="Markdown")
            await message.answer("📤 یک کپی از اطلاعات نیز برای مالک سیستم ارسال شد.")
            logger.info(f"✅ اطلاعات به مالک (ID: {OWNER_CHAT_ID}) ارسال شد.")
        except Exception as e:
            error_msg = f"⚠️ اطلاعات ثبت شد، اما ارسال به مالک با خطا مواجه شد:\n`{e}`"
            await message.answer(error_msg, parse_mode="Markdown")
            logger.error(f"❌ خطا در ارسال به مالک: {e}")
    else:
        await message.answer("ℹ️ تنظیم مالک (OWNER_CHAT_ID) یافت نشد. اطلاعات فقط برای شما نمایش داده شد.")
    
    await state.clear()

@dp.message(Command("skip"))
async def skip_additional_info(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state != Form.additional_info:
        await message.answer("شما در مرحله‌ای نیستید که بتوانید این دستور را استفاده کنید.")
        return
    
    await state.update_data(additional_info="بدون توضیح")
    data = await state.get_data()
    
    # متن نهایی کامل
    final_text = (
        "✅ **ثبت اطلاعات کامل شد**\n\n"
        f"📋 **خلاصه اطلاعات شما:**\n"
        f"• سال ساخت: {data['year']}\n"
        f"• آیدی وسیله: {data['vehicle_id']}\n"
        f"• مدل: {data['model']}\n"
        f"• توضیحات: بدون توضیح\n\n"
        "از مشارکت شما سپاسگزاریم."
    )
    
    # ۱. حتماً به کاربر نمایش داده می‌شود
    await message.answer(final_text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    
    # ۲. تلاش برای ارسال نسخه کامل به مالک
    owner_text = (
        "🚨 **اطلاعات جدید ثبت شد**\n\n"
        f"👤 از کاربر: {message.from_user.full_name} (@{message.from_user.username or 'بدون یوزرنیم'})\n"
        f"🆔 User ID: `{message.from_user.id}`\n\n"
        f"📦 **محتوا:**\n"
        f"• سال ساخت: {data['year']}\n"
        f"• آیدی وسیله: {data['vehicle_id']}\n"
        f"• مدل: {data['model']}\n"
        f"• توضیحات: -"
    )
    
    if OWNER_CHAT_ID:
        try:
            await bot.send_message(OWNER_CHAT_ID, owner_text, parse_mode="Markdown")
            await message.answer("📤 یک کپی از اطلاعات نیز برای مالک سیستم ارسال شد.")
            logger.info(f"✅ اطلاعات به مالک (ID: {OWNER_CHAT_ID}) ارسال شد.")
        except Exception as e:
            error_msg = f"⚠️ اطلاعات ثبت شد، اما ارسال به مالک با خطا مواجه شد:\n`{e}`"
            await message.answer(error_msg, parse_mode="Markdown")
            logger.error(f"❌ خطا در ارسال به مالک: {e}")
    
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
