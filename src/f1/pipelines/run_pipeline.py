"""Ponto de entrada de linha de comando (CLI) para execução do pipeline OpenF1."""

import argparse
import sys

from f1.config.settings import Settings
from f1.services.f1_service import F1DataService
from f1.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Configura e retorna o analisador de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        prog="poetry run python -m f1.pipelines.run_pipeline",
        description="Executa o pipeline de ingestão, transformação e persistência da F1 via OpenF1 API.",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Ano da temporada da Fórmula 1 (ex: 2023, 2024).",
    )
    parser.add_argument(
        "--session-key",
        type=str,
        default="latest",
        help="Identificador numérico da sessão ou 'latest' (padrão: latest).",
    )
    parser.add_argument(
        "--driver",
        type=int,
        default=None,
        help="Número permanente do piloto para telemetria (ex: 1, 44, 55).",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Nome do diretório raiz para gravação dos arquivos (padrão: data).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Função principal de orquestração via CLI.

    Args:
        argv: Lista opcional de argumentos de linha de comando.

    Returns:
        0 em caso de sucesso ou 1 em caso de falha.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    logger.info("Iniciando execução do pipeline de dados da Fórmula 1...")

    try:
        settings = Settings(data_dir_name=args.data_dir)
        service = F1DataService(settings=settings)

        if args.year is not None:
            logger.info("Processando meetings e sessões da temporada %d", args.year)
            service.process_meetings(year=args.year)
            service.process_sessions(year=args.year)

        driver_list = [args.driver] if args.driver is not None else None
        artifacts = service.run_session_pipeline(
            session_key=args.session_key,
            driver_numbers=driver_list,
        )

        logger.info("Pipeline concluído com êxito! Artefatos gravados:")
        for name, path in artifacts.items():
            logger.info(" - %s: %s", name, path)

        return 0
    except Exception as exc:
        logger.error(
            "Falha crítica durante a execução do pipeline: %s", exc, exc_info=True
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
