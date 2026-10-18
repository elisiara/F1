"""Testes unitários para contratos e modelos de domínio."""

from typing import Any

from f1.domain.models import (
    Driver,
    Lap,
    Meeting,
    Session,
    SessionResult,
    TelemetrySample,
    WeatherSample,
)


def test_meeting_from_dict(mock_meetings_response: list[dict[str, Any]]) -> None:
    """Valida instanciação e serialização de Meeting."""
    raw = mock_meetings_response[0]
    meeting = Meeting.from_dict(raw)
    assert meeting.meeting_key == 1219
    assert meeting.year == 2023
    assert meeting.country_name == "Italy"
    assert meeting.circuit_short_name == "Monza"
    assert meeting.to_dict()["meeting_key"] == 1219


def test_session_from_dict(mock_sessions_response: list[dict[str, Any]]) -> None:
    """Valida instanciação e serialização de Session."""
    raw = mock_sessions_response[1]
    session = Session.from_dict(raw)
    assert session.session_key == 9161
    assert session.session_name == "Race"
    assert session.session_type == "Race"
    assert session.to_dict()["session_key"] == 9161


def test_driver_from_dict(mock_drivers_response: list[dict[str, Any]]) -> None:
    """Valida instanciação e campos do Driver."""
    raw = mock_drivers_response[0]
    driver = Driver.from_dict(raw)
    assert driver.driver_number == 1
    assert driver.name_acronym == "VER"
    assert driver.team_name == "Red Bull Racing"
    assert driver.to_dict()["driver_number"] == 1


def test_lap_from_dict(mock_laps_response: list[dict[str, Any]]) -> None:
    """Valida instanciação da Lap com tempos parciais e conversão de tipos."""
    raw = mock_laps_response[1]
    lap = Lap.from_dict(raw)
    assert lap.session_key == 9161
    assert lap.driver_number == 1
    assert lap.lap_number == 2
    assert lap.lap_duration == 85.073
    assert not lap.is_pit_out_lap
    assert lap.to_dict()["lap_duration"] == 85.073


def test_telemetry_sample_from_dict(
    mock_car_data_response: list[dict[str, Any]],
) -> None:
    """Valida instanciação da TelemetrySample e precisão numérica."""
    raw = mock_car_data_response[0]
    sample = TelemetrySample.from_dict(raw)
    assert sample.speed == 315.0
    assert sample.rpm == 11450
    assert sample.n_gear == 7
    assert sample.throttle == 100.0
    assert sample.drs == 12
    assert sample.to_dict()["speed"] == 315.0


def test_weather_sample_from_dict(mock_weather_response: list[dict[str, Any]]) -> None:
    """Valida instanciação da WeatherSample."""
    raw = mock_weather_response[0]
    weather = WeatherSample.from_dict(raw)
    assert weather.air_temperature == 28.5
    assert weather.track_temperature == 42.1
    assert weather.rainfall == 0
    assert weather.to_dict()["rainfall"] == 0


def test_session_result_from_dict(
    mock_session_results_response: list[dict[str, Any]],
) -> None:
    """Valida instanciação de SessionResult."""
    raw = mock_session_results_response[0]
    result = SessionResult.from_dict(raw)
    assert result.position == 1
    assert result.driver_number == 1
    assert not result.dnf
    assert result.to_dict()["position"] == 1
