"""Testes unitários isolados com mocks para o OpenF1Client."""

from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from f1.connectors.openf1_client import OpenF1Client, OpenF1ClientError


@pytest.fixture
def mock_session() -> MagicMock:
    """Fixture com mock de requests.Session."""
    return MagicMock(spec=requests.Session)


def test_fetch_meetings_success(
    mock_session: MagicMock,
    mock_meetings_response: list[dict[str, Any]],
) -> None:
    """Valida consulta bem-sucedida a meetings com parâmetros."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_meetings_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_meetings(year=2023, country_name="Italy")

    assert len(result) == 1
    assert result[0]["meeting_key"] == 1219
    mock_session.get.assert_called_once_with(
        "https://api.openf1.org/v1/meetings",
        params={"year": 2023, "country_name": "Italy"},
        timeout=15,
    )


def test_fetch_sessions_success(
    mock_session: MagicMock,
    mock_sessions_response: list[dict[str, Any]],
) -> None:
    """Valida consulta de sessões com filtros de query string."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_sessions_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_sessions(session_key=9161, year=2023)

    assert len(result) == 2
    mock_session.get.assert_called_once_with(
        "https://api.openf1.org/v1/sessions",
        params={"year": 2023, "session_key": 9161},
        timeout=15,
    )


def test_fetch_drivers_success(
    mock_session: MagicMock,
    mock_drivers_response: list[dict[str, Any]],
) -> None:
    """Valida consulta de pilotos para a sessão."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_drivers_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_drivers(session_key=9161)

    assert len(result) == 2
    assert result[0]["driver_number"] == 1


def test_fetch_laps_success(
    mock_session: MagicMock,
    mock_laps_response: list[dict[str, Any]],
) -> None:
    """Valida consulta de voltas para a sessão."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_laps_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_laps(session_key=9161, driver_number=1)

    assert len(result) == 4
    mock_session.get.assert_called_once_with(
        "https://api.openf1.org/v1/laps",
        params={"session_key": 9161, "driver_number": 1},
        timeout=15,
    )


def test_fetch_car_data_success(
    mock_session: MagicMock,
    mock_car_data_response: list[dict[str, Any]],
) -> None:
    """Valida consulta de telemetria com filtro de velocidade."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_car_data_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_car_data(session_key=9161, driver_number=1, speed_gte=300.0)

    assert len(result) == 3
    mock_session.get.assert_called_once_with(
        "https://api.openf1.org/v1/car_data",
        params={"session_key": 9161, "driver_number": 1, "speed>=": 300.0},
        timeout=15,
    )


def test_fetch_weather_success(
    mock_session: MagicMock,
    mock_weather_response: list[dict[str, Any]],
) -> None:
    """Valida consulta de condições climáticas."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_weather_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_weather(session_key=9161)

    assert len(result) == 1
    assert result[0]["air_temperature"] == 28.5


def test_fetch_session_results_success(
    mock_session: MagicMock,
    mock_session_results_response: list[dict[str, Any]],
) -> None:
    """Valida consulta da classificação final."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_session_results_response
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_session_results(session_key=9161)

    assert len(result) == 2
    assert result[0]["position"] == 1


def test_client_raises_openf1_error_on_http_failure(mock_session: MagicMock) -> None:
    """Garante que falhas HTTP disparem OpenF1ClientError sem vazar requests.RequestException."""
    mock_session.get.side_effect = requests.RequestException("Connection timeout")

    client = OpenF1Client(session=mock_session)
    with pytest.raises(OpenF1ClientError, match="Erro ao consultar OpenF1"):
        client.fetch_sessions(year=2023)


def test_client_handles_unexpected_non_list_response(mock_session: MagicMock) -> None:
    """Garante tratamento elegante caso a API retorne objeto em vez de lista."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": "rate limited"}
    mock_session.get.return_value = mock_response

    client = OpenF1Client(session=mock_session)
    result = client.fetch_sessions(year=2023)
    assert result == []
