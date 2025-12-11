from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
import os

# توکن و بات
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# تعریف استیت‌ها
class MotorForm(StatesGroup):
    name = State()
    model = State()
    year = State()
    color = State()
    engine_cc = State()

# شروع ربات
@dp.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext):
    await message.answer("سلام! اسم موتور رو وارد کن:")
    await state.set_state(MotorForm.name)

# دریافت اسم موتور
@dp.message()
async def process_name(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    
    if state_name == MotorForm.name.state:
        await state.update_data(name=message.text)
        await message.answer("مدل موتور رو وارد کن:")
        await state.set_state(MotorForm.model)
    
    elif state_name == MotorForm.model.state:
        await state.update_data(model=message.text)
        await message.answer("سال ساخت موتور رو وارد کن:")
        await state.set_state(MotorForm.year)
    
    elif state_name == MotorForm.year.state:
        await state.update_data(year=message.text)
        await message.answer("رنگ موتور رو وارد کن:")
        await state.set_state(MotorForm.color)
    
    elif state_name == MotorForm.color.state:
        await state.update_data(color=message.text)
        await message.answer("حجم موتور (CC) رو وارد کن:")
        await state.set_state(MotorForm.engine_cc)
    
    elif state_name == MotorForm.engine_cc.state:
        await state.update_data(engine_cc=message.text)
        data = await state.get_data()
        await message.answer(
            f"اطلاعات موتور ثبت شد:\n"
            f"اسم: {data['name']}\n"
            f"مدل: {data['model']}\n"
            f"سال ساخت: {data['year']}\n"
            f"رنگ: {data['color']}\n"
            f"حجم موتور: {data['engine_cc']}"
        )
        await state.clear()
