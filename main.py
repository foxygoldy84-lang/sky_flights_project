"""Главный модуль запуска программы авиамониторинга."""

from api_clients import fetch_and_save_aeroplanes, fetch_and_save_countries
from config import DB_CONFIG, LIST_OF_COUNTRIES
from db_init import init_database
from db_manager import DBManager


def main():
    """Основной сценарий выполнения программы."""
    print("=== ЗАПУСК СИСТЕМЫ АВИАМОНИТОРИНГА ===\n")

    # 1. Автоматически проверяем и создаем таблицы в PostgreSQL
    init_database()

    # 2. Собираем реальные координаты 10 стран через Nominatim API
    fetch_and_save_countries(LIST_OF_COUNTRIES)

    # 3. Собираем реальные самолеты в воздухе через OpenSky API
    fetch_and_save_aeroplanes()

    # 4. Инициализируем менеджер аналитики
    db_manager = DBManager(DB_CONFIG)

    # 5. Выводим результаты аналитики
    print("\n=== РЕЗУЛЬТАТЫ АНАЛИТИКИ ===")

    print("\n1. Количество самолетов по странам:")
    for country, count in db_manager.get_companies_and_aeroplanes_count():
        print(f"   Страна: {country} — Самолётов в воздухе: {count}")

    print("\n2. Список всех самолетов в базе данных:")
    for plane in db_manager.get_all_aeroplanes():
        print(f"   Страна: {plane[0]} | Позывной: {plane[1]} | " f"Скорость: {plane[2]} м/с | Высота: {plane[3]} м")

    avg_speed = db_manager.get_avg_velocity()
    print(f"\n3. Средняя скорость всех самолетов: {avg_speed} м/с")

    print("\n4. Самолеты со скоростью выше средней:")
    for plane in db_manager.get_high_velocity_aeroplanes():
        print(f"   Позывной: {plane[0]} | Скорость: {plane[1]} м/с")

    keyword = "DLH"  # Поиск немецких рейсов Lufthansa
    print(f"\n5. Поиск самолетов по ключевому слову '{keyword}':")
    for plane in db_manager.get_aeroplanes_by_keyword(keyword):
        print(f"   Найден позывной: {plane[0]} | Скорость: {plane[1]} м/с")

    print("\n=== ПРОГРАММА УСПЕШНО ЗАВЕРШЕНА ===")


if __name__ == "__main__":
    main()
