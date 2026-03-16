import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import aiohttp

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8656316812:AAEfFrLFUsUXj2qxCy7IQYRVQCWl8iSVhpI"
OPENROUTER_API_KEY = "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"
# Актуальная модель Qwen Coder на OpenRouter
MODEL_NAME = "qwen/qwen3-coder:free" 

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def get_ai_response(user_text):
    """Запрос к OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/aiogram/aiogram", # Обязательно для OpenRouter
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a professional coding assistant. Answer in detail and provide clean code."},
            {"role": "user", "content": user_text}
        ]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await resp.text()
                    return f"Ошибка API: {resp.status}\n{error_text}"
        except Exception as e:
            return f"Ошибка соединения: {str(e)}"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Ready. Конфиг применён. Отправляй код или задачу — Qwen Coder на связи.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    # Индикация "печатает..." в телеграме
    await bot.send_chat_action(message.chat.id, "typing")
    
    response = await get_ai_response(message.text)
    
    # Если ответ слишком длинный, Телеграм его не пропустит (лимит 4096 символов)
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            await message.answer(response[x:x+4096])
    else:
        await message.answer(response, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
