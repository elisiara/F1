"""Configurações centralizadas da aplicação e caminhos de dados."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Configurações operacionais do pipeline F1."""

    openf1_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENF1_BASE_URL", "https://api.openf1.org/v1"
        ).rstrip("/")
    )
    request_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    )
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    base_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent
    )
    data_dir_name: str = field(default_factory=lambda: os.getenv("DATA_DIR", "data"))

    @property
    def data_dir(self) -> Path:
        """Diretório raiz de armazenamento de dados."""
        return self.base_dir / self.data_dir_name

    @property
    def raw_data_dir(self) -> Path:
        """Diretório de dados brutos (camada bronze)."""
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        """Diretório de dados processados particionados (camada silver)."""
        return self.data_dir / "processed"

    def ensure_directories(self) -> None:
        """Cria as pastas necessárias no sistema de arquivos caso não existam."""
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Instancia e retorna as configurações padrão do ambiente."""
    return Settings()
