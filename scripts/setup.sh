#!/bin/bash

# Скрипт автоматической настройки сервера для CheekyBot
# Использование: ./scripts/setup.sh

set -e

echo "🚀 Настройка сервера для CheekyBot..."

# Проверка на root права
if [ "$EUID" -eq 0 ]; then
    echo "❌ Не запускайте скрипт от имени root!"
    exit 1
fi

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
echo "📦 Установка необходимых пакетов..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Установка Docker
echo "🐳 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

# Установка Docker Compose
echo "🐳 Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

# Создание директории для проекта
echo "📁 Создание директории проекта..."
mkdir -p ~/CheekyBot
cd ~/CheekyBot

# Клонирование репозитория (если не существует)
if [ ! -d ".git" ]; then
    echo "📥 Клонирование репозитория..."
    git clone https://github.com/your-username/CheekyBot.git .
else
    echo "✅ Репозиторий уже существует"
fi

# Создание файла конфигурации
echo "⚙️ Настройка конфигурации..."
if [ ! -f ".env" ]; then
    cp config.env.example .env
    echo "📝 Файл .env создан. Не забудьте настроить переменные окружения!"
else
    echo "✅ Файл .env уже существует"
fi

# Создание директории для логов
echo "📁 Создание директории для логов..."
mkdir -p logs

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chmod +x scripts/*.sh

# Включение автозапуска Docker
echo "🔄 Настройка автозапуска Docker..."
sudo systemctl enable docker

echo ""
echo "✅ Настройка сервера завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env и настройте переменные окружения"
echo "2. Запустите бота: docker-compose up -d"
echo "3. Проверьте логи: docker-compose logs -f bot"
echo ""
echo "🔧 Полезные команды:"
echo "  docker-compose up -d          # Запуск бота"
echo "  docker-compose down           # Остановка бота"
echo "  docker-compose logs -f bot    # Просмотр логов"
echo "  docker-compose restart bot    # Перезапуск бота"
echo ""
echo "📚 Документация: README.md" 