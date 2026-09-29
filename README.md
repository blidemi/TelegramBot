Вот подробный, готовый файл **`README.md`**, в котором расписан весь процесс создание и деплой бота от А до Я. В нём учтены все особенности для **Windows** и **macOS**, а также все нюансы, с которыми сталкиваются при деплое на Render.

Скопируйте текст ниже и вставьте его в файл `README.md` в вашем репозитории на GitHub:

```markdown
# Telegram Welcome Bot (Group Greeting Bot)

Telegram-бот для автоматического приветствия новых участников в группах/чатах. 
Бот поддерживает объединение (пакетирование) нескольких вступающих пользователей в одно приветственное сообщение и развернут для бесплатной круглосуточной работы (24/7) на хостинге **Render.com**.

---

## 🛠 Технологический стек
* **Python** 3.11+
* **aiogram 3.x** — асинхронный фреймворк для взаимодействия с Telegram Bot API
* **aiohttp** — асинхронный веб-сервер для поддержки веб-сервиса на Render
* **Render.com** — бесплатный хостинг (Free Web Service)

---

## 📁 Структура проекта
```text
TelegramBot/
├── bot.py                # Основной код бота и фиктивный веб-сервер
├── requirements.txt      # Список библиотек/зависимостей Python
├── Procfile              # Команда запуска для хостинга
└── .python-version       # Фиксация стабильной версии Python (3.11.9)

```

---

## 🚀 Пошаговая инструкция: От создания до деплоя 24/7

### Шаг 1. Создание и настройка бота в Telegram (@BotFather)

1. Откройте Telegram и найдите бота **`@BotFather`**.
2. Отправьте команду `/newbot`, укажите имя и username (должен оканчиваться на `bot`).
3. Скопируйте полученный **API Token**.
4. **Важные настройки для работы в группах**:
* Отправьте `/setprivacy` -> Выберите бота -> Нажмите **Disable** *(отключает приватность, чтобы бот видел вступление участников)*.
* Отправьте `/setjoingroups` -> Выберите бота -> Нажмите **Enable** *(разрешает добавлять бота в группы)*.



---

### Шаг 2. Настройка локального окружения и файлов

#### 1. Файл `requirements.txt`

Задает необходимые зависимости:

```text
aiogram>=3.17.0
aiohttp

```

#### 2. Файл `Procfile` (без расширения, с заглавной `P`)

Инструкция запуска для серверов:

```text
web: python bot.py

```

#### 3. Файл `.python-version`

Фиксирует стабильную версию Python (чтобы избежать ошибок сборки C-расширений на Render):

```text
3.11.9

```

> 💡 **Примечание для macOS**: Файлы, начинающиеся с точки (например `.python-version`), являются скрытыми. Чтобы увидеть их в Finder, нажмите комбинацию клавиш: **`Cmd (⌘) + Shift (⇧) + Точка (.)`**.

#### 4. Файл `bot.py`

Полный исходный код бота:

```python
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiohttp import web

# Токен берется из переменных окружения
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

# Веб-сервер для прохождения Port Check на Render
async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    print("Бот запускает polling...")
    await dp.start_polling(bot, allowed_updates=["message"])

if __name__ == "__main__":
    asyncio.run(main())

```

---

### Шаг 3. Локальный запуск и остановка (Тестирование)

#### 🍏 macOS (Терминал / VS Code):

* **Запуск**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="ВАШ_ТОКЕН"
python bot.py

```


* **Остановка**: `Control + C`
* **Принудительное закрытие незавершенных процессов**:
```bash
pkill -f bot.py

```



#### 🪟 Windows (PowerShell / Command Prompt):

* **Запуск**:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set BOT_TOKEN="ВАШ_ТОКЕН"
python bot.py

```


* **Остановка**: `Ctrl + C`
* **Принудительное закрытие процессов (PowerShell)**:
```powershell
Stop-Process -Name "python" -Force

```



---

### Шаг 4. Публикация кода на GitHub

1. Загрузите файлы `bot.py`, `requirements.txt`, `Procfile` и `.python-version` в ваш репозиторий GitHub.

---

### Шаг 5. Бесплатный деплой на Render.com (24/7)

1. Зарегистрируйтесь на [Render.com](https://render.com/).
2. В верхнем меню нажмите **`+ New`** -> выберите **Web Service** (НЕ Background Worker, так как он платный).
3. Подключите ваш GitHub-репозиторий.
4. Укажите основные параметры сервиса:
* **Name**: `Friendly-Bot` (или любое другое имя)
* **Language**: `Python 3`
* **Region**: Задайте любой
* **Branch**: `main` (или `master`)
* **Root Directory**: *Оставьте пустым*
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `python bot.py`
* **Instance Type**: **Free ($0 / month)**


5. Добавьте переменную окружения в блоке **Environment Variables**:
* **Key**: `BOT_TOKEN`
* **Value**: *Ваш токен от BotFather (строчка вида 123456789:ABC...)*


6. Нажмите **Deploy Web Service**.

---

### ⚠️ Частые ошибки при деплое и их решения

1. **`TelegramConflictError: terminated by other getUpdates request`**
* *Причина*: Бот запущен одновременно на локальном компьютере и на сервере Render.
* *Решение*: Выключите скрипт на компьютере (`Control + C` или `pkill -f bot.py` на Mac / `Stop-Process` на Windows).


2. **`Port scan timeout reached, no open ports detected`**
* *Причина*: Render требует, чтобы Web Service прослушивал порт HTTP.
* *Решение*: Убедитесь, что в `bot.py` интегрирован модуль `aiohttp` с функцией `start_web_server()`, открывающей `os.environ.get("PORT")`.


3. **`Exited with status 1 while building... / pydantic-core error`**
* *Причина*: Render использует слишком новую версию Python (например, 3.14), под которую нет готовых wheel-пакетов.
* *Решение*: Добавьте файл `.python-version` с текстом `3.11.9` в корень репозитория.



---

### Шаг 6. Использование бота в Telegram-группе

1. Зайдите в целевую группу в Telegram.
2. Добавьте бота по его username (например `@lin_friendly_bot`).
3. Назначьте бота **Администратором** группы с правом отправки сообщений.
4. При вступлении новых участников бот автоматически отправит сгруппированное приветствие через 2 секунды.

```

```
