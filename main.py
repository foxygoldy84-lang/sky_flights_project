import time

import psycopg2
import requests

# ИМПОРТИРУЕМ НАШ КЛАСС ИЗ ВТОРОГО ФАЙЛА
from db_manager import DBManager

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "Prostoparol",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
}


def fetch_and_save_countries(country_names):
    """Находит координаты стран через Nominatim API и сохраняет их в БД."""
    url = "https://nominatim.openstreetmap.org/search"
    for name in country_names:
        print(f"\n[API] Ищу координаты для страны: {name}...")
        params = {"country": name, "format": "json", "limit": 1}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                continue
            bbox = data[0].get("boundingbox")
            if not bbox or len(bbox) < 4:
                continue

            lat_min, lat_max, lon_min, lon_max = (
                float(bbox[0]),
                float(bbox[1]),
                float(bbox[2]),
                float(bbox[3]),
            )

            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO countries (name, lat_min, lat_max, lon_min, lon_max)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING;
                    """,
                        (name, lat_min, lat_max, lon_min, lon_max),
                    )
                    conn.commit()
            print(f"[БД] Страна {name} успешно сохранена в базу данных!")
        except Exception as e:
            print(f"[Ошибка] Не удалось обработать страну {name}: {e}")
        time.sleep(2.0)


def insert_mock_data():
    """Вспомогательная функция для заполнения базы тестовыми самолетами."""
    print("[Тест] Заполняю базу данных тестовыми самолетами для проверки ТЗ...")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM countries;")
                countries = {name: country_id for country_id, name in cur.fetchall()}
                if countries:
                    cur.execute("TRUNCATE TABLE aeroplanes RESTART IDENTITY;")
                    mock_planes = [
                        (
                            countries.get("Germany"),
                            "1a2b3c",
                            "DLH123",
                            240.5,
                            10000.0,
                        ),
                        (
                            countries.get("Germany"),
                            "4d5e6f",
                            "DLH99A",
                            180.0,
                            7500.0,
                        ),
                        (
                            countries.get("France"),
                            "7g8h9i",
                            "AFR456",
                            250.0,
                            11000.0,
                        ),
                        (
                            countries.get("France"),
                            "0j1k2l",
                            "AFR777",
                            150.2,
                            5000.0,
                        ),
                        (
                            countries.get("Poland"),
                            "3m4n5o",
                            "LOT888",
                            210.3,
                            9000.0,
                        ),
                    ]
                    cur.executemany(
                        """
                        INSERT INTO aeroplanes (country_id, icao24, callsign, velocity, altitude)
                        VALUES (%s, %s, %s, %s, %s);
                    """,
                        mock_planes,
                    )
                    conn.commit()
                    print("[Успех] Тестовые самолеты загружены.")
    except Exception as e:
        print(f"[Ошибка теста] {e}")


# ==========================================
# ГЛАВНЫЙ ЗАПУСК ПРОГРАММЫ
# ==========================================
if __name__ == "__main__":
    # Наполняем базу тестовыми данными
    insert_mock_data()

    # Создаем экземпляр менеджера из импортированного файла db_manager.py
    db_manager = DBManager(DB_CONFIG)

    # 1. Проверяем подсчет самолетов по странам
    print("\n1. Количество самолетов по странам:")
    for country, count in db_manager.get_companies_and_aeroplanes_count():
        print(f"   Страна: {country} — Самолетов в воздухе: {count}")

    # 2. Проверяем вывод всех самолетов
    print("\n2. Список всех самолетов в базе:")
    for plane in db_manager.get_all_aeroplanes():
        print(f"   Позывной: {plane[0]} | Скорость: {plane[1]} м/с | " f"Высота: {plane[2]} м | Страна: {plane[3]}")

    # 3. Проверяем расчет средней скорости
    avg_speed = db_manager.get_avg_velocity()
    print(f"\n3. Средняя скорость всех самолетов: {avg_speed} м/с")

    # 4. Проверяем поиск быстрых самолетов
    print("\n4. Самолеты со скоростью выше средней:")
    for plane in db_manager.get_high_velocity_aeroplanes():
        print(f"   Позывной: {plane[0]} | Скорость: {plane[1]} м/с")

    # 5. Проверяем поиск по ключевому слову
    keyword = "DLH"
    print(f"\n5. Поиск самолетов по ключевому слову '{keyword}':")
    for plane in db_manager.get_aeroplanes_by_keyword(keyword):
        print(f"   Найден позывной: {plane[0]} | Скорость: {plane[1]} м/с")
