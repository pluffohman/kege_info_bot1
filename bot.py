import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import create_database, populate_database, get_task


BOT_TOKEN="token"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

create_database()
populate_database()


class TaskState(StatesGroup):
    waiting_for_answer = State()

class TaskCallbackData(CallbackData, prefix="task"):
    task_number: int
class VariantCallbackData(CallbackData, prefix="variant"):
    task_number: int
    variant: int


@router.message(Command("start"))
async def start_handler(message: Message):
    keyboard = InlineKeyboardBuilder()

    for task_number in range(1, 28):
        keyboard.button(
            text=f"{task_number}",
            callback_data=TaskCallbackData(task_number=task_number).pack()
        )

    await message.answer("Выберите задание:", reply_markup=keyboard.as_markup())


@router.callback_query(TaskCallbackData.filter())
async def send_task(callback_query: CallbackQuery, callback_data: TaskCallbackData):
    task_number = callback_data.task_number
    keyboard = InlineKeyboardBuilder()

    for variant in [1, 2]:
        keyboard.button(
            text=f"Вариант {variant}",
            callback_data=VariantCallbackData(task_number=task_number, variant=variant).pack()
        )

    await callback_query.message.answer(f"Вы выбрали задание {task_number}. Выберите вариант:", reply_markup=keyboard.as_markup())
    await callback_query.answer()

@router.callback_query(VariantCallbackData.filter())
async def send_variant(callback_query: CallbackQuery, callback_data: VariantCallbackData, state: FSMContext):
    task_number = callback_data.task_number
    variant = callback_data.variant

    # Получаем задание из базы данных
    task = get_task(task_number, variant)
    if not task:
        await callback_query.message.answer("Задание не найдено в базе данных.")
        return

    if task.get("image_path") and os.path.exists(task["image_path"]):
        try:
            image_file = FSInputFile(task["image_path"])
            await bot.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=image_file,
                caption=f"Задание {task_number}, вариант {variant}.\nВведите ваш ответ:"
            )
        except Exception as e:
            await callback_query.message.answer(f"Ошибка при отправке изображения: {e}")

    # Отправляем ZIP-архив, ЕСЛИ ОН ЕСТЬ
    if task.get("zip_path") and os.path.exists(task["zip_path"]):
        try:
            zip_file = FSInputFile(task["zip_path"])
            await bot.send_document(
                chat_id=callback_query.message.chat.id,
                document=zip_file,
                caption="Дополнительные материалы"
            )
        except Exception as e:
            await callback_query.message.answer(f"Ошибка при отправке архива: {e}")

    await state.update_data(task_number=task_number, variant=variant, correct_answer=task["correct_answer"])
    await state.set_state(TaskState.waiting_for_answer)
    await callback_query.answer()


@router.message(TaskState.waiting_for_answer)
async def check_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    correct_answer = user_data["correct_answer"]

    if message.text.strip() == correct_answer.strip():
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {correct_answer}")

    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    print("Бот запущен")
    asyncio.run(main())