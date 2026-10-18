"""Transformações puras e padronização para registros de sessões."""

from typing import Any


def normalize_session_record(session: dict[str, Any]) -> dict[str, Any]:
    """Normaliza e sanitiza os campos de um registro individual de sessão.

    Args:
        session: Dicionário bruto vindo da API.

    Returns:
        Dicionário normalizado com chaves tipadas e valores limpos.

    Raises:
        ValueError: Caso o registro não contenha session_key válida.
    """
    raw_key = session.get("session_key")
    if raw_key is None:
        raise ValueError("Registro de sessão inválido: 'session_key' ausente")

    return {
        "session_key": int(raw_key),
        "meeting_key": int(session["meeting_key"])
        if session.get("meeting_key") is not None
        else None,
        "session_name": str(session.get("session_name", "")).strip(),
        "session_type": str(session.get("session_type", "")).strip(),
        "year": int(session.get("year", 0)),
        "date_start": str(session["date_start"]).strip()
        if session.get("date_start")
        else None,
        "date_end": str(session["date_end"]).strip()
        if session.get("date_end")
        else None,
        "gmt_offset": str(session["gmt_offset"]).strip()
        if session.get("gmt_offset")
        else None,
        "location": str(session["location"]).strip()
        if session.get("location")
        else None,
        "circuit_key": int(session["circuit_key"])
        if session.get("circuit_key") is not None
        else None,
    }


def clean_sessions(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aplica normalização a um lote de sessões, descartando registros inválidos.

    Args:
        sessions: Lista de sessões brutas.

    Returns:
        Lista de sessões sanitizadas.
    """
    cleaned: list[dict[str, Any]] = []
    for session in sessions:
        try:
            cleaned.append(normalize_session_record(session))
        except (ValueError, KeyError, TypeError):
            continue
    return cleaned


def filter_sessions_by_type(
    sessions: list[dict[str, Any]], session_type: str
) -> list[dict[str, Any]]:
    """Filtra sessões por tipo de forma insensível a maiúsculas/minúsculas.

    Args:
        sessions: Lista de sessões.
        session_type: Tipo desejado (ex: 'Race', 'Qualifying', 'Practice').

    Returns:
        Lista contendo apenas as sessões correspondentes.
    """
    target = session_type.strip().lower()
    return [
        s
        for s in sessions
        if str(s.get("session_type", "")).strip().lower() == target
        or str(s.get("session_name", "")).strip().lower() == target
    ]


def sort_sessions_by_date(
    sessions: list[dict[str, Any]], reverse: bool = False
) -> list[dict[str, Any]]:
    """Ordena determinísticamente uma lista de sessões pela data de início.

    Args:
        sessions: Lista de sessões.
        reverse: Se True, ordena em ordem decrescente (mais recente primeiro).

    Returns:
        Nova lista de sessões ordenadas.
    """
    return sorted(
        sessions,
        key=lambda s: str(s.get("date_start") or ""),
        reverse=reverse,
    )
