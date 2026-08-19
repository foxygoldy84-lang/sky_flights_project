import time

import psycopg2
import requests

from config import DB_CONFIG, HEADERS


def fetch_and_save_countries(country_names):
    """Находит координаты границ стран через Nominatim API и сохраняет их в БД.

    :param country_names: Список названий стран для поиска.
    """
    url = "https://openstreetmap.org"
    for name in country_names:
        print(f"[API Nominatim] Запрашиваю координаты для: {name}...")
        params = {"country": name, "format": "json", "limit": 1}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                print(f"[API Nominatim] Страна '{name}' не найдена.")
                continue

            bbox = data[0].get("boundingbox")
            if not bbox or len(bbox) < 4:
                print(f"[API Nominatim] Не удалось получить границы для '{name}'.")
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
            print(f"[БД] Координаты страны {name} сохранены.")
        except Exception as e:
            print(f"[API Nominatim] Ошибка обработки страны {name}: {e}")

        # Обязательная пауза, чтобы Nominatim не заблокировал за частые запросы
        time.sleep(1.5)


def fetch_and_save_aeroplanes():
    """Читает координаты из БД, запрашивает самолеты через OpenSky API и сохраняет их."""
    opensky_url = "https://opensky-network.org"

    # Шаг 1: Достаем страны и их сохраненные границы из базы данных
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, lat_min, lat_max, lon_min, lon_max FROM countries;")
                countries = cur.fetchall()
    except Exception as e:
        print(f"[БД] Не удалось прочитать список стран: {e}")
        return

    if not countries:
        print("[Предупреждение] В таблице countries пусто. Сначала соберите страны!")
        return

    # Шаг 2: Обходим каждую страну и делаем реальный запрос к OpenSky
    for country in countries:
        country_id, country_name, lat_min, lat_max, lon_min, lon_max = country
        print(f"\n[API OpenSky] Ищу самолеты в воздухе над: {country_name}...")

        params = {"lamin": lat_min, "lamax": lat_max, "lomin": lon_min, "lomax": lon_max}

        try:
            response = requests.get(opensky_url, params=params, headers=HEADERS, timeout=15)

            if response.status_code == 404:
                print(f"[API OpenSky] Активных самолетов над {country_name} сейчас нет.")
                continue

            response.raise_for_status()
            data = response.json()

            states = data.get("states")
            if not states:
                print(f"[API OpenSky] Свободное небо над {country_name}.")
                continue

            print(f"[API OpenSky] Обнаружено судов: {len(states)}. Запись в PostgreSQL...")

            # Шаг 3: Сохраняем пойманные самолеты в базу данных
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    for state in states:
                        icao24 = state[0]
                        callsign = state[1].strip() if state[1] else None
                        velocity = state[9]  # Скорость в м/с из структуры ответа OpenSky
                        altitude = state[7]  # Геометрическая высота в метрах

                        cur.execute(
                            """
                            INSERT INTO aeroplanes (country_id, icao24, callsign, velocity, altitude)
                            VALUES (%s, %s, %s, %s, %s);
                        """,
                            (country_id, icao24, callsign, velocity, altitude),
                        )

                    conn.commit()
            print(f"[БД] Самолеты для {country_name} успешно занесены в базу.")

        except Exception as e:
            print(f"[API OpenSky] Сервер OpenSky временно недоступен или отклонил запрос: {e}")

        # Пауза между запросами к серверам авиамониторинга
        time.sleep(2.0)
