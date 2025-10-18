#!/bin/bash

# Скрипт для валидации GitHub Secrets перед деплоем

set -e

echo "🔍 Валидация GitHub Secrets..."

# Список обязательных секретов
REQUIRED_SECRETS=(
    "VM_HOST"
    "VM_USERNAME" 
    "VM_SSH_KEY"
    "VM_PORT"
    "DATABASE_URL"
    "POSTGRES_PASSWORD"
    "SECRET_KEY"
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "GOOGLE_REDIRECT_URI"
    "ANDROID_CLIENT_ID"
    "ALLOWED_ORIGINS"
)

# Список опциональных секретов с значениями по умолчанию
OPTIONAL_SECRETS=(
    "ALGORITHM:HS256"
    "ACCESS_TOKEN_EXPIRE_MINUTES:30"
    "REFRESH_TOKEN_EXPIRE_DAYS:7"
    "DEBUG:False"
    "LOG_LEVEL:INFO"
)

echo "📋 Проверяем обязательные секреты..."

# Проверяем обязательные секреты
MISSING_SECRETS=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if [ -z "${!secret}" ]; then
        MISSING_SECRETS+=("$secret")
    else
        echo "✅ $secret - OK"
    fi
done

# Проверяем опциональные секреты
echo ""
echo "📋 Проверяем опциональные секреты..."
for secret_default in "${OPTIONAL_SECRETS[@]}"; do
    secret="${secret_default%:*}"
    default="${secret_default#*:}"
    
    if [ -z "${!secret}" ]; then
        echo "⚠️  $secret - отсутствует, будет использовано значение по умолчанию: $default"
    else
        echo "✅ $secret - OK"
    fi
done

# Проверяем формат значений
echo ""
echo "🔍 Проверяем формат значений..."

# Проверяем DATABASE_URL
if [[ ! "$DATABASE_URL" =~ ^postgresql:// ]]; then
    echo "❌ DATABASE_URL должен начинаться с 'postgresql://'"
    exit 1
fi

# Проверяем GOOGLE_REDIRECT_URI
if [[ ! "$GOOGLE_REDIRECT_URI" =~ ^https?:// ]]; then
    echo "❌ GOOGLE_REDIRECT_URI должен быть валидным URL"
    exit 1
fi

# Проверяем SECRET_KEY
if [ ${#SECRET_KEY} -lt 32 ]; then
    echo "❌ SECRET_KEY должен быть длиннее 32 символов"
    exit 1
fi

# Проверяем POSTGRES_PASSWORD
if [ ${#POSTGRES_PASSWORD} -lt 12 ]; then
    echo "❌ POSTGRES_PASSWORD должен быть длиннее 12 символов"
    exit 1
fi

# Проверяем VM_PORT
if ! [[ "$VM_PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ VM_PORT должен быть числом"
    exit 1
fi

# Проверяем ALLOWED_ORIGINS
if [[ "$ALLOWED_ORIGINS" == *"*"* ]] && [[ "$ALLOWED_ORIGINS" != "*" ]]; then
    echo "❌ ALLOWED_ORIGINS не должен содержать '*' вместе с другими доменами"
    exit 1
fi

# Выводим результат
echo ""
if [ ${#MISSING_SECRETS[@]} -eq 0 ]; then
    echo "🎉 Все обязательные секреты настроены правильно!"
    echo "✅ Валидация прошла успешно"
    exit 0
else
    echo "❌ Обнаружены отсутствующие секреты:"
    for secret in "${MISSING_SECRETS[@]}"; do
        echo "   - $secret"
    done
    echo ""
    echo "📝 Добавьте отсутствующие секреты в GitHub:"
    echo "   Settings → Secrets and variables → Actions"
    exit 1
fi
