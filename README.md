# T-Prep Backend

Backend API для приложения T-Prep - системы подготовки к экзаменам с использованием методики интервальных повторений.

## Возможности

- 🔐 Авторизация через Google OAuth 2.0
- 🎫 JWT токены для аутентификации
- 📚 Управление модулями и карточками
- 🧠 Алгоритм интервальных повторений (SFRS)
- 🐳 Docker контейнеризация
- 📊 PostgreSQL база данных

## Архитектура

```
app/
├── api/                    # API endpoints
│   ├── v1/                # API версии 1
│   └── endpoints/         # Отдельные endpoints
├── core/                  # Основная конфигурация
│   ├── config.py         # Настройки приложения
│   ├── security.py       # JWT и безопасность
│   └── deps.py           # Зависимости
├── db/                    # База данных
│   └── database.py       # Подключение к БД
├── models/                # SQLAlchemy модели
│   ├── user.py           # Модель пользователя
│   ├── module.py         # Модель модуля
│   ├── card.py           # Модель карточки
│   ├── interval_repetition.py  # Интервальные повторения
│   └── module_access.py  # Права доступа
├── schemas/               # Pydantic схемы
├── services/              # Бизнес-логика
│   ├── auth_service.py   # Сервис авторизации
│   └── google_oauth_service.py  # Google OAuth
└── utils/                 # Утилиты
```

## Установка и запуск

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd t-prep
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `env.example`:
```bash
cp env.example .env
```

5. Настройте переменные окружения в `.env`:
```env
DATABASE_URL=postgresql://tprep_user:tprep_password@localhost:5432/tprep_db
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

6. Запустите приложение:
```bash
uvicorn main:app --reload
```

### Docker

1. Запустите все сервисы:
```bash
docker-compose up -d
```

2. Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### Авторизация
- `GET /api/v1/auth/google` - Получить URL для Google OAuth
- `POST /api/v1/auth/google/callback` - Обработка callback от Google
- `GET /api/v1/auth/me` - Получить информацию о текущем пользователе
- `POST /api/v1/auth/logout` - Выход из системы

### Модули
- `GET /api/v1/modules/` - Получить все модули пользователя
- `POST /api/v1/modules/` - Создать новый модуль
- `GET /api/v1/modules/{module_id}` - Получить модуль по ID
- `PUT /api/v1/modules/{module_id}` - Обновить модуль
- `DELETE /api/v1/modules/{module_id}` - Удалить модуль

### Карточки
- `GET /api/v1/cards/module/{module_id}` - Получить карточки модуля
- `POST /api/v1/cards/` - Создать новую карточку
- `GET /api/v1/cards/{card_id}` - Получить карточку по ID
- `PUT /api/v1/cards/{card_id}` - Обновить карточку
- `DELETE /api/v1/cards/{card_id}` - Удалить карточку

### Пользователи
- `GET /api/v1/users/me` - Получить профиль пользователя
- `PUT /api/v1/users/me` - Обновить профиль пользователя

## Настройка Google OAuth

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API
4. Создайте OAuth 2.0 credentials
5. Добавьте redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
6. Скопируйте Client ID и Client Secret в файл `.env`

## Структура базы данных

### Таблицы:
- `users` - Пользователи системы
- `modules` - Модули (наборы карточек)
- `cards` - Карточки для изучения
- `interval_repetitions` - Интервальные повторения
- `module_accesses` - Права доступа к модулям

## Разработка

### Добавление новых endpoints:
1. Создайте схему в `app/schemas/`
2. Добавьте endpoint в `app/api/endpoints/`
3. Зарегистрируйте в `app/api/v1/api.py`

### Миграции базы данных:
```bash
# Создать миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head
```
