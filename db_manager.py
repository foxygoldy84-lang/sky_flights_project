"""Модуль менеджера базы данных для аналитики авиационной активности."""

import psycopg2


class DBManager:
    """Класс для взаимодействия с базой данных PostgreSQL.

    Предоставляет методы аналитики, фильтрации и подсчета данных
    о странах и воздушных судах в соответствии с техническим заданием.
    """

    def __init__(self, db_config: dict):
        """Инициализирует менеджер базы данных.

        :param db_config: Словарь с параметрами подключения к PostgreSQL.
        """
        self.db_config = db_config

    def get_companies_and_aeroplanes_count(self):
        """1. Получает список всех стран и количество самолетов в каждой из них."""
        query = """
            SELECT c.name, COUNT(a.id)
            FROM countries c
            LEFT JOIN aeroplanes a ON c.id = a.country_id
            GROUP BY c.name;
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_all_aeroplanes(self):
        """2. Получает список всех самолетов.

        Возвращает название страны, позывной, скорость и высоту для каждого судна.
        """
        query = """
            SELECT c.name, a.callsign, a.velocity, a.altitude
            FROM aeroplanes a
            JOIN countries c ON a.country_id = c.id;
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_avg_velocity(self):
        """3. Получает среднюю скорость всех самолетов."""
        query = "SELECT AVG(velocity) FROM aeroplanes;"
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                res = cur.fetchone()
                # Перестраховка: если в базе нет самолетов, AVG вернет None
                return round(res[0], 2) if res and res[0] is not None else 0.0

    def get_high_velocity_aeroplanes(self):
        """4. Получает список самолетов, скорость которых выше средней."""
        query = """
            SELECT callsign, velocity, altitude
            FROM aeroplanes
            WHERE velocity > (SELECT AVG(velocity) FROM aeroplanes);
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_aeroplanes_by_keyword(self, keyword: str):
        """5. Получает список всех самолетов, содержащих переданное слово в позывном."""
        query = """
            SELECT callsign, velocity, altitude
            FROM aeroplanes
            WHERE callsign ILIKE %s;
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (f"%{keyword}%",))
                return cur.fetchall()
