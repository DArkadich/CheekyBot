# CheekyBot - Telegram Bot для флирта и романтического общения

🤖 Интеллектуальный Telegram-бот для флирта и эротических ролевых игр с использованием OpenAI GPT-4.

## 🚀 Возможности

### Основные функции
- **4 стиля общения**: игривый, романтичный, страстный, загадочный
- **Гендерная настройка**: выбор пола бота (М/Ж/Нейтральный)
- **Адаптивное общение**: плавный переход между уровнями общения
- **Система безопасности**: стоп-слова и согласие на контент 18+
- **Ролевые сценарии**: готовые сценарии для ролевых игр
- **Статистика**: отслеживание активности пользователей

### Технические особенности
- **AI-генерация**: использование OpenAI GPT-4 для ответов
- **Кеширование**: Redis для оптимизации запросов к API
- **База данных**: PostgreSQL для хранения данных пользователей и диалогов
- **Асинхронность**: полная асинхронная архитектура
- **Контейнеризация**: Docker для простого развертывания

## 🛠 Технологии

- **Python 3.11+**
- **Aiogram 3.4.1** - Telegram Bot API
- **OpenAI API** - генерация ответов
- **PostgreSQL** - основная база данных
- **Redis** - кеширование
- **Docker & Docker Compose** - контейнеризация

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose
- Telegram Bot Token
- OpenAI API Key
- PostgreSQL (если запуск без Docker)

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd CheekyBot
```

### 2. Настройка переменных окружения
```bash
cp config.env.example .env
```

Отредактируйте файл `.env`:
```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Database Configuration (для Docker)
DATABASE_URL=postgresql://cheekybot:password@postgres:5432/cheekybot

# Redis Configuration (для Docker)
REDIS_URL=redis://redis:6379/0

# Bot Settings
DEFAULT_GENDER=neutral
MAX_MESSAGE_LENGTH=4096
CACHE_TTL=3600
LOG_LEVEL=INFO
```

### 3. Запуск с Docker Compose
```bash
docker-compose up -d
```

### 4. Проверка работы
```bash
docker-compose logs -f bot
```

## 🔧 Локальная разработка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
# Установка PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres createdb cheekybot
sudo -u postgres psql -d cheekybot -f database/init.sql
```

### 3. Настройка Redis
```bash
# Установка Redis
sudo apt-get install redis-server

# Запуск Redis
sudo systemctl start redis-server
```

### 4. Запуск бота
```bash
docker compose up -d
```

### 5. Просмотр логов
```bash
docker compose logs -f bot
```

## 📁 Структура проекта

```
CheekyBot/
├── config/                 # Конфигурация
│   ├── __init__.py
│   └── settings.py        # Настройки приложения
├── database/              # Работа с базой данных
│   ├── __init__.py
│   ├── connection.py      # Менеджер подключений
│   ├── models.py          # Модели данных
│   └── init.sql           # Инициализация БД
├── handlers/              # Обработчики сообщений
│   ├── __init__.py
│   ├── keyboards.py       # Клавиатуры Telegram
│   ├── user_handlers.py   # Основные обработчики
│   ├── settings_handlers.py # Обработчики настроек
│   └── roleplay_handlers.py # Обработчики ролевых игр
├── services/              # Сервисы
│   ├── __init__.py
│   └── openai_service.py  # Сервис OpenAI
├── logs/                  # Логи (создается автоматически)
├── main.py               # Главный файл
├── requirements.txt      # Зависимости Python
├── Dockerfile           # Docker образ
├── docker-compose.yml   # Docker Compose
├── config.env.example   # Пример конфигурации
└── README.md           # Документация
```

## 🔐 Безопасность

### Система согласия
- Обязательное согласие на контент 18+
- Возможность отзыва согласия
- Проверка возраста пользователя

### Стоп-слова
- Настраиваемый список запрещенных слов
- Автоматическая фильтрация сообщений
- Возможность добавления пользовательских стоп-слов

### Обработка ошибок
- Логирование всех ошибок
- Graceful handling исключений
- Автоматическое восстановление после сбоев

## 📊 Мониторинг и логирование

### Логи
- Ротация логов (1 день)
- Хранение логов 7 дней
- Структурированное логирование

### Статистика
- Количество сообщений
- Использованные токены
- Любимый стиль общения
- Активность пользователей

## 🚀 Развертывание на Timeweb

### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
# Docker Compose теперь встроен в Docker Desktop
# Для Linux может потребоваться установка:
# sudo apt-get update && sudo apt-get install docker-compose-plugin
```

### 2. Клонирование и настройка
```bash
git clone <repository-url>
cd CheekyBot
cp config.env.example .env
# Редактирование .env файла
```

### 3. Запуск
```bash
docker-compose up -d
```

### 4. Настройка автозапуска
```bash
sudo systemctl enable docker
```

## 🔧 Настройка CI/CD

### GitHub Actions
Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Timeweb

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd /path/to/CheekyBot
          git pull origin main
          docker compose down
docker compose up -d --build
```

## 📝 API Документация

### Основные команды бота
- `/start` - Начало работы с ботом
- `/help` - Справка по использованию
- `/settings` - Настройки профиля
- `/stats` - Статистика пользователя

### Стили общения
1. **Игривый** - легкий флирт, шутки, эмодзи
2. **Романтичный** - нежные комплименты, поэтичность
3. **Страстный** - яркие эмоции, смелые выражения
4. **Загадочный** - интрига, намеки, таинственность

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## ⚠️ Отказ от ответственности

Этот бот предназначен для взрослых пользователей (18+). Разработчики не несут ответственности за использование бота несовершеннолетними или в незаконных целях.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте Issue в GitHub
- Обратитесь к документации
- Проверьте логи в папке `logs/`

---

**CheekyBot** - Интеллектуальный флирт-бот для Telegram 🤖💕 # Trigger deployment
# Trigger CI
