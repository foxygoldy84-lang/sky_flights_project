import psycopg2


class DBManager:

    def __init__(self, db_config):
        self.db_config = db_config

    def get_companies_and_aeroplanes_count(self):
        """1. Получает список всех стран и количество самолетов в каждой."""
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
        """2. Получает список всех самолетов с указанием названия страны."""
        query = """
            SELECT a.callsign, a.velocity, a.altitude, c.name
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
                res = cur.fetchone()[0]
                return round(res, 2) if res is not None else 0.0

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

    def get_aeroplanes_by_keyword(self, keyword):
        """5. Получает список всех самолетов по ключевому слову."""
        query = """
            SELECT callsign, velocity, altitude
            FROM aeroplanes
            WHERE callsign ILIKE %s;
        """
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (f"%{keyword}%",))
                return cur.fetchall()
