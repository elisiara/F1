"""Testes unitários para o serviço orquestrador F1DataService."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from f1.config.settings import Settings
from f1.connectors.openf1_client import OpenF1Client
from f1.services.f1_service import F1DataService


@pytest.fixture
def mock_client(
    mock_meetings_response: list[dict[str, Any]],
    mock_sessions_response: list[dict[str, Any]],
    mock_drivers_response: list[dict[str, Any]],
    mock_laps_response: list[dict[str, Any]],
    mock_car_data_response: list[dict[str, Any]],
) -> MagicMock:
    """Mock de OpenF1Client com retornos pré-definidos."""
    client = MagicMock(spec=OpenF1Client)
    client.fetch_meetings.return_value = mock_meetings_response
    client.fetch_sessions.return_value = mock_sessions_response
    client.fetch_drivers.return_value = mock_drivers_response
    client.fetch_laps.return_value = mock_laps_response
    client.fetch_car_data.return_value = mock_car_data_response
    return client


def test_process_meetings(mock_client: MagicMock, tmp_path: Path) -> None:
    """Verifica extração e escrita em Parquet para meetings."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    parquet_path = service.process_meetings(year=2023)
    assert parquet_path.exists()
    assert parquet_path.name == "meetings.parquet"

    df = pd.read_parquet(parquet_path)
    assert len(df) == 1
    assert df["meeting_key"].iloc[0] == 1219


def test_process_sessions(mock_client: MagicMock, tmp_path: Path) -> None:
    """Verifica extração, limpeza e escrita em Parquet para sessões."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    parquet_path = service.process_sessions(year=2023)
    assert parquet_path.exists()
    assert parquet_path.name == "sessions.parquet"

    df = pd.read_parquet(parquet_path)
    assert len(df) == 2


def test_process_laps(mock_client: MagicMock, tmp_path: Path) -> None:
    """Verifica cálculo de voltas válidas e gravação particionada."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    parquet_path = service.process_laps(session_key=9161, driver_number=1)
    assert parquet_path.exists()
    assert "session_key=9161" in str(parquet_path)

    df = pd.read_parquet(parquet_path)
    # Voltas válidas da fixture: 3 voltas
    assert len(df) == 3
    assert "delta_to_previous_lap" in df.columns


def test_process_car_telemetry(mock_client: MagicMock, tmp_path: Path) -> None:
    """Verifica gravação da telemetria em Parquet."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    parquet_path = service.process_car_telemetry(session_key=9161, driver_number=1)
    assert parquet_path.exists()
    assert "driver=1" in str(parquet_path)

    df = pd.read_parquet(parquet_path)
    assert len(df) == 3
    assert "drs_status" in df.columns


def test_run_session_pipeline(mock_client: MagicMock, tmp_path: Path) -> None:
    """Valida execução completa da pipeline orquestrada."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    artifacts = service.run_session_pipeline(session_key=9161, driver_numbers=[1])
    assert "sessions" in artifacts
    assert "laps" in artifacts
    assert "telemetry_driver_1" in artifacts

    for path in artifacts.values():
        assert path.exists()


def test_run_session_pipeline_raises_on_empty_session(
    mock_client: MagicMock, tmp_path: Path
) -> None:
    """Garante que sessão inexistente dispare ValueError."""
    mock_client.fetch_sessions.return_value = []
    settings = Settings(base_dir=tmp_path, data_dir_name="data")
    service = F1DataService(client=mock_client, settings=settings)

    with pytest.raises(ValueError, match="Sessão não localizada"):
        service.run_session_pipeline(session_key=99999)
