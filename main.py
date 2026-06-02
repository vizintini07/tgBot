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

@dp.message()
async def process_user_message(message: Message):
    """Обработчик всех текстовых сообщений пользователя"""
    user_id = message.from_user.id
    user_text = message.text

    # Инициализируем сессию, если вдруг ее нет
    if user_id not in user_sessions:
        user_sessions[user_id] = {"history": [], "last_question": ""}

    session = user_sessions[user_id]

    # Формируем пару "предыдущий вопрос бота - текущий ответ юзера"
    message_pair = {
        "question": session["last_question"],
        "answer": user_text
    }

    # Добавляем в историю
    session["history"].append(message_pair)

    # Чтобы контекст не разрастался бесконечно, можно ограничить историю (например, 5 последних пар)
    # if len(session["history"]) > 5:
    #   session["history"].pop(0)

    # Отправляем "typing..." пока ждем ответ от ИИ
    await bot.send_chat_action(chat_id=user_id, action="typing")

    # Получаем ответ от бэкенда
    backend_response = await send_to_backend(user_id, session["history"])

    action = backend_response.get("action")
    response_text = backend_response.get("text", "Извини, я немного задумался. Повторишь?")

    if action == "ask":
        # Бот задает уточняющий вопрос. Обновляем last_question
        session["last_question"] = response_text
        await message.answer(response_text)

    elif action == "recommend":
        # ИИ определил настроение и выдал рекомендацию
        movie_data = backend_response.get("movie")
