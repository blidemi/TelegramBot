import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

WELCOME_TEXT = (
    "Привеет! Добро пожаловать в нашу группу, {mentions}!\n\n"
    "Если не секрет, могли бы вы представиться, пожалуйста: "
    "Ваше имя, возраст, страна, где/на кого учитесь и какой у вас background 😊\n\n"
    "И просим не стесняться — спрашивайте, делитесь, общайтесь!"
)

pending_users = []
processing_lock = asyncio.Lock()

async def send_grouped_welcome(chat_id: int):
    await asyncio.sleep(2)
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
        pending_users.append(new_member.mention_html())
    
    if pending_users:
        asyncio.create_task(send_grouped_welcome(message.chat.id))

async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    # Render передает PORT в переменные окружения, по умолчанию 10000
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Веб-сервер слушает порт {port}")

async def main():
    await start_web_server()
    print("Бот запускает polling...")
    await dp.start_polling(bot, allowed_updates=["message"])

if __name__ == "__main__":
    asyncio.run(main())
