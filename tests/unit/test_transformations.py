"""Testes unitários detalhados para as transformações puras."""

from typing import Any

import pytest

from f1.transformations.laps import (
    calculate_lap_deltas,
    filter_valid_laps,
    find_driver_fastest_laps,
    find_fastest_lap,
    parse_mini_sector_code,
)
from f1.transformations.sessions import (
    clean_sessions,
    filter_sessions_by_type,
    normalize_session_record,
    sort_sessions_by_date,
)
from f1.transformations.telemetry import (
    calculate_speed_kph,
    calculate_telemetry_summary,
    clean_telemetry_samples,
    parse_drs_status,
)

# ---------------------------------------------------------------------------
# Testes de Sessões
# ---------------------------------------------------------------------------


def test_normalize_session_record_valid() -> None:
    """Valida normalização de campos de uma sessão válida."""
    raw = {
        "session_key": "9161",
        "meeting_key": "1219",
        "session_name": "  Race  ",
        "session_type": "Race",
        "year": "2023",
        "date_start": "2023-09-03T13:00:00+00:00",
        "circuit_key": 39,
    }
    normalized = normalize_session_record(raw)
    assert normalized["session_key"] == 9161
    assert normalized["meeting_key"] == 1219
    assert normalized["session_name"] == "Race"
    assert normalized["year"] == 2023


def test_normalize_session_record_raises_on_missing_key() -> None:
    """Garante que a ausência de session_key dispare ValueError."""
    with pytest.raises(ValueError, match="session_key"):
        normalize_session_record({"session_name": "Test"})


def test_clean_sessions_drops_invalid_records() -> None:
    """Valida descarte de registros inválidos sem interromper o lote."""
    batch = [
        {"session_key": 1, "session_name": "S1"},
        {"session_name": "Invalida (sem key)"},
        {"session_key": 2, "session_name": "S2"},
    ]
    cleaned = clean_sessions(batch)
    assert len(cleaned) == 2
    assert [s["session_key"] for s in cleaned] == [1, 2]


def test_filter_sessions_by_type(mock_sessions_response: list[dict[str, Any]]) -> None:
    """Valida filtro insensível a maiúsculas/minúsculas por tipo."""
    races = filter_sessions_by_type(mock_sessions_response, "race")
    assert len(races) == 1
    assert races[0]["session_name"] == "Race"

    practices = filter_sessions_by_type(mock_sessions_response, "practice")
    assert len(practices) == 1
    assert practices[0]["session_name"] == "Practice 1"


def test_sort_sessions_by_date(mock_sessions_response: list[dict[str, Any]]) -> None:
    """Valida ordenação cronológica direta e reversa."""
    sorted_asc = sort_sessions_by_date(mock_sessions_response, reverse=False)
    assert sorted_asc[0]["session_name"] == "Practice 1"

    sorted_desc = sort_sessions_by_date(mock_sessions_response, reverse=True)
    assert sorted_desc[0]["session_name"] == "Race"


# ---------------------------------------------------------------------------
# Testes de Voltas (Laps)
# ---------------------------------------------------------------------------


def test_filter_valid_laps(mock_laps_response: list[dict[str, Any]]) -> None:
    """Valida filtragem descartando voltas de pit out e sem tempo."""
    valid = filter_valid_laps(mock_laps_response)
    # 4 voltas na fixture: volta 1 do piloto 1 é pit-out e lap_duration=None
    assert len(valid) == 3
    for lap in valid:
        assert lap["lap_duration"] is not None
        assert lap["lap_duration"] > 0
        assert not lap["is_pit_out_lap"]


def test_find_fastest_lap(mock_laps_response: list[dict[str, Any]]) -> None:
    """Identifica a volta com menor duração absoluta."""
    valid = filter_valid_laps(mock_laps_response)
    fastest = find_fastest_lap(valid)
    assert fastest is not None
    assert fastest["driver_number"] == 1
    assert fastest["lap_number"] == 3
    assert fastest["lap_duration"] == 84.821


def test_find_fastest_lap_empty() -> None:
    """Garante retorno de None para coleções vazias."""
    assert find_fastest_lap([]) is None


def test_find_driver_fastest_laps(mock_laps_response: list[dict[str, Any]]) -> None:
    """Valida melhor marca individual por piloto."""
    valid = filter_valid_laps(mock_laps_response)
    driver_bests = find_driver_fastest_laps(valid)

    assert 1 in driver_bests
    assert 55 in driver_bests
    assert driver_bests[1]["lap_duration"] == 84.821
    assert driver_bests[55]["lap_duration"] == 85.120


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        (2048, "YELLOW"),
        (2049, "GREEN"),
        (2051, "PURPLE"),
        (2064, "PIT"),
        (0, "UNKNOWN"),
        (9999, "UNKNOWN"),
    ],
)
def test_parse_mini_sector_code(code: int, expected_status: str) -> None:
    """Valida mapeamento semântico dos códigos numéricos de mini-setores."""
    assert parse_mini_sector_code(code) == expected_status


def test_calculate_lap_deltas() -> None:
    """Valida cálculo de deltas temporais entre voltas consecutivas."""
    laps = [
        {"lap_number": 1, "lap_duration": 85.0},
        {"lap_number": 2, "lap_duration": 84.5},
        {"lap_number": 3, "lap_duration": 86.0},
    ]
    deltas = calculate_lap_deltas(laps)
    assert len(deltas) == 3
    assert deltas[0]["delta_to_previous_lap"] is None
    assert deltas[1]["delta_to_previous_lap"] == -0.5
    assert deltas[2]["delta_to_previous_lap"] == 1.5


# ---------------------------------------------------------------------------
# Testes de Telemetria
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("speed_mps", "expected_kph"),
    [
        (0.0, 0.0),
        (10.0, 36.0),
        (50.0, 180.0),
        (88.8889, 320.0),
    ],
)
def test_calculate_speed_kph_valid(speed_mps: float, expected_kph: float) -> None:
    """Valida conversão de m/s para km/h."""
    assert calculate_speed_kph(speed_mps) == expected_kph


def test_calculate_speed_kph_raises_on_negative() -> None:
    """Garante que velocidades negativas disparem ValueError."""
    with pytest.raises(ValueError, match="Velocidade não pode ser negativa"):
        calculate_speed_kph(-10.0)


@pytest.mark.parametrize(
    ("drs_value", "expected_status"),
    [
        (0, "CLOSED"),
        (1, "CLOSED"),
        (8, "DETECTED"),
        (10, "OPEN"),
        (12, "OPEN"),
        (14, "OPEN"),
        (99, "UNKNOWN"),
    ],
)
def test_parse_drs_status(drs_value: int, expected_status: str) -> None:
    """Valida mapeamento de estados do DRS."""
    assert parse_drs_status(drs_value) == expected_status


def test_clean_telemetry_samples(mock_car_data_response: list[dict[str, Any]]) -> None:
    """Valida limpeza, clamping de throttle/brake e enriquecimento de DRS."""
    cleaned = clean_telemetry_samples(mock_car_data_response)
    assert len(cleaned) == 3
    assert cleaned[0]["drs_status"] == "OPEN"
    assert cleaned[2]["drs_status"] == "CLOSED"


def test_calculate_telemetry_summary(
    mock_car_data_response: list[dict[str, Any]],
) -> None:
    """Valida cálculo de resumo estatístico agregado de telemetria."""
    cleaned = clean_telemetry_samples(mock_car_data_response)
    summary = calculate_telemetry_summary(cleaned)

    assert summary["sample_count"] == 3
    assert summary["max_speed"] == 322.0
    assert summary["max_rpm"] == 11800
    assert summary["full_throttle_ratio"] == round(2 / 3, 4)


def test_calculate_telemetry_summary_empty() -> None:
    """Valida resumo seguro para conjuntos de telemetria vazios."""
    summary = calculate_telemetry_summary([])
    assert summary["sample_count"] == 0
    assert summary["max_speed"] == 0.0
