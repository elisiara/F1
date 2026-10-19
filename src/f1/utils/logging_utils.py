"""Configuração e utilitários de logging padronizados para o pipeline."""

import logging
import os
import sys


def get_logger(name: str | None = None) -> logging.Logger:
    """Configura e retorna um logger padronizado para o módulo especificado.

    Args:
        name: Nome semântico do módulo ou componente (ex: __name__).

    Returns:
        Instância de logging.Logger devidamente configurada.
    """
    logger_name = name if name else "f1"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, level_str, logging.INFO)
        logger.setLevel(log_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
