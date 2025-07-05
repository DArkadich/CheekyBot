# 🚀 Настройка GitHub Actions для CheekyBot

## 📋 Что у нас есть

### GitHub Actions Workflows:
1. **`deploy.yml`** - Основной workflow для деплоя на сервер
2. **`test.yml`** - Тестирование с pytest и покрытием кода
3. **`lint.yml`** - Проверка качества кода (flake8, black, isort, mypy)
4. **`format.yml`** - Автоматическое форматирование кода
5. **`security.yml`** - Проверка безопасности (safety, bandit, trufflehog)

### Инструменты разработки:
- **Black** - форматирование кода
- **isort** - сортировка импортов
- **flake8** - линтинг
- **mypy** - проверка типов
- **pytest** - тестирование
- **pre-commit** - хуки для git

## 🔧 Быстрая настройка

### 1. Создание репозитория на GitHub
```bash
# Запустите автоматический скрипт
./scripts/setup-github.sh
```

Или вручную:
```bash
# Создание репозитория
gh repo create CheekyBot --public --source=. --remote=origin --push
```

### 2. Настройка секретов
В настройках репозитория (Settings → Secrets and variables → Actions) добавьте:

- `HOST` - IP адрес или домен сервера
- `USERNAME` - имя пользователя на сервере
- `KEY` - приватный SSH ключ
- `PORT` - SSH порт (по умолчанию 22)

### 3. Настройка защиты веток
```bash
# Защита main ветки
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["test","lint"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

## 🔄 Как это работает

### При Push в main:
1. **test** - запускаются тесты
2. **lint** - проверяется качество кода
3. **security** - проверяется безопасность
4. **deploy** - деплой на сервер (только если все тесты прошли)

### При Pull Request:
1. **test** - тестирование
2. **lint** - линтинг
3. **security** - проверка безопасности
4. **format** - проверка форматирования

### При workflow_dispatch:
- Можно запустить любой workflow вручную

## 📊 Мониторинг

### Проверка статуса:
- GitHub Actions → вкладка Actions
- Проверка статуса каждого workflow

### Логи:
- Каждый workflow создает логи
- Security workflow создает артефакты с отчетами

### Уведомления:
- Настройте уведомления в GitHub Settings
- Можно подключить Slack/Discord webhooks

## 🛠 Локальная разработка

### Установка инструментов:
```bash
pip install -r requirements-dev.txt
```

### Pre-commit хуки:
```bash
pre-commit install
```

### Запуск проверок локально:
```bash
# Все проверки
pre-commit run --all-files

# Отдельные проверки
black .
isort .
flake8 .
mypy config/ database/ services/ handlers/ main.py
pytest tests/ -v
```

## 🔧 Настройка сервера

### Автоматическая настройка:
```bash
# На сервере
curl -fsSL https://raw.githubusercontent.com/your-username/CheekyBot/main/scripts/setup.sh | bash
```

### Ручная настройка:
1. Установить Docker и Docker Compose
2. Клонировать репозиторий
3. Настроить .env файл
4. Запустить docker-compose up -d

## 📈 Метрики качества

### Покрытие кода:
- Минимум 80% покрытия тестами
- Отчеты в GitHub Actions artifacts

### Качество кода:
- Black форматирование
- isort сортировка импортов
- flake8 без ошибок
- mypy без ошибок типов

### Безопасность:
- safety без уязвимостей
- bandit без проблем безопасности
- trufflehog без секретов в коде

## 🚨 Устранение проблем

### Тесты не проходят:
1. Проверьте логи в GitHub Actions
2. Запустите тесты локально: `pytest tests/ -v`
3. Исправьте ошибки и перезапустите

### Линтинг не проходит:
1. Запустите форматирование: `black . && isort .`
2. Исправьте ошибки flake8
3. Проверьте типы: `mypy config/ database/ services/ handlers/ main.py`

### Деплой не работает:
1. Проверьте секреты в GitHub
2. Проверьте SSH доступ к серверу
3. Проверьте логи деплоя

## 📞 Поддержка

- **Issues**: для багов в CI/CD
- **Discussions**: для вопросов по настройке
- **Wiki**: дополнительная документация

---

**GitHub Actions настроены и готовы к работе! 🎉** 