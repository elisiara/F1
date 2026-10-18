"""Transformações puras e padronização para telemetria de sensores do carro."""

from typing import Any


def calculate_speed_kph(speed_mps: float) -> float:
    """Converte velocidade de metros por segundo (m/s) para km/h.

    Args:
        speed_mps: Velocidade em metros por segundo.

    Returns:
        Velocidade calculada em km/h arredondada para 2 casas decimais.

    Raises:
        ValueError: Caso a velocidade seja negativa.
    """
    if speed_mps < 0:
        raise ValueError(f"Velocidade não pode ser negativa: {speed_mps}")
    return round(speed_mps * 3.6, 2)


def parse_drs_status(drs_value: int) -> str:
    """Traduz o código numérico de DRS do carro para descrição semântica.

    Args:
        drs_value: Código numérico retornado pelo sensor de DRS.

    Returns:
        Estado legível: 'CLOSED', 'DETECTED', 'OPEN' ou 'UNKNOWN'.
    """
    match drs_value:
        case 0 | 1:
            return "CLOSED"
        case 8:
            return "DETECTED"
        case 10 | 12 | 14:
            return "OPEN"
        case _:
            return "UNKNOWN"


def clean_telemetry_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitiza e enriquece registros amostrais de telemetria de carro (~3.7 Hz).

    Args:
        samples: Lista de leituras brutas de sensores.

    Returns:
        Lista de amostras limpas e validadas com enriquecimento de status de DRS.
    """
    cleaned: list[dict[str, Any]] = []

    for sample in samples:
        speed = sample.get("speed")
        rpm = sample.get("rpm")
        throttle = sample.get("throttle")
        brake = sample.get("brake")
        drs = sample.get("drs", 0)

        if speed is None or rpm is None or throttle is None or brake is None:
            continue

        speed_val = max(0.0, float(speed))
        rpm_val = max(0, int(rpm))
        throttle_val = max(0.0, min(100.0, float(throttle)))
        brake_val = max(0.0, min(100.0, float(brake)))
        drs_val = int(drs)

        cleaned.append(
            {
                "date": str(sample.get("date", "")).strip(),
                "driver_number": int(sample["driver_number"]),
                "session_key": int(sample["session_key"]),
                "meeting_key": int(sample["meeting_key"])
                if sample.get("meeting_key") is not None
                else None,
                "speed": speed_val,
                "rpm": rpm_val,
                "n_gear": int(sample.get("n_gear", 0)),
                "throttle": throttle_val,
                "brake": brake_val,
                "drs": drs_val,
                "drs_status": parse_drs_status(drs_val),
            }
        )

    return cleaned


def calculate_telemetry_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula métricas analíticas agregadas para um lote de telemetria.

    Args:
        samples: Lista de amostras tratadas de telemetria.

    Returns:
        Dicionário com estatísticas descritivas (médias, picos e proporções).
    """
    if not samples:
        return {
            "sample_count": 0,
            "max_speed": 0.0,
            "avg_speed": 0.0,
            "max_rpm": 0,
            "avg_rpm": 0.0,
            "full_throttle_ratio": 0.0,
        }

    total_samples = len(samples)
    speeds = [float(s["speed"]) for s in samples]
    rpms = [int(s["rpm"]) for s in samples]
    full_throttle_count = sum(
        1 for s in samples if float(s.get("throttle", 0.0)) >= 98.0
    )

    return {
        "sample_count": total_samples,
        "max_speed": round(max(speeds), 2),
        "avg_speed": round(sum(speeds) / total_samples, 2),
        "max_rpm": max(rpms),
        "avg_rpm": round(sum(rpms) / total_samples, 2),
        "full_throttle_ratio": round(full_throttle_count / total_samples, 4),
    }
