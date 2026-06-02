import asyncio
import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Настройки
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище сессий (для продакшена лучше использовать Redis или БД)
# Структура: {user_id: {"history": [], "last_question": ""}}
user_sessions = {}


async def send_to_backend(user_id: int, history: list) -> dict:
    """Функция для отправки запроса к FastAPI бэкенду"""
    payload = {
        "user_id": user_id,
        "consversion": history  # Используем опечатку из бэкенда для совместимости
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"Backend error: {response.status}")
                    return {"action": "error", "text": "Произошла ошибка на сервере."}
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return {"action": "error", "text": "Не удалось связаться с мозговым центром."}


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id

    # Очищаем историю при новом старте
    user_sessions[user_id] = {"history": [], "last_question": ""}

    welcome_text = (
        "Привет! Я Кинотавр 🎬\n"
        "Расскажи, какое у тебя сейчас настроение, или чего хочется от фильма на вечер?"
    )

    # Запоминаем вопрос бота
    user_sessions[user_id]["last_question"] = welcome_text
    await message.answer(welcome_text)

