"""Fixtures globais e dados sintéticos para a suíte de testes com Pytest."""

from typing import Any

import pytest


@pytest.fixture
def mock_meetings_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/meetings."""
    return [
        {
            "meeting_key": 1219,
            "meeting_name": "Italian Grand Prix",
            "meeting_official_name": "FORMULA 1 PIRELLI GRAN PREMIO D'ITALIA 2023",
            "year": 2023,
            "location": "Monza",
            "country_name": "Italy",
            "country_code": "ITA",
            "circuit_key": 39,
            "circuit_short_name": "Monza",
            "date_start": "2023-09-01T11:30:00+00:00",
            "date_end": "2023-09-03T15:00:00+00:00",
            "gmt_offset": "+02:00",
        }
    ]


@pytest.fixture
def mock_sessions_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/sessions."""
    return [
        {
            "session_key": 9158,
            "meeting_key": 1219,
            "session_name": "Practice 1",
            "session_type": "Practice",
            "year": 2023,
            "date_start": "2023-09-01T11:30:00+00:00",
            "date_end": "2023-09-01T12:30:00+00:00",
            "gmt_offset": "+02:00",
            "location": "Monza",
            "circuit_key": 39,
        },
        {
            "session_key": 9161,
            "meeting_key": 1219,
            "session_name": "Race",
            "session_type": "Race",
            "year": 2023,
            "date_start": "2023-09-03T13:00:00+00:00",
            "date_end": "2023-09-03T15:00:00+00:00",
            "gmt_offset": "+02:00",
            "location": "Monza",
            "circuit_key": 39,
        },
    ]


@pytest.fixture
def mock_drivers_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/drivers."""
    return [
        {
            "driver_number": 1,
            "session_key": 9161,
            "meeting_key": 1219,
            "full_name": "Max Verstappen",
            "first_name": "Max",
            "last_name": "Verstappen",
            "name_acronym": "VER",
            "broadcast_name": "M VERSTAPPEN",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
            "headshot_url": "https://www.formula1.com/content/dam/fom-website/drivers/M/MAXVER01.png",
        },
        {
            "driver_number": 55,
            "session_key": 9161,
            "meeting_key": 1219,
            "full_name": "Carlos Sainz",
            "first_name": "Carlos",
            "last_name": "Sainz",
            "name_acronym": "SAI",
            "broadcast_name": "C SAINZ",
            "team_name": "Ferrari",
            "team_colour": "E80020",
            "headshot_url": "https://www.formula1.com/content/dam/fom-website/drivers/C/CARSAI01.png",
        },
    ]


@pytest.fixture
def mock_laps_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/laps."""
    return [
        {
            "session_key": 9161,
            "meeting_key": 1219,
            "driver_number": 1,
            "lap_number": 1,
            "lap_duration": None,
            "is_pit_out_lap": True,
            "date_start": "2023-09-03T13:03:00+00:00",
            "duration_sector_1": 31.2,
            "duration_sector_2": 28.1,
            "duration_sector_3": 27.5,
            "i1_speed": 320.0,
            "i2_speed": 330.0,
            "st_speed": 345.0,
        },
        {
            "session_key": 9161,
            "meeting_key": 1219,
            "driver_number": 1,
            "lap_number": 2,
            "lap_duration": 85.073,
            "is_pit_out_lap": False,
            "date_start": "2023-09-03T13:04:28+00:00",
            "duration_sector_1": 27.4,
            "duration_sector_2": 27.8,
            "duration_sector_3": 29.873,
            "i1_speed": 335.0,
            "i2_speed": 342.0,
            "st_speed": 352.0,
        },
        {
            "session_key": 9161,
            "meeting_key": 1219,
            "driver_number": 1,
            "lap_number": 3,
            "lap_duration": 84.821,
            "is_pit_out_lap": False,
            "date_start": "2023-09-03T13:05:53+00:00",
            "duration_sector_1": 27.1,
            "duration_sector_2": 27.7,
            "duration_sector_3": 30.021,
            "i1_speed": 338.0,
            "i2_speed": 345.0,
            "st_speed": 354.0,
        },
        {
            "session_key": 9161,
            "meeting_key": 1219,
            "driver_number": 55,
            "lap_number": 2,
            "lap_duration": 85.120,
            "is_pit_out_lap": False,
            "date_start": "2023-09-03T13:04:29+00:00",
            "duration_sector_1": 27.5,
            "duration_sector_2": 27.9,
            "duration_sector_3": 29.720,
            "i1_speed": 336.0,
            "i2_speed": 340.0,
            "st_speed": 350.0,
        },
    ]


@pytest.fixture
def mock_car_data_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/car_data (~3.7 Hz)."""
    return [
        {
            "date": "2023-09-03T13:04:30.100000+00:00",
            "driver_number": 1,
            "session_key": 9161,
            "meeting_key": 1219,
            "speed": 315.0,
            "rpm": 11450,
            "n_gear": 7,
            "throttle": 100.0,
            "brake": 0.0,
            "drs": 12,
        },
        {
            "date": "2023-09-03T13:04:30.370000+00:00",
            "driver_number": 1,
            "session_key": 9161,
            "meeting_key": 1219,
            "speed": 322.0,
            "rpm": 11800,
            "n_gear": 8,
            "throttle": 100.0,
            "brake": 0.0,
            "drs": 12,
        },
        {
            "date": "2023-09-03T13:04:31.000000+00:00",
            "driver_number": 1,
            "session_key": 9161,
            "meeting_key": 1219,
            "speed": 120.0,
            "rpm": 8500,
            "n_gear": 3,
            "throttle": 10.0,
            "brake": 100.0,
            "drs": 1,
        },
    ]


@pytest.fixture
def mock_weather_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/weather."""
    return [
        {
            "date": "2023-09-03T13:00:00+00:00",
            "session_key": 9161,
            "meeting_key": 1219,
            "air_temperature": 28.5,
            "track_temperature": 42.1,
            "humidity": 45.0,
            "pressure": 1012.3,
            "rainfall": 0,
            "wind_speed": 2.1,
            "wind_direction": 180,
        }
    ]


@pytest.fixture
def mock_session_results_response() -> list[dict[str, Any]]:
    """Payload simulado do endpoint /v1/session_result."""
    return [
        {
            "position": 1,
            "driver_number": 1,
            "session_key": 9161,
            "meeting_key": 1219,
            "number_of_laps": 51,
            "duration": 4411.0,
            "gap_to_leader": None,
            "dnf": False,
            "dns": False,
            "dsq": False,
        },
        {
            "position": 2,
            "driver_number": 55,
            "session_key": 9161,
            "meeting_key": 1219,
            "number_of_laps": 51,
            "duration": 4417.0,
            "gap_to_leader": "+6.000",
            "dnf": False,
            "dns": False,
            "dsq": False,
        },
    ]
