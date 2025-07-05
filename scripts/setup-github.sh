#!/bin/bash

# Скрипт для настройки GitHub репозитория и секретов
# Использование: ./scripts/setup-github.sh

set -e

echo "🚀 Настройка GitHub репозитория для CheekyBot..."

# Проверка наличия gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен. Установите его:"
    echo "   macOS: brew install gh"
    echo "   Ubuntu: sudo apt install gh"
    echo "   Или скачайте с: https://cli.github.com/"
    exit 1
fi

# Проверка авторизации в GitHub
if ! gh auth status &> /dev/null; then
    echo "🔐 Авторизация в GitHub..."
    gh auth login
fi

# Создание репозитория
echo "📦 Создание репозитория..."
REPO_NAME="CheekyBot"
REPO_DESC="Telegram bot for flirting and romantic roleplay games"

# Проверяем, существует ли репозиторий
if gh repo view "$REPO_NAME" &> /dev/null; then
    echo "✅ Репозиторий $REPO_NAME уже существует"
else
    echo "📝 Создание нового репозитория..."
    gh repo create "$REPO_NAME" \
        --description "$REPO_DESC" \
        --public \
        --source=. \
        --remote=origin \
        --push
fi

# Добавление remote origin (если не существует)
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Добавление remote origin..."
    gh repo set-default "$REPO_NAME"
    git remote add origin "$(gh repo view --json url -q .url)"
fi

# Настройка секретов
echo "🔐 Настройка GitHub Secrets..."

# Функция для добавления секрета
add_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    if [ -z "$secret_value" ]; then
        echo "⚠️  $description не установлен. Пропускаем $secret_name"
        return
    fi
    
    echo "🔑 Добавление секрета: $secret_name"
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO_NAME"
}

# Запрос данных для секретов
echo ""
echo "📋 Введите данные для настройки секретов:"
echo ""

# HOST
read -p "🌐 IP адрес или домен сервера (HOST): " HOST
if [ -n "$HOST" ]; then
    add_secret "HOST" "$HOST" "IP адрес сервера"
fi

# USERNAME
read -p "👤 Имя пользователя на сервере (USERNAME): " USERNAME
if [ -n "$USERNAME" ]; then
    add_secret "USERNAME" "$USERNAME" "Имя пользователя"
fi

# PORT (опционально)
read -p "🔌 Порт SSH (по умолчанию 22): " PORT
PORT=${PORT:-22}
add_secret "PORT" "$PORT" "SSH порт"

# SSH KEY
echo ""
echo "🔑 Для настройки SSH ключа:"
echo "1. Создайте SSH ключ: ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo "2. Добавьте публичный ключ на сервер: ssh-copy-id $USERNAME@$HOST"
echo "3. Скопируйте содержимое приватного ключа (обычно ~/.ssh/id_ed25519)"
echo ""

read -p "📝 Введите содержимое приватного SSH ключа (или нажмите Enter для пропуска): " SSH_KEY
if [ -n "$SSH_KEY" ]; then
    add_secret "KEY" "$SSH_KEY" "SSH приватный ключ"
fi

# Настройка веток
echo "🌿 Настройка защиты веток..."
gh api repos/:owner/:repo/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["test"]}' \
    --field enforce_admins=true \
    --field required_pull_request_reviews='{"required_approving_review_count":1}' \
    --field restrictions=null || echo "⚠️ Не удалось настроить защиту веток"

# Настройка Issues и Projects
echo "📋 Включение Issues и Projects..."
gh api repos/:owner/:repo --method PATCH \
    --field has_issues=true \
    --field has_projects=true \
    --field has_wiki=true || echo "⚠️ Не удалось настроить дополнительные функции"

# Создание базовых Issues
echo "📝 Создание базовых Issues..."

# Issue для настройки сервера
gh issue create \
    --title "🚀 Настройка сервера" \
    --body "## Задачи для настройки сервера

### 1. Подготовка сервера
- [ ] Обновить систему: `sudo apt update && sudo apt upgrade -y`
- [ ] Установить Docker: `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`
- [ ] Установить Docker Compose
- [ ] Добавить пользователя в группу docker: `sudo usermod -aG docker \$USER`

### 2. Развертывание
- [ ] Клонировать репозиторий: `git clone https://github.com/\$USERNAME/CheekyBot.git`
- [ ] Настроить .env файл с токенами
- [ ] Запустить: `docker-compose up -d`

### 3. Проверка
- [ ] Проверить логи: `docker-compose logs -f bot`
- [ ] Протестировать бота в Telegram
- [ ] Настроить мониторинг

### Полезные команды:
\`\`\`bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f bot

# Перезапуск
docker-compose restart bot
\`\`\`" \
    --label "deployment" \
    --label "documentation" || echo "⚠️ Не удалось создать Issue"

# Issue для настройки бота
gh issue create \
    --title "🤖 Настройка Telegram бота" \
    --body "## Настройка Telegram бота

### 1. Создание бота
- [ ] Написать @BotFather в Telegram
- [ ] Создать нового бота: `/newbot`
- [ ] Получить токен бота
- [ ] Настроить команды бота

### 2. Настройка OpenAI
- [ ] Зарегистрироваться на OpenAI
- [ ] Получить API ключ
- [ ] Проверить лимиты и тарифы

### 3. Конфигурация
- [ ] Скопировать config.env.example в .env
- [ ] Заполнить BOT_TOKEN
- [ ] Заполнить OPENAI_API_KEY
- [ ] Настроить остальные параметры

### 4. Тестирование
- [ ] Запустить бота
- [ ] Протестировать команду /start
- [ ] Проверить все функции
- [ ] Настроить стоп-слова" \
    --label "configuration" \
    --label "documentation" || echo "⚠️ Не удалось создать Issue"

echo ""
echo "✅ Настройка GitHub репозитория завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте сервер согласно Issue '🚀 Настройка сервера'"
echo "2. Настройте бота согласно Issue '🤖 Настройка Telegram бота'"
echo "3. Запустите первый деплой: git push origin main"
echo ""
echo "🔗 Ссылки:"
echo "  Репозиторий: $(gh repo view --json url -q .url)"
echo "  Actions: $(gh repo view --json url -q .url)/actions"
echo "  Issues: $(gh repo view --json url -q .url)/issues" 