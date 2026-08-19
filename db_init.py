import psycopg2

from config import DB_CONFIG


def init_database():
    """Создает таблицы countries и aeroplanes, если они отсутствуют в БД."""
    print("[БД] Проверка и создание структуры таблиц...")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # 1. Создаем таблицу стран
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS countries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        lat_min DOUBLE PRECISION,
                        lat_max DOUBLE PRECISION,
                        lon_min DOUBLE PRECISION,
                        lon_max DOUBLE PRECISION
                    );
                """)

                # 2. Создаем таблицу самолетов (со связью CASCADE)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aeroplanes (
                        id SERIAL PRIMARY KEY,
                        country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
                        icao24 VARCHAR(50),
                        callsign VARCHAR(50),
                        velocity DOUBLE PRECISION,
                        altitude DOUBLE PRECISION
                    );
                """)

                conn.commit()
                print("[БД] Структура таблиц успешно инициализирована!")
    except Exception as e:
        print(f"[БД] КРИТИЧЕСКАЯ ОШИБКА инициализации: {e}")
        raise e
