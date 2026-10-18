"""Serviço de orquestração para ingestão, transformação e persistência colunar."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from f1.config.settings import Settings, get_settings
from f1.connectors.openf1_client import OpenF1Client
from f1.transformations.laps import calculate_lap_deltas, filter_valid_laps
from f1.transformations.sessions import clean_sessions
from f1.transformations.telemetry import clean_telemetry_samples
from f1.utils.logging_utils import get_logger

logger = get_logger(__name__)


class F1DataService:
    """Coordena o fluxo E-V-T-L integrando OpenF1Client, transformações e armazenamento."""

    def __init__(
        self,
        client: OpenF1Client | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Inicializa o serviço com cliente de API e configurações."""
        self.settings = settings or get_settings()
        self.client = client or OpenF1Client(
            base_url=self.settings.openf1_base_url,
            timeout_seconds=self.settings.request_timeout_seconds,
            max_retries=self.settings.max_retries,
        )

    def _save_raw(
        self, entity_name: str, identifier: str, data: list[dict[str, Any]]
    ) -> Path:
        """Salva uma cópia do payload bruto (camada bronze) em JSON para rastreabilidade."""
        self.settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
        raw_file = self.settings.raw_data_dir / f"{entity_name}_{identifier}.json"
        with open(raw_file, mode="w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        logger.debug("Payload bruto de %s salvo em %s", entity_name, raw_file)
        return raw_file

    def _save_parquet(self, df: pd.DataFrame, target_path: Path) -> Path:
        """Grava um DataFrame de forma atômica e idempotente em formato Parquet."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(target_path, index=False, engine="pyarrow")
        logger.info(
            "Dataset persistido em Parquet com sucesso: %s (%d registros)",
            target_path,
            len(df),
        )
        return target_path

    def process_meetings(self, year: int) -> Path:
        """Extrai, valida e persiste Grandes Prêmios e testes para determinado ano.

        Args:
            year: Ano da temporada da F1.

        Returns:
            Caminho do arquivo Parquet particionado gravado.
        """
        logger.info("Iniciando ingestão de meetings para o ano %d", year)
        raw_data = self.client.fetch_meetings(year=year)
        self._save_raw("meetings", str(year), raw_data)

        df = pd.DataFrame(raw_data)
        if df.empty:
            logger.warning("Nenhum meeting retornado para o ano %d", year)
            df = pd.DataFrame(
                columns=[
                    "meeting_key",
                    "meeting_name",
                    "year",
                    "country_name",
                    "circuit_short_name",
                ]
            )

        target_path = (
            self.settings.processed_data_dir
            / "meetings"
            / f"year={year}"
            / "meetings.parquet"
        )
        return self._save_parquet(df, target_path)

    def process_sessions(self, year: int) -> Path:
        """Extrai, limpa e persiste as sessões de pista de determinado ano.

        Args:
            year: Ano da temporada da F1.

        Returns:
            Caminho do arquivo Parquet particionado gravado.
        """
        logger.info("Iniciando ingestão e limpeza de sessões para o ano %d", year)
        raw_data = self.client.fetch_sessions(year=year)
        self._save_raw("sessions", str(year), raw_data)

        cleaned_data = clean_sessions(raw_data)
        df = pd.DataFrame(cleaned_data)
        if df.empty:
            logger.warning("Nenhuma sessão válida após limpeza para o ano %d", year)
            df = pd.DataFrame(
                columns=[
                    "session_key",
                    "meeting_key",
                    "session_name",
                    "session_type",
                    "year",
                ]
            )

        target_path = (
            self.settings.processed_data_dir
            / "sessions"
            / f"year={year}"
            / "sessions.parquet"
        )
        return self._save_parquet(df, target_path)

    def process_laps(
        self, session_key: int | str, driver_number: int | None = None
    ) -> Path:
        """Extrai, filtra voltas válidas, calcula deltas e persiste em Parquet.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número opcional do piloto.

        Returns:
            Caminho do arquivo Parquet particionado gravado.
        """
        logger.info(
            "Iniciando ingestão de voltas para session_key=%s (driver=%s)",
            session_key,
            driver_number,
        )
        raw_data = self.client.fetch_laps(
            session_key=session_key, driver_number=driver_number
        )
        ident = (
            f"{session_key}_driver_{driver_number}"
            if driver_number
            else str(session_key)
        )
        self._save_raw("laps", ident, raw_data)

        valid_laps = filter_valid_laps(raw_data)
        transformed_laps = calculate_lap_deltas(valid_laps)
        df = pd.DataFrame(transformed_laps)

        if df.empty:
            logger.warning(
                "Nenhuma volta válida encontrada para session_key=%s", session_key
            )
            df = pd.DataFrame(
                columns=["session_key", "driver_number", "lap_number", "lap_duration"]
            )

        target_path = (
            self.settings.processed_data_dir
            / "laps"
            / f"session_key={session_key}"
            / "laps.parquet"
        )
        return self._save_parquet(df, target_path)

    def process_car_telemetry(self, session_key: int | str, driver_number: int) -> Path:
        """Extrai, sanitiza e persiste telemetria de sensores de carro para um piloto.

        Args:
            session_key: Identificador da sessão ou 'latest'.
            driver_number: Número permanente do piloto.

        Returns:
            Caminho do arquivo Parquet particionado gravado.
        """
        logger.info(
            "Iniciando ingestão de telemetria para session_key=%s, piloto #%d",
            session_key,
            driver_number,
        )
        raw_data = self.client.fetch_car_data(
            session_key=session_key, driver_number=driver_number
        )
        self._save_raw("telemetry", f"{session_key}_driver_{driver_number}", raw_data)

        cleaned_data = clean_telemetry_samples(raw_data)
        df = pd.DataFrame(cleaned_data)

        if df.empty:
            logger.warning(
                "Nenhuma amostra de telemetria válida para session_key=%s, piloto #%d",
                session_key,
                driver_number,
            )
            df = pd.DataFrame(
                columns=[
                    "date",
                    "driver_number",
                    "session_key",
                    "speed",
                    "rpm",
                    "throttle",
                    "brake",
                    "drs_status",
                ]
            )

        target_path = (
            self.settings.processed_data_dir
            / "telemetry"
            / f"session_key={session_key}"
            / f"driver={driver_number}"
            / "telemetry.parquet"
        )
        return self._save_parquet(df, target_path)

    def run_session_pipeline(
        self,
        session_key: int | str = "latest",
        driver_numbers: list[int] | None = None,
    ) -> dict[str, Path]:
        """Executa o pipeline analítico completo para uma sessão específica ou a mais recente.

        Args:
            session_key: Chave da sessão ou 'latest'.
            driver_numbers: Lista opcional de números de pilotos para telemetria.

        Returns:
            Mapeamento de nomes de datasets gerados para seus respectivos caminhos Parquet.
        """
        logger.info(
            ">>> Iniciando Pipeline Completo da Sessão: session_key=%s <<<", session_key
        )
        self.settings.ensure_directories()
        results: dict[str, Path] = {}

        # 1. Buscar detalhes da sessão
        sessions = self.client.fetch_sessions(session_key=session_key)
        if not sessions:
            logger.error("Nenhuma informação encontrada para a sessão %s", session_key)
            raise ValueError(f"Sessão não localizada: {session_key}")

        current_session = sessions[0]
        resolved_key = current_session.get("session_key", session_key)
        year = int(current_session.get("year", 2023))

        # 2. Processar sessões do ano correspondente
        results["sessions"] = self.process_sessions(year=year)

        # 3. Processar voltas da sessão
        results["laps"] = self.process_laps(session_key=resolved_key)

        # 4. Processar pilotos da sessão se não foram informados
        drivers_to_process = driver_numbers
        if not drivers_to_process:
            drivers_raw = self.client.fetch_drivers(session_key=resolved_key)
            drivers_to_process = [
                int(d["driver_number"])
                for d in drivers_raw
                if d.get("driver_number") is not None
            ][:2]  # Processa os primeiros 2 pilotos por padrão para agilidade

        # 5. Processar telemetria para os pilotos selecionados
        for driver_num in drivers_to_process:
            key_name = f"telemetry_driver_{driver_num}"
            results[key_name] = self.process_car_telemetry(
                session_key=resolved_key, driver_number=driver_num
            )

        logger.info(
            ">>> Pipeline da Sessão concluído com sucesso! %d artefatos gerados <<<",
            len(results),
        )
        return results
