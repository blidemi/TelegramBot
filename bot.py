import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

# Бот будет брать токен из настроек хостинга (или из переменной окружения)
TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_ОТ_BOTFATHER_ДЛЯ_ТЕСТА_ДОМА")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ваш текст приветствия
WELCOME_TEXT = (
    "Привеет! Добро пожаловать в нашу группу, {mentions}!\n\n"
    "Если не секрет, могли бы вы представиться, пожалуйста: "
    "Ваше имя, возраст, страна, где/на кого учитесь и какой у вас background 😊\n\n"
    "И просим не стесняться — спрашивайте, делитесь, общайтесь!"
)

pending_users = []
processing_lock = asyncio.Lock()

async def send_grouped_welcome(chat_id: int):
    await asyncio.sleep(2)  # Пауза 2 сек, если зашло сразу несколько человек
    
    async with processing_lock:
        if not pending_users:
            return
        
        mentions_str = ", ".join(pending_users)
        pending_users.clear()
        
        text = WELCOME_TEXT.format(mentions=mentions_str)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

@dp.message(F.new_chat_members)
async def handle_new_members(message: Message):
    bot_info = await bot.get_me()
    
    for new_member in message.new_chat_members:
        if new_member.id == bot_info.id:
            continue
        
        mention = new_member.mention_html()
        pending_users.append(mention)
    
    if pending_users:
        asyncio.create_task(send_grouped_welcome(message.chat.id))

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot, allowed_updates=["message"])

if __name__ == "__main__":
    asyncio.run(main())