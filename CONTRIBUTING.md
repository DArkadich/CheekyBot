# Руководство для контрибьюторов

Спасибо за интерес к проекту CheekyBot! 🎉

## 🚀 Быстрый старт для разработчиков

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/CheekyBot.git
cd CheekyBot
```

### 2. Настройка виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements-dev.txt
```

### 4. Настройка pre-commit хуков
```bash
pre-commit install
```

### 5. Настройка конфигурации
```bash
cp config.env.example .env
# Отредактируйте .env файл с вашими токенами
```

## 🧪 Запуск тестов

### Все тесты
```bash
pytest tests/ -v
```

### С покрытием кода
```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Отдельные тесты
```bash
pytest tests/test_config.py -v
pytest tests/test_models.py -v
```

## 🔧 Инструменты разработки

### Форматирование кода
```bash
# Автоматическое форматирование
black .
isort .

# Проверка форматирования
black --check .
isort --check-only .
```

### Линтинг
```bash
# Проверка стиля кода
flake8 .

# Проверка типов
mypy config/ database/ services/ handlers/ main.py
```

### Безопасность
```bash
# Проверка зависимостей
safety check

# Проверка кода на уязвимости
bandit -r .
```

## 📝 Процесс разработки

### 1. Создание ветки
```bash
git checkout -b feature/your-feature-name
# или
git checkout -b fix/your-bug-fix
```

### 2. Внесение изменений
- Следуйте стилю кода (black + isort)
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости

### 3. Проверка кода
```bash
# Запуск всех проверок
pre-commit run --all-files

# Или по отдельности
black .
isort .
flake8 .
mypy config/ database/ services/ handlers/ main.py
pytest tests/ -v
```

### 4. Коммит изменений
```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push и создание Pull Request
```bash
git push origin feature/your-feature-name
```

## 📋 Стандарты кода

### Стиль кода
- Используйте **Black** для форматирования
- Используйте **isort** для сортировки импортов
- Максимальная длина строки: 88 символов
- Используйте типизацию (type hints)

### Именование
- **Файлы**: snake_case (например, `user_handlers.py`)
- **Классы**: PascalCase (например, `DatabaseManager`)
- **Функции/переменные**: snake_case (например, `get_user_stats`)
- **Константы**: UPPER_SNAKE_CASE (например, `MAX_MESSAGE_LENGTH`)

### Документация
- Используйте docstrings для всех функций и классов
- Обновляйте README.md при изменении API
- Добавляйте комментарии к сложной логике

### Тестирование
- Покрытие кода должно быть не менее 80%
- Добавляйте тесты для новой функциональности
- Используйте моки для внешних зависимостей

## 🐛 Сообщение об ошибках

При создании Issue:

1. **Опишите проблему** - что происходит и что должно происходить
2. **Шаги для воспроизведения** - пошаговая инструкция
3. **Ожидаемое поведение** - что должно произойти
4. **Скриншоты/логи** - если применимо
5. **Окружение** - версия Python, ОС, зависимости

## 🔄 Pull Request

При создании PR:

1. **Опишите изменения** - что было добавлено/изменено
2. **Ссылка на Issue** - если исправляете баг
3. **Тесты** - убедитесь, что все тесты проходят
4. **Документация** - обновите README если нужно
5. **Скриншоты** - для UI изменений

## 📚 Полезные команды

### Docker
```bash
# Запуск в режиме разработки
docker compose up -d postgres redis
python main.py

# Полный запуск
docker compose up -d

# Просмотр логов
docker compose logs -f bot
```

### Git
```bash
# Просмотр изменений
git diff

# Отмена последнего коммита
git reset --soft HEAD~1

# Создание патча
git format-patch -1 HEAD
```

### Отладка
```bash
# Запуск с отладкой
python -m pdb main.py

# Логирование
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Получение помощи

- **Issues**: для багов и предложений
- **Discussions**: для вопросов и обсуждений
- **Wiki**: для дополнительной документации

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

---

Спасибо за ваш вклад в проект! 🎉 