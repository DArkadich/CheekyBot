#!/bin/bash

# Скрипт для настройки GitHub Secrets
# Использование: ./scripts/setup-secrets.sh

set -e

echo "🔐 Настройка GitHub Secrets для CheekyBot..."

# Проверка наличия gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен. Установите его:"
    echo "   macOS: brew install gh"
    echo "   Ubuntu: sudo apt install gh"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "🔐 Авторизация в GitHub..."
    gh auth login
fi

echo ""
echo "📋 Введите данные для настройки секретов:"
echo ""

# HOST
read -p "🌐 IP адрес или домен сервера (HOST): " HOST
if [ -n "$HOST" ]; then
    echo "🔑 Добавление секрета: HOST"
    echo "$HOST" | gh secret set HOST --repo DArkadich/CheekyBot
fi

# USERNAME
read -p "👤 Имя пользователя на сервере (USERNAME): " USERNAME
if [ -n "$USERNAME" ]; then
    echo "🔑 Добавление секрета: USERNAME"
    echo "$USERNAME" | gh secret set USERNAME --repo DArkadich/CheekyBot
fi

# PORT
read -p "🔌 Порт SSH (по умолчанию 22): " PORT
PORT=${PORT:-22}
echo "🔑 Добавление секрета: PORT"
echo "$PORT" | gh secret set PORT --repo DArkadich/CheekyBot

# SSH KEY
echo ""
echo "🔑 Для настройки SSH ключа:"
echo "1. Создайте SSH ключ: ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo "2. Добавьте публичный ключ на сервер: ssh-copy-id $USERNAME@$HOST"
echo "3. Скопируйте содержимое приватного ключа (обычно ~/.ssh/id_ed25519)"
echo ""

read -p "📝 Введите содержимое приватного SSH ключа (или нажмите Enter для пропуска): " SSH_KEY
if [ -n "$SSH_KEY" ]; then
    echo "🔑 Добавление секрета: KEY"
    echo "$SSH_KEY" | gh secret set KEY --repo DArkadich/CheekyBot
fi

# Проверка существующих секретов
echo ""
echo "📋 Проверка настроенных секретов:"
gh secret list --repo DArkadich/CheekyBot

echo ""
echo "✅ Настройка секретов завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте сервер согласно SSH_KEYS_GUIDE.md"
echo "2. Протестируйте SSH подключение: ssh $USERNAME@$HOST"
echo "3. Запустите первый деплой: git push origin main"
echo ""
echo "🔗 Ссылки:"
echo "  Репозиторий: https://github.com/DArkadich/CheekyBot"
echo "  Actions: https://github.com/DArkadich/CheekyBot/actions" 