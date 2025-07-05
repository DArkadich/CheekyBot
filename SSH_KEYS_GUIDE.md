# 🔑 Руководство по SSH ключам для GitHub Actions

## 📍 Где найти SSH ключи

### Стандартные расположения:
```bash
# macOS/Linux
~/.ssh/id_rsa          # RSA ключ (старый формат)
~/.ssh/id_ed25519      # Ed25519 ключ (рекомендуемый)
~/.ssh/id_ecdsa        # ECDSA ключ

# Windows
C:\Users\YourUsername\.ssh\id_rsa
C:\Users\YourUsername\.ssh\id_ed25519
```

### Проверка существующих ключей:
```bash
ls -la ~/.ssh/
```

## 🔍 Поиск SSH ключа

### 1. Проверка существующих ключей:
```bash
# Показать все файлы в .ssh директории
ls -la ~/.ssh/

# Искать все приватные ключи
find ~/.ssh/ -name "id_*" -type f ! -name "*.pub"
```

### 2. Проверка содержимого ключа:
```bash
# Показать приватный ключ
cat ~/.ssh/id_ed25519

# Показать публичный ключ
cat ~/.ssh/id_ed25519.pub
```

## 🆕 Создание нового SSH ключа

### 1. Создание Ed25519 ключа (рекомендуется):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 2. Создание RSA ключа (если нужна совместимость):
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### 3. Интерактивный процесс:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter file in which to save the key (/Users/username/.ssh/id_ed25519): [Enter]
# Enter passphrase (empty for no passphrase): [Enter для пустой парольной фразы]
# Enter same passphrase again: [Enter]
```

## 🔧 Настройка SSH ключа для сервера

### 1. Копирование публичного ключа на сервер:
```bash
# Автоматическое копирование
ssh-copy-id username@server_ip

# Ручное копирование
cat ~/.ssh/id_ed25519.pub | ssh username@server_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 2. Настройка прав доступа на сервере:
```bash
# Подключение к серверу
ssh username@server_ip

# Настройка прав
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 3. Тестирование подключения:
```bash
ssh username@server_ip
```

## 🔐 Настройка GitHub Actions

### 1. Получение приватного ключа:
```bash
# Скопировать содержимое приватного ключа
cat ~/.ssh/id_ed25519
```

### 2. Добавление секрета в GitHub:
1. Перейдите в ваш репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. New repository secret
4. Name: `KEY`
5. Value: вставьте содержимое приватного ключа

### 3. Другие необходимые секреты:
- `HOST` - IP адрес или домен сервера
- `USERNAME` - имя пользователя на сервере
- `PORT` - SSH порт (обычно 22)

## 🛠 Автоматическая настройка

### Скрипт для настройки SSH:
```bash
#!/bin/bash
# setup-ssh.sh

echo "🔑 Настройка SSH для GitHub Actions..."

# Проверка существования ключа
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "📝 Создание нового SSH ключа..."
    ssh-keygen -t ed25519 -C "github-actions@cheekybot" -f ~/.ssh/id_ed25519 -N ""
else
    echo "✅ SSH ключ уже существует"
fi

# Показать публичный ключ
echo "📋 Публичный ключ (добавьте на сервер):"
cat ~/.ssh/id_ed25519.pub

echo ""
echo "🔐 Приватный ключ (добавьте в GitHub Secrets как KEY):"
cat ~/.ssh/id_ed25519

echo ""
echo "📝 Инструкции:"
echo "1. Скопируйте публичный ключ на сервер: ssh-copy-id username@server_ip"
echo "2. Добавьте приватный ключ в GitHub Secrets как KEY"
echo "3. Добавьте HOST, USERNAME и PORT в GitHub Secrets"
```

## 🔒 Безопасность

### Рекомендации:
1. **Используйте Ed25519** вместо RSA (более безопасный и быстрый)
2. **Не используйте парольную фразу** для GitHub Actions (автоматизация)
3. **Ограничьте права** ключа на сервере
4. **Регулярно ротируйте** ключи
5. **Используйте отдельный ключ** для каждого проекта

### Ограничение доступа на сервере:
```bash
# В ~/.ssh/authorized_keys добавьте ограничения
command="docker-compose up -d",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...
```

## 🚨 Устранение проблем

### Проблема: Permission denied
```bash
# Проверка прав доступа
ls -la ~/.ssh/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Проблема: SSH не работает
```bash
# Тестирование с verbose режимом
ssh -v username@server_ip

# Проверка SSH агента
ssh-add -l
ssh-add ~/.ssh/id_ed25519
```

### Проблема: GitHub Actions не может подключиться
1. Проверьте правильность секретов
2. Убедитесь, что публичный ключ добавлен на сервер
3. Проверьте SSH доступ вручную
4. Проверьте логи GitHub Actions

## 📋 Чек-лист настройки

- [ ] SSH ключ создан (`ssh-keygen -t ed25519`)
- [ ] Публичный ключ добавлен на сервер (`ssh-copy-id`)
- [ ] Приватный ключ добавлен в GitHub Secrets как `KEY`
- [ ] IP сервера добавлен в GitHub Secrets как `HOST`
- [ ] Имя пользователя добавлено в GitHub Secrets как `USERNAME`
- [ ] SSH порт добавлен в GitHub Secrets как `PORT`
- [ ] SSH подключение протестировано вручную
- [ ] GitHub Actions workflow протестирован

## 🔗 Полезные ссылки

- [GitHub SSH Keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [SSH Key Types](https://www.ssh.com/academy/ssh/key)
- [GitHub Actions SSH](https://docs.github.com/en/actions/using-workflows/using-ssh-keys-in-workflows)

---

**SSH ключи настроены и готовы к использованию! 🔑** 