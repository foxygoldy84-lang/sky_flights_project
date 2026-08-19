"""Модуль конфигурации проекта."""

# Настройки подключения к PostgreSQL.
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "Prostoparol",
}

# Список из 10 стран
LIST_OF_COUNTRIES = [
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

# Общие заголовки для работы с API
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
}
