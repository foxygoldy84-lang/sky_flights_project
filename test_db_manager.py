from unittest.mock import MagicMock
import pytest
from db_manager import DBManager


@pytest.fixture
def mock_db_manager():
    """Фикстура для создания объекта DBManager с поддельным подключением к БД."""
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "test",
        "user": "test",
        "password": "test",
    }
    return DBManager(db_config)


def test_get_avg_velocity(mock_db_manager, monkeypatch):
    """Тест метода расчета средней скорости с данными."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (250.5,)

    mock_connect = MagicMock()
    mock_connect.__enter__.return_value = mock_connect
    mock_connect.cursor.return_value.__enter__.return_value = mock_cursor

    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: mock_connect)

    result = mock_db_manager.get_avg_velocity()

    assert result == 250.5
    mock_cursor.execute.assert_called_once_with(
        "SELECT AVG(velocity) FROM aeroplanes;"
    )


def test_get_avg_velocity_empty(mock_db_manager, monkeypatch):
    """Тест метода расчета средней скорости, если база данных пуста."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (None,)

    mock_connect = MagicMock()
    mock_connect.__enter__.return_value = mock_connect
    mock_connect.cursor.return_value.__enter__.return_value = mock_cursor

    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: mock_connect)

    result = mock_db_manager.get_avg_velocity()

    # Наш код в менеджере должен перестраховаться и вернуть 0.0 вместо None
    assert result == 0.0


def test_get_aeroplanes_by_keyword(mock_db_manager, monkeypatch):
    """Тест поиска самолетов по ключевому слову."""
    mock_cursor = MagicMock()
    # Имитируем, что база нашла один самолет по запросу
    mock_cursor.fetchall.return_value = [("DLH123", 240.5, 10000.0)]

    mock_connect = MagicMock()
    mock_connect.__enter__.return_value = mock_connect
    mock_connect.cursor.return_value.__enter__.return_value = mock_cursor

    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: mock_connect)

    result = mock_db_manager.get_aeroplanes_by_keyword("DLH")

    assert len(result) == 1
    assert result == [("DLH123", 240.5, 10000.0)]
    mock_cursor.execute.assert_called_once()
