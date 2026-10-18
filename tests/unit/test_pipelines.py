"""Testes unitários para o ponto de entrada CLI run_pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from f1.pipelines.run_pipeline import build_parser, main


def test_build_parser() -> None:
    """Valida argumentos aceitos pelo CLI."""
    parser = build_parser()
    args = parser.parse_args(
        [
            "--year",
            "2023",
            "--session-key",
            "9161",
            "--driver",
            "1",
            "--data-dir",
            "lake",
        ]
    )
    assert args.year == 2023
    assert args.session_key == "9161"
    assert args.driver == 1
    assert args.data_dir == "lake"


@patch("f1.pipelines.run_pipeline.F1DataService")
def test_main_success(mock_service_cls: MagicMock, tmp_path: Path) -> None:
    """Valida fluxo de execução com código de saída 0."""
    mock_instance = MagicMock()
    mock_instance.run_session_pipeline.return_value = {
        "laps": tmp_path / "laps.parquet",
    }
    mock_service_cls.return_value = mock_instance

    exit_code = main(["--year", "2023", "--session-key", "latest", "--driver", "55"])
    assert exit_code == 0
    mock_instance.process_meetings.assert_called_once_with(year=2023)
    mock_instance.process_sessions.assert_called_once_with(year=2023)
    mock_instance.run_session_pipeline.assert_called_once_with(
        session_key="latest",
        driver_numbers=[55],
    )


@patch("f1.pipelines.run_pipeline.F1DataService")
def test_main_handles_exception(mock_service_cls: MagicMock) -> None:
    """Garante que exceções críticas resultem em código de saída 1."""
    mock_instance = MagicMock()
    mock_instance.run_session_pipeline.side_effect = RuntimeError("Falha de conexão")
    mock_service_cls.return_value = mock_instance

    exit_code = main(["--session-key", "9999"])
    assert exit_code == 1
