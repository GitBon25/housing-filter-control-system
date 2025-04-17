<h1 align="center">HousingBot</h1>

</h2>

<p align="center">

<img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" >

<img src="https://camo.githubusercontent.com/89e8b2eeeb9c2652c1dc087a9f72b514d8a50efd787ffced15c6af9c2c718c14/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d507974686f6e2d626c61636b3f7374796c653d666c61742d737175617265266c6f676f3d507974686f6e">

<img src="https://camo.githubusercontent.com/0ced1e0be80f32eee58612df57ae3dbc4aa9fa2e969060fc1491263e6f94d6f3/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4769744875622d3138313731373f7374796c653d666c61742d737175617265266c6f676f3d676974687562">
</p>

# 📖Описание
HousingBot — Telegram-бот для поиска жилой недвижимости (покупка или аренда) с использованием обработки естественного языка (NLP) и интеграцией с внешними API. Пользователи могут вводить запросы текстом или голосом, получать данные о квартирах (адрес, цена, площадь, фото), просматривать объекты на карте и использовать чек-листы для сделок.  

# ✨Особенности
**· Обработка запросов:** Извлечение параметров (местоположение, цена, площадь, комнаты, тип сделки) из текста или голоса с помощью Natasha.  
**· Поиск недвижимости:** Интеграция с API domclick.ru для актуальных предложений.  
**· Интерактивность:** Инлайн-кнопки, карты через Yandex Maps API.  
**· Хранение данных:** История запросов в PostgreSQL.  
**· Чек-листы:** Рекомендации для покупки (/sale) и аренды (/rent).  
**· Стилистика:** Уникальный стиль сообщений в духе антиутопии 1984.  

# 🛠Технические детал
**Язык:** Python 3.8+  
**Библиотеки:**  
· python-telegram-bot  
· psycopg2 (PostgreSQL)  
· requests (HTTP)  
· natasha (NLP)  
· speech_recognition (голос)  
· ffmpeg-python (аудио)  
**Сервисы:**  
· Telegram Bot API  
· domclick.ru API  
· Yandex Maps API  
· Google Speech API  
**Структура проекта:**
```
housing-filter-control-system/
├── bot/bot.py           # Сам бот
├── bot/messages.py      # Шаблоны сообщений для бота
├── bot/nlp_processor.py # NLP обработчки запросов
└── services/url.py      # Обращения к api domclick
```

# 🚀Установка
**1. Клонируйте репозиторий:**  
```
git clone https://github.com/username/housingbot.git
cd housingbot
```
**2. Установите зависимости:**  
```
pip install -r requirements.txt
```
**3. Установите FFmpeg:**  
```
Ubuntu: sudo apt-get install ffmpeg
macOS: brew install ffmpeg
Windows: Загрузите с сайта и добавьте в PATH.
```
**4. Настройте переменные окружения:**  
```
export TELEGRAM_TOKEN="your_telegram_bot_token"
export DATABASE_URL="postgresql://user:password@localhost:5432/housingbot"
```
**5. Настройте базу данных:**  
· Убедитесь, что PostgreSQL запущен.  
· Бот создаст таблицу users автоматически.  
**6. Запустите бота:**  
```
python bot/bot.py
```

# 📖 Использование
**1. Запустите бота:** Отправьте /start в Telegram.  
**2. Введите запрос:**  
· Текст: "Снять 1-комнатную квартиру в Москве до 30 тыс рублей"  
· Голосовое сообщение  
**3. Подтвердите параметры:**  
Бот извлечёт параметры и предложит поиск.  
**4. Получите результаты:**  
Фото, описание, карта.  
**Команды:**  
· /reset — сброс параметров  
· /lastresults — последние результаты  
· /sale — чек-лист покупки  
· /rent — чек-лист аренды  
· /help — справка  

# 📧Обратная связь
При обнаружении проблем или предложения идей для реализации обращаться:
**t.me/gitbon | gitbon@yandex.ru**
