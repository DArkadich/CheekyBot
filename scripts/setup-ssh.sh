#!/bin/bash

# Скрипт для настройки SSH ключей для GitHub Actions
# Использование: ./scripts/setup-ssh.sh

set -e

echo "🔑 Настройка SSH для GitHub Actions..."

# Проверка существования ключа
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "📝 Создание нового SSH ключа..."
    ssh-keygen -t ed25519 -C "github-actions@cheekybot" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH ключ создан"
else
    echo "✅ SSH ключ уже существует"
fi

# Настройка прав доступа
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

echo ""
echo "📋 Публичный ключ (добавьте на сервер):"
echo "=========================================="
cat ~/.ssh/id_ed25519.pub
echo "=========================================="

echo ""
echo "🔐 Приватный ключ (добавьте в GitHub Secrets как KEY):"
echo "=========================================="
cat ~/.ssh/id_ed25519
echo "=========================================="

echo ""
echo "📝 Инструкции по настройке:"
echo ""
echo "1. 🖥️  На сервере:"
echo "   ssh-copy-id username@server_ip"
echo "   # или вручную добавьте публичный ключ в ~/.ssh/authorized_keys"
echo ""
echo "2. 🔐 В GitHub репозитории:"
echo "   Settings → Secrets and variables → Actions"
echo "   Добавьте следующие секреты:"
echo "   - KEY: (приватный ключ выше)"
echo "   - HOST: IP адрес сервера"
echo "   - USERNAME: имя пользователя на сервере"
echo "   - PORT: SSH порт (обычно 22)"
echo ""
echo "3. 🧪 Тестирование:"
echo "   ssh username@server_ip"
echo ""
echo "4. 🚀 Запуск деплоя:"
echo "   git push origin main"
echo ""
echo "✅ SSH настройка завершена!" 