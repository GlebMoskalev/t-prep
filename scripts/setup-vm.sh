#!/bin/bash

# Скрипт для первоначальной настройки Ubuntu VM для T-Prep

set -e

echo "🚀 Начинаем настройку Ubuntu VM для T-Prep..."

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем необходимые пакеты..."
sudo apt install -y \
    curl \
    wget \
    git \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    nano \
    ufw \
    fail2ban

# Настраиваем Docker
echo "🐳 Настраиваем Docker..."
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Создаем директорию для проекта
echo "📁 Создаем директорию проекта..."
sudo mkdir -p /opt/t-prep
sudo chown $USER:$USER /opt/t-prep

# Клонируем репозиторий (замените на ваш URL)
echo "📥 Клонируем репозиторий..."
cd /opt/t-prep
if [ ! -d ".git" ]; then
    echo "Введите URL вашего GitHub репозитория:"
    read REPO_URL
    git clone $REPO_URL .
fi

# Создаем .env файл
echo "⚙️  Создаем .env файл..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "⚠️  ВНИМАНИЕ: Создан .env файл из env.example"
    echo "   Не забудьте настроить переменные окружения!"
    echo "   При деплое через GitHub Actions .env будет создан автоматически из GitHub Secrets"
fi

# Настраиваем Nginx
echo "🌐 Настраиваем Nginx..."
sudo tee /etc/nginx/sites-available/t-prep << EOF
server {
    listen 80;
    server_name _;  # Замените на ваш домен
    
    # Редирект на HTTPS (раскомментируйте после настройки SSL)
    # return 301 https://\$server_name\$request_uri;
    
    # Проксирование на FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Статические файлы
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }
}
EOF

# Активируем конфигурацию Nginx
sudo ln -sf /etc/nginx/sites-available/t-prep /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Настраиваем файрвол
echo "🔥 Настраиваем файрвол..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Настраиваем fail2ban
echo "🛡️  Настраиваем fail2ban..."
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Создаем systemd сервис для автозапуска
echo "🔄 Создаем systemd сервис..."
sudo tee /etc/systemd/system/t-prep.service << EOF
[Unit]
Description=T-Prep Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/t-prep
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable t-prep

# Создаем скрипт для обновления
echo "📝 Создаем скрипт для обновления..."
tee /opt/t-prep/update.sh << EOF
#!/bin/bash
cd /opt/t-prep
git pull origin main || git pull origin master
docker compose pull
docker compose build --no-cache
docker compose down
docker compose up -d
echo "✅ Обновление завершено!"
EOF

chmod +x /opt/t-prep/update.sh

# Запускаем приложение
echo "🚀 Запускаем приложение..."
cd /opt/t-prep
docker compose up -d

# Ждем запуска
sleep 10

# Проверяем статус
echo "📊 Проверяем статус..."
docker compose ps
curl -f http://localhost:8000/health || echo "⚠️  API не отвечает"

echo "✅ Настройка VM завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте переменные окружения в /opt/t-prep/.env"
echo "2. Настройте домен в /etc/nginx/sites-available/t-prep"
echo "3. Получите SSL сертификат: sudo certbot --nginx"
echo "4. Добавьте SSH ключи в GitHub Secrets"
echo ""
echo "🔑 Для добавления SSH ключей в GitHub:"
echo "1. Сгенерируйте SSH ключ: ssh-keygen -t ed25519 -C 'github-actions'"
echo "2. Добавьте публичный ключ в authorized_keys на VM"
echo "3. Добавьте приватный ключ в GitHub Secrets как VM_SSH_KEY"
echo ""
echo "🌐 Для настройки SSL:"
echo "sudo certbot --nginx -d your-domain.com"
