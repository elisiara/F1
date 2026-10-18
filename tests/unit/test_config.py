"""Testes unitários para configurações e gerenciamento de caminhos."""

from pathlib import Path
from unittest.mock import patch

from f1.config.settings import Settings, get_settings


def test_settings_defaults() -> None:
    """Verifica se as configurações padrão são carregadas adequadamente."""
    settings = Settings()
    assert settings.openf1_base_url == "https://api.openf1.org/v1"
    assert settings.request_timeout_seconds == 15
    assert settings.max_retries == 3
    assert settings.log_level == "INFO"
    assert isinstance(settings.base_dir, Path)
    assert settings.data_dir == settings.base_dir / "data"
    assert settings.raw_data_dir == settings.data_dir / "raw"
    assert settings.processed_data_dir == settings.data_dir / "processed"


def test_settings_custom_data_dir() -> None:
    """Valida customização de diretório raiz."""
    settings = Settings(data_dir_name="custom_data")
    assert settings.data_dir == settings.base_dir / "custom_data"
    assert settings.raw_data_dir == settings.data_dir / "raw"


def test_settings_environment_override() -> None:
    """Valida a leitura e override de configurações a partir de variáveis de ambiente."""
    env = {
        "OPENF1_BASE_URL": "https://custom.api.f1/v1/",
        "REQUEST_TIMEOUT_SECONDS": "25",
        "MAX_RETRIES": "5",
        "LOG_LEVEL": "DEBUG",
        "DATA_DIR": "lake",
    }
    with patch.dict("os.environ", env):
        settings = get_settings()
        assert settings.openf1_base_url == "https://custom.api.f1/v1"
        assert settings.request_timeout_seconds == 25
        assert settings.max_retries == 5
        assert settings.log_level == "DEBUG"
        assert settings.data_dir_name == "lake"


def test_ensure_directories(tmp_path: Path) -> None:
    """Garante que ensure_directories crie as pastas no disco."""
    settings = Settings(base_dir=tmp_path, data_dir_name="data_test")
    assert not settings.raw_data_dir.exists()
    assert not settings.processed_data_dir.exists()

    settings.ensure_directories()
    assert settings.raw_data_dir.exists()
    assert settings.processed_data_dir.exists()

