"""Transformações puras e regras de negócio para análise de voltas (Laps)."""

from typing import Any


def filter_valid_laps(laps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filtra voltas descartando voltas de pit out, tempos zerados ou ausentes.

    Args:
        laps: Lista de registros brutos de voltas.

    Returns:
        Lista de voltas válidas e cronometradas.
    """
    valid: list[dict[str, Any]] = []
    for lap in laps:
        duration = lap.get("lap_duration")
        is_pit_out = lap.get("is_pit_out_lap", False)

        if duration is not None and float(duration) > 0 and not is_pit_out:
            valid.append(
                {
                    "session_key": int(lap["session_key"]),
                    "meeting_key": int(lap["meeting_key"])
                    if lap.get("meeting_key") is not None
                    else None,
                    "driver_number": int(lap["driver_number"]),
                    "lap_number": int(lap.get("lap_number", 0)),
                    "lap_duration": float(duration),
                    "duration_sector_1": float(lap["duration_sector_1"])
                    if lap.get("duration_sector_1") is not None
                    else None,
                    "duration_sector_2": float(lap["duration_sector_2"])
                    if lap.get("duration_sector_2") is not None
                    else None,
                    "duration_sector_3": float(lap["duration_sector_3"])
                    if lap.get("duration_sector_3") is not None
                    else None,
                    "i1_speed": float(lap["i1_speed"])
                    if lap.get("i1_speed") is not None
                    else None,
                    "i2_speed": float(lap["i2_speed"])
                    if lap.get("i2_speed") is not None
                    else None,
                    "st_speed": float(lap["st_speed"])
                    if lap.get("st_speed") is not None
                    else None,
                    "is_pit_out_lap": False,
                    "date_start": str(lap["date_start"]).strip()
                    if lap.get("date_start")
                    else None,
                }
            )
    return valid


def find_fastest_lap(laps: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Encontra a volta mais rápida absoluta de um conjunto de voltas válidas.

    Args:
        laps: Lista de voltas válidas.

    Returns:
        Dicionário com a melhor volta ou None caso a lista esteja vazia.
    """
    valid_laps = [
        lap
        for lap in laps
        if lap.get("lap_duration") is not None and float(lap["lap_duration"]) > 0
    ]
    if not valid_laps:
        return None
    return min(valid_laps, key=lambda lap: float(lap["lap_duration"]))


def find_driver_fastest_laps(laps: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Encontra a melhor volta pessoal para cada piloto presente no conjunto.

    Args:
        laps: Lista de voltas válidas.

    Returns:
        Mapeamento de driver_number para a respectiva melhor volta.
    """
    driver_laps: dict[int, dict[str, Any]] = {}
    for lap in laps:
        driver = lap.get("driver_number")
        duration = lap.get("lap_duration")
        if driver is None or duration is None or float(duration) <= 0:
            continue

        driver_num = int(driver)
        current_best = driver_laps.get(driver_num)
        if current_best is None or float(duration) < float(
            current_best["lap_duration"]
        ):
            driver_laps[driver_num] = lap

    return driver_laps


def parse_mini_sector_code(code: int) -> str:
    """Traduz o código numérico de mini-setor da OpenF1 para rótulo legível.

    Args:
        code: Código numérico retornado pela API.

    Returns:
        String representando o status/cor do setor ('YELLOW', 'GREEN', 'PURPLE', 'PIT', 'UNKNOWN').
    """
    match code:
        case 2048:
            return "YELLOW"
        case 2049:
            return "GREEN"
        case 2051:
            return "PURPLE"
        case 2064:
            return "PIT"
        case _:
            return "UNKNOWN"


def calculate_lap_deltas(laps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Calcula a diferença de tempo (delta) entre voltas cronometradas consecutivas.

    Args:
        laps: Lista de voltas ordenadas por número da volta.

    Returns:
        Nova lista contendo o campo adicional 'delta_to_previous_lap'.
    """
    result: list[dict[str, Any]] = []
    previous_duration: float | None = None

    for lap in sorted(laps, key=lambda x: int(x.get("lap_number", 0))):
        lap_copy = dict(lap)
        current_duration = lap.get("lap_duration")

        if current_duration is not None and previous_duration is not None:
            lap_copy["delta_to_previous_lap"] = round(
                float(current_duration) - previous_duration, 3
            )
        else:
            lap_copy["delta_to_previous_lap"] = None

        if current_duration is not None:
            previous_duration = float(current_duration)

        result.append(lap_copy)

    return result
