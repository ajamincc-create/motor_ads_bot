import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
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
    logger.warning("⚠️ OWNER_CHAT_ID تنظیم نشده.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class MotorForm(StatesGroup):
    model = State()          # مدل موتور
    year = State()           # سال ساخت
    color = State()          # رنگ
    mileage = State()        # کارکرد (کیلومتر)
    location = State()       # محل
    contact = State()        # آیدی یا شماره تماس
    photos = State()         # عکس‌ها

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 ثبت آگهی موتور")],
            [KeyboardButton(text="ℹ️ راهنما")]
        ],
        resize_keyboard=True
    )
    await message.answer("🏍️ ربات ثبت آگهی موتور\nبرای ثبت آگهی جدید روی دکمه زیر کلیک کنید.", reply_markup=kb)

@dp.message(F.text == "ℹ️ راهنما")
async def show_help(message: types.Message):
    help_text = (
        "راهنمای ربات آگهی موتور\n\n"
        "1. روی '📝 ثبت آگهی موتور' کلیک کنید\n"
        "2. اطلاعات خواسته شده را وارد کنید\n"
        "3. حداقل یک عکس از موتور ارسال کنید\n"
        "4. اگر عکس بیشتری دارید، می‌توانید ارسال کنید\n"
        "5. برای پایان، /finish را تایپ کنید"
    )
    await message.answer(help_text)

@dp.message(F.text == "📝 ثبت آگهی موتور")
async def start_motor_form(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(MotorForm.model)
    await message.answer("📝 ثبت آگهی جدید\n\nمدل موتور را وارد کنید (مثال: هایابوسا، R6، کاوازاکی):", reply_markup=ReplyKeyboardRemove())

@dp.message(MotorForm.model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(MotorForm.year)
    await message.answer(f"سال ساخت را وارد کنید (مثال: 1402، 2023):")

@dp.message(MotorForm.year)
async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(MotorForm.color)
    await message.answer(f"رنگ موتور را وارد کنید (مثال: مشکی، قرمز، آبی):")

@dp.message(MotorForm.color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    await state.set_state(MotorForm.mileage)
    await message.answer(f"کارکرد را وارد کنید (کیلومتر - مثال: 15000):")

@dp.message(MotorForm.mileage)
async def process_mileage(message: types.Message, state: FSMContext):
    await state.update_data(mileage=message.text)
    await state.set_state(MotorForm.location)
    await message.answer(f"محل را وارد کنید (شهر/منطقه - مثال: تهران، میرداماد):")

@dp.message(MotorForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(MotorForm.contact)
    await message.answer(f"شماره تماس یا آیدی تلگرام را وارد کنید:")

@dp.message(MotorForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(MotorForm.photos)
    
    await message.answer("📸 لطفاً عکس‌های موتور را ارسال کنید:\n• حداقل یک عکس الزامی است\n• می‌توانید چند عکس ارسال کنید\n• بعد از ارسال عکس‌ها، /finish را تایپ کنید\n• برای لغو: /cancel")

# دریافت عکس‌ها
@dp.message(MotorForm.photos, F.photo)
async def process_photos(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # بزرگترین سایز عکس
    file_id = photo.file_id
    
    # ذخیره عکس‌ها در state
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(file_id)
    await state.update_data(photos=photos)
    
    count = len(photos)
    await message.answer(f"✅ عکس {count} دریافت شد\nعکس بیشتری ارسال کنید یا برای پایان: /finish")

# پایان ثبت عکس‌ها و ارسال نهایی
@dp.message(MotorForm.photos, Command("finish"))
async def finish_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    
    if not photos:
        await message.answer("⚠️ حداقل یک عکس الزامی است!\nلطفاً حداقل یک عکس از موتور ارسال کنید.")
        return
    
    # ساخت متن نهایی آگهی - با عنوان جدید
    ad_text = (
        "🏍 آگهی فروش 🏍\n\n"
        f"🏍 **مدل:** {data['model']}\n"
        f"📅 **سال ساخت:** {data['year']}\n"
        f"🎨 **رنگ:** {data['color']}\n"
        f"🛣 **کارکرد:** {data['mileage']} کیلومتر\n"
        f"📍 **محل:** {data['location']}\n"
        f"📞 **تماس:** {data['contact']}\n\n"
        f"👤 **ثبت کننده:** {message.from_user.full_name}\n"
        f"🆔 @{message.from_user.username or 'بدون یوزرنیم'}"
    )
    
    # ارسال به مالک (مدیر) - با آلبوم عکس
    if OWNER_CHAT_ID:
        try:
            # همیشه از media group استفاده می‌کنیم
            media_group = []
            
            # همه عکس‌ها را به آلبوم اضافه می‌کنیم
            for i, photo_id in enumerate(photos):
                if i == 0:  # عکس اول با کپشن
                    media_group.append(
                        InputMediaPhoto(
                            media=photo_id,
                            caption=ad_text,
                            parse_mode="Markdown"
                        )
                    )
                else:  # عکس‌های بعدی بدون کپشن
                    media_group.append(
                        InputMediaPhoto(media=photo_id)
                    )
            
            # ارسال آلبوم
            await bot.send_media_group(
                chat_id=OWNER_CHAT_ID,
                media=media_group
            )
            
            await message.answer("✅ آگهی شما با موفقیت ثبت و برای مدیر ارسال شد.\nبرای ثبت آگهی جدید روی /start کلیک کنید.")
            logger.info(f"✅ آگهی موتور برای مالک (ID: {OWNER_CHAT_ID}) ارسال شد. {len(photos)} عکس.")
            
        except Exception as e:
            error_msg = f"❌ خطا در ارسال آگهی: {e}"
            await message.answer(error_msg)
            logger.error(f"❌ خطا در ارسال آگهی به مالک: {e}")
    else:
        await message.answer("⚠️ تنظیمات مدیر یافت نشد.")
    
    await state.clear()

# دستور لغو
@dp.message(Command("cancel"))
async def cancel_form(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ ثبت آگهی لغو شد.\nبرای شروع مجدد روی /start کلیک کنید.")

# راهنمای عکس‌ها
@dp.message(MotorForm.photos)
async def invalid_photo_input(message: types.Message):
    await message.answer("📸 لطفاً فقط عکس ارسال کنید\nبرای پایان: /finish\nبرای لغو: /cancel")

async def main():
    logger.info("🚀 ربات آگهی موتور در حال شروع...")
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
