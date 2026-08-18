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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
}


def fetch_and_save_countries(country_names):
    """Находит координаты стран через Nominatim API и сохраняет их в БД."""
    url = "https://openstreetmap.org"
    for name in country_names:
        print(f"\n[API] Ищу координаты для страны: {name}...")
        params = {"country": name, "format": "json", "limit": 1}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                continue
            bbox = data.get("boundingbox")
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
                        # 1. Германия
                        (countries.get("Germany"), "1a2b3c", "DLH123", 240.5, 10000.0),
                        (countries.get("Germany"), "4d5e6f", "DLH99A", 180.0, 7500.0),
                        # 2. Франция
                        (countries.get("France"), "7g8h9i", "AFR456", 250.0, 11000.0),
                        (countries.get("France"), "0j1k2l", "AFR777", 150.2, 5000.0),
                        # 3. Польша
                        (countries.get("Poland"), "3m4n5o", "LOT888", 210.3, 9000.0),
                        # 4. Испания
                        (countries.get("Spain"), "6p7q8r", "IBE321", 225.0, 9500.0),
                        # 5. Италия
                        (countries.get("Italy"), "9s0t1u", "ITY444", 230.1, 10200.0),
                        # 6. Великобритания
                        (countries.get("United Kingdom"), "2v3w4x", "BAW555", 245.4, 10800.0),
                        # 7. Нидерланды
                        (countries.get("Netherlands"), "5y6z7a", "KLM789", 235.0, 9900.0),
                        # 8. Бельгия
                        (countries.get("Belgium"), "8b9c0d", "BEL111", 195.2, 8000.0),
                        # 9. Австрия
                        (countries.get("Austria"), "1e2f3g", "AUA222", 215.8, 8800.0),
                        # 10. Швейцария
                        (countries.get("Switzerland"), "4h5i6j", "SWR333", 220.0, 9200.0),
                    ]
                    cur.executemany(
                        """
                        INSERT INTO aeroplanes (country_id, icao24, callsign, velocity, altitude)
                        VALUES (%s, %s, %s, %s, %s);
                    """,
                        mock_planes,
                    )
                    conn.commit()
                    print("[Успех] Тестовые самолеты для 10 стран загружены.")
    except Exception as e:
        print(f"[Ошибка теста] {e}")


# ==========================================
# ГЛАВНЫЙ ЗАПУСК ПРОГРАММЫ
# ==========================================
if __name__ == "__main__":
    # Список из 10 стран для соответствия критериям
    list_of_countries = [
        "Germany",
        "France",
        "Poland",
        "Spain",
        "Italy",
        "United Kingdom",
        "Netherlands",
        "Belgium",
        "Austria",
        "Switzerland",
    ]

    # Запускаем сбор 10 стран через API (если база пустая, один раз отработает)
    # fetch_and_save_countries(list_of_countries)

    # Наполняем базу тестовыми данными по 10 странам
    insert_mock_data()

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
    print("\n4. Самолеты со сокростью выше средней:")
    for plane in db_manager.get_high_velocity_aeroplanes():
        print(f"   Позывной: {plane[0]} | Скорость: {plane[1]} м/с")

    # 5. Проверяем поиск по ключевому слову
    keyword = "DLH"
    print(f"\n5. Поиск самолетов по ключевому слову '{keyword}':")
    for plane in db_manager.get_aeroplanes_by_keyword(keyword):
        print(f"   Найден позывной: {plane[0]} | Скорость: {plane[1]} м/с")
