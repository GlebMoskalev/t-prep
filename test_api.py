#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API T-Prep
Запустите сервер перед использованием этого скрипта
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class TPrepAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
    
    def test_health(self):
        """Тест health check endpoint"""
        print("🔍 Тестируем health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check пройден")
                print(f"   Ответ: {response.json()}")
            else:
                print(f"❌ Health check не прошел: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка при health check: {e}")
    
    def test_google_auth_url(self):
        """Тест получения Google OAuth URL"""
        print("\n🔍 Тестируем получение Google OAuth URL...")
        try:
            response = self.session.get(f"{API_BASE}/auth/google")
            if response.status_code == 200:
                print("✅ Google OAuth URL получен")
                auth_data = response.json()
                print(f"   URL: {auth_data.get('auth_url', 'Не найден')}")
            else:
                print(f"❌ Не удалось получить OAuth URL: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка при получении OAuth URL: {e}")
    
    def test_android_auth(self, id_token: str):
        """Тест Android авторизации"""
        print(f"\n🔍 Тестируем Android авторизацию...")
        try:
            response = self.session.post(
                f"{API_BASE}/auth/google/android",
                params={"id_token": id_token}
            )
            if response.status_code == 200:
                print("✅ Android авторизация прошла успешно")
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                print(f"   Токен получен: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Android авторизация не прошла: {response.status_code}")
                print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка при Android авторизации: {e}")
        return False
    
    def test_user_info(self):
        """Тест получения информации о пользователе"""
        if not self.token:
            print("\n⚠️  Пропускаем тест информации о пользователе (нет токена)")
            return
        
        print("\n🔍 Тестируем получение информации о пользователе...")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            if response.status_code == 200:
                print("✅ Информация о пользователе получена")
                user_data = response.json()
                print(f"   Имя: {user_data.get('name', 'Не указано')}")
                print(f"   Email: {user_data.get('email', 'Не указан')}")
            else:
                print(f"❌ Не удалось получить информацию о пользователе: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка при получении информации о пользователе: {e}")
    
    def test_modules(self):
        """Тест работы с модулями"""
        if not self.token:
            print("\n⚠️  Пропускаем тест модулей (нет токена)")
            return
        
        print("\n🔍 Тестируем работу с модулями...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Создание модуля
        try:
            module_data = {
                "name": "Тестовый модуль",
                "description": "Модуль для тестирования API"
            }
            response = self.session.post(
                f"{API_BASE}/modules/",
                json=module_data,
                headers=headers
            )
            if response.status_code == 200:
                print("✅ Модуль создан успешно")
                module = response.json()
                module_id = module.get("id")
                print(f"   ID модуля: {module_id}")
                
                # Получение модулей
                response = self.session.get(f"{API_BASE}/modules/", headers=headers)
                if response.status_code == 200:
                    print("✅ Список модулей получен")
                    modules = response.json()
                    print(f"   Количество модулей: {len(modules)}")
                
                return module_id
            else:
                print(f"❌ Не удалось создать модуль: {response.status_code}")
                print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка при работе с модулями: {e}")
        return None
    
    def test_cards(self, module_id: int):
        """Тест работы с карточками"""
        if not self.token or not module_id:
            print("\n⚠️  Пропускаем тест карточек (нет токена или module_id)")
            return
        
        print(f"\n🔍 Тестируем работу с карточками (модуль {module_id})...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Создание карточки
            card_data = {
                "question": "Что такое FastAPI?",
                "answer": "FastAPI - это современный веб-фреймворк для создания API на Python",
                "module_id": module_id
            }
            response = self.session.post(
                f"{API_BASE}/cards/",
                json=card_data,
                headers=headers
            )
            if response.status_code == 200:
                print("✅ Карточка создана успешно")
                card = response.json()
                card_id = card.get("id")
                print(f"   ID карточки: {card_id}")
                
                # Получение карточек модуля
                response = self.session.get(
                    f"{API_BASE}/cards/module/{module_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    print("✅ Список карточек получен")
                    cards = response.json()
                    print(f"   Количество карточек: {len(cards)}")
            else:
                print(f"❌ Не удалось создать карточку: {response.status_code}")
                print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка при работе с карточками: {e}")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования T-Prep API")
    print("=" * 50)
    
    tester = TPrepAPITester()
    
    # Базовые тесты
    tester.test_health()
    tester.test_google_auth_url()
    
    # Тест Android авторизации (нужен реальный ID токен)
    print("\n" + "=" * 50)
    print("📱 Для тестирования Android авторизации:")
    print("1. Получите ID токен из Google Sign-In в Android приложении")
    print("2. Запустите: python test_api.py <id_token>")
    print("=" * 50)
    
    import sys
    if len(sys.argv) > 1:
        id_token = sys.argv[1]
        if tester.test_android_auth(id_token):
            tester.test_user_info()
            module_id = tester.test_modules()
            if module_id:
                tester.test_cards(module_id)
    else:
        print("\n💡 Для полного тестирования с авторизацией:")
        print("   python test_api.py <google_id_token>")

if __name__ == "__main__":
    main()
