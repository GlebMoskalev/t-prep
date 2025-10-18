#!/bin/bash

# Скрипт для настройки SSL сертификата Let's Encrypt

set -e

echo "🔒 Настройка SSL сертификата Let's Encrypt..."

# Проверяем, что домен указан
if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажите домен"
    echo "Использование: $0 your-domain.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Настраиваем SSL для домена: $DOMAIN"

# Создаем временную конфигурацию Nginx для получения сертификата
echo "📝 Создаем временную конфигурацию Nginx..."
sudo tee /etc/nginx/sites-available/t-prep-temp << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF

# Создаем директорию для certbot
sudo mkdir -p /var/www/certbot

# Активируем временную конфигурацию
sudo ln -sf /etc/nginx/sites-available/t-prep-temp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/t-prep
sudo nginx -t
sudo systemctl reload nginx

# Получаем SSL сертификат
echo "🔐 Получаем SSL сертификат..."
sudo certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN

# Обновляем конфигурацию Nginx с SSL
echo "⚙️  Обновляем конфигурацию Nginx с SSL..."
sudo sed -i "s/your-domain.com/$DOMAIN/g" /opt/t-prep/nginx.prod.conf
sudo cp /opt/t-prep/nginx.prod.conf /etc/nginx/sites-available/t-prep

# Активируем финальную конфигурацию
sudo rm -f /etc/nginx/sites-enabled/t-prep-temp
sudo ln -sf /etc/nginx/sites-available/t-prep /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Настраиваем автообновление сертификатов
echo "🔄 Настраиваем автообновление сертификатов..."
sudo tee /etc/cron.d/certbot << EOF
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

echo "✅ SSL сертификат настроен успешно!"
echo "🌐 Ваш сайт доступен по адресу: https://$DOMAIN"
echo "📋 Сертификат будет автоматически обновляться каждые 12 часов"
