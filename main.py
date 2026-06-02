import asyncio
import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

# Настройки
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com")  # URL где будет размещено приложение

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
        "Расскажи, какое у тебя сейчас настроение, или чего хочется от фильма на вечер?\n\n"
        "Открой Mini App для более удобного интерфейса 👇"
    )

    # Создаем кнопку для Mini App
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎬 Открыть Кинотавр",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )

    await message.answer(welcome_text, reply_markup=builder.as_markup())


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

        if movie_data:
            # Парсим данные фильма (ключи зависят от структуры таблицы movies коллеги)
            title = movie_data.get("title", "Неизвестный фильм")
            description = movie_data.get("description", "Описание отсутствует.")
            year = movie_data.get("year", "")
            poster_url = movie_data.get("poster_url", "")
            kp_url = movie_data.get("kp_url", "")
            rutube_url = movie_data.get("rutube_url", "")

            # Формируем сообщение с фильмом
            final_message = f"{response_text}\n\n"
            final_message += f"🍿 <b>{title}</b> {f'({year})' if year else ''}\n"
            final_message += f"📝 {description}\n\n"

            # Добавляем ссылки если есть
            links = []
            if kp_url:
                links.append(f'<a href="{kp_url}">Кинопоиск</a>')
            if rutube_url:
                links.append(f'<a href="{rutube_url}">Смотреть на Rutube</a>')

            if links:
                final_message += "🔗 " + " | ".join(links)

            await message.answer(final_message, parse_mode="HTML", disable_web_page_preview=False)

            # Сбрасываем историю после успешной рекомендации
            user_sessions[user_id] = {"history": [], "last_question": ""}
        else:
            await message.answer(
                f"{response_text}\n\nК сожалению, в базе пока нет подходящего фильма для этого настроения 😔")
            # Сбрасываем историю
            user_sessions[user_id] = {"history": [], "last_question": ""}

    else:
        # Обработка ошибок
        await message.answer(response_text)


# Web server для обслуживания Mini App
async def webapp_handler(request):
    """Обработчик для главной страницы Mini App"""
    with open('miniapp/templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
        # Replace API_URL placeholder
        html = html.replace('API_URL_PLACEHOLDER', API_URL)
    return web.Response(text=html, content_type='text/html')


async def serve_static(request):
    """Обработчик для статических файлов"""
    filename = request.match_info['filename']
    filepath = os.path.join('miniapp', 'static', filename)

    if not os.path.exists(filepath):
        return web.Response(status=404, text='File not found')

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine content type
    content_type = 'text/plain'
    if filename.endswith('.css'):
        content_type = 'text/css'
    elif filename.endswith('.js'):
        content_type = 'application/javascript'
        # Replace API_URL placeholder in JavaScript
        content = content.replace('API_URL_PLACEHOLDER', API_URL)

    return web.Response(text=content, content_type=content_type)


async def init_webapp():
    """Инициализация веб-сервера для Mini App"""
    app = web.Application()
    app.router.add_get('/', webapp_handler)
    app.router.add_get('/static/{filename:.*}', serve_static)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    logging.info("WebApp server started at http://localhost:8080")


async def main():
    logging.basicConfig(level=logging.INFO)

    # Запускаем веб-сервер для Mini App (для локальной разработки)
    # В продакшене используйте ngrok или разверните на реальном сервере
    await init_webapp()

    logging.info("Starting Telegram Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
