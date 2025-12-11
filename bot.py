import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

if not BOT_TOKEN or not OWNER_CHAT_ID:
    raise ValueError("BOT_TOKEN یا OWNER_CHAT_ID در فایل .env نیست!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# اطلاعات آگهی را در یک دیکشنری موقت ذخیره می‌کنیم
ads_data = {}

async def start_cmd(message: types.Message):
    if message.from_user.id != OWNER_CHAT_ID:
        await message.answer("شما اجازه استفاده از این ربات را ندارید.")
        return
    ads_data[message.from_user.id] = {}
    await message.answer("سلام! لطفا اسم موتور را وارد کن:")

async def process_text(message: types.Message):
    user_id = message.from_user.id
    if user_id != OWNER_CHAT_ID:
        return

    user_ads = ads_data.get(user_id)
    if user_ads is None:
        await start_cmd(message)
        return

    # گرفتن داده‌ها مرحله به مرحله
    if "name" not in user_ads:
        user_ads["name"] = message.text
        await message.answer("مدل موتور را وارد کن:")
    elif "model" not in user_ads:
        user_ads["model"] = message.text
        await message.answer("سال ساخت موتور را وارد کن:")
    elif "year" not in user_ads:
        user_ads["year"] = message.text
        await message.answer("رنگ موتور را وارد کن:")
    elif "color" not in user_ads:
        user_ads["color"] = message.text
        await message.answer("لطفا عکس موتور را ارسال کن:")
    else:
        await message.answer("لطفا عکس موتور را ارسال کن:")

async def process_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id != OWNER_CHAT_ID:
        return

    user_ads = ads_data.get(user_id)
    if not user_ads or "photo" in user_ads:
        await message.answer("ابتدا اطلاعات متن را وارد کن.")
        return

    photo_file = await message.photo[-1].download()
    user_ads["photo"] = photo_file.name

    # ارسال آگهی به خودت
    caption = f"📝 آگهی موتور:\nاسم: {user_ads['name']}\nمدل: {user_ads['model']}\nسال: {user_ads['year']}\nرنگ: {user_ads['color']}"
    await bot.send_photo(chat_id=OWNER_CHAT_ID, photo=InputFile(user_ads["photo"]), caption=caption)

    # پاک کردن داده‌های موقت
    del ads_data[user_id]
    await message.answer("آگهی ثبت شد! میتونی حالا فورواردش کنی.", reply_markup=ReplyKeyboardRemove())

# ثبت هندلرها
dp.message.register(start_cmd, Command(commands=["start"]))
dp.message.register(process_text, lambda message: message.content_type == "text")
dp.message.register(process_photo, lambda message: message.content_type == "photo")

# وب سرور ساده برای Render
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.add_routes([web.get("/", handle)])

async def main():
    from aiogram import asyncio
    asyncio.create_task(dp.start_polling(bot))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8000)))
    await site.start()
    print("Bot is running with web server for Render...")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

