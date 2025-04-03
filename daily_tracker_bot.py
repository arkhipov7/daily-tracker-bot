import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === НАСТРОЙКИ ===
API_TOKEN = '8016029705:AAGs4aMAryzGZBSMhOvKdnItC-gg85XlWp0'
GOOGLE_SHEET_NAME = 'Трекер Даниила'

# Подключение к Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('google-credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1

# Настройка Telegram-бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === ОБРАБОТКА СООБЩЕНИЙ ===
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я твой трекер. В 20:00 буду присылать вопросы по дню ✍️")

@dp.message_handler(commands=['track'])
async def manual_check_in(message: types.Message):
    await ask_daily_questions(message.chat.id)

async def ask_daily_questions(chat_id):
    text = (
        "Привет! Как прошёл день?\n\n"
        "1. Во сколько встал?\n"
        "2. Была ли тренировка? 💪\n"
        "3. Сколько часов фокусной работы было? ⏳\n"
        "4. Что сделал по боту / клиенту? 🤖\n"
        "5. Что мешало? 🌀\n"
        "6. Что считаешь достижением дня? 🏆\n\n"
        "Ответь одним сообщением."
    )
    await bot.send_message(chat_id, text)

@dp.message_handler()
async def receive_daily_report(message: types.Message):
    now = datetime.now().strftime("%Y-%m-%d")
    data = message.text.split('\n')
    row = [now] + data[:6]  # Обрезаем лишнее, если пользователь ввёл больше
    sheet.append_row(row)
    await message.reply("Спасибо! Записал всё в таблицу ✅")

# === АВТОЗАПУСК ВОПРОСА В 20:00 ===
async def scheduler():
    while True:
        now = datetime.now()
        if now.hour == 20 and now.minute == 0:
            # Заменить ID на свой Telegram ID или список пользователей
            await ask_daily_questions(188573278)
            await asyncio.sleep(60)  # подождать минуту, чтобы не дублировать
        await asyncio.sleep(30)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
