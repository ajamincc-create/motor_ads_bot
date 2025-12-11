import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Define FSM states
class AdForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_model = State()
    waiting_for_year = State()
    waiting_for_color = State()
    waiting_for_photo = State()

# Start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("سلام! برای ثبت آگهی موتور، اسم موتور را وارد کنید:")
    await state.set_state(AdForm.waiting_for_name)

# Handle motor name
@dp.message(AdForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("مدل موتور را وارد کنید:")
    await state.set_state(AdForm.waiting_for_model)

# Handle model
@dp.message(AdForm.waiting_for_model)
async def process_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("سال ساخت موتور را وارد کنید:")
    await state.set_state(AdForm.waiting_for_year)

# Handle year
@dp.message(AdForm.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("رنگ موتور را وارد کنید:")
    await state.set_state(AdForm.waiting_for_color)

# Handle color
@dp.message(AdForm.waiting_for_color)
async def process_color(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("عکس موتور را ارسال کنید:")
    await state.set_state(AdForm.waiting_for_photo)

# Handle photo
@dp.message(AdForm.waiting_for_photo, content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)

    data = await state.get_data()
    ad_text = (f"آگهی جدید ثبت شد:\n"
               f"اسم موتور: {data['name']}\n"
               f"مدل: {data['model']}\n"
               f"سال ساخت: {data['year']}\n"
               f"رنگ: {data['color']}")
    
    # Send to owner only
    await bot.send_photo(chat_id=OWNER_CHAT_ID, photo=data['photo'], caption=ad_text)
    await message.answer("آگهی شما دریافت شد و برای بررسی ارسال شد.")
    await state.clear()

# Run bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
