"""Cliente HTTP resiliente e tipado para consumo da OpenF1 REST API."""

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1.utils.logging_utils import get_logger

logger = get_logger(__name__)


class OpenF1ClientError(Exception):
    """Exceção semântica para falhas na comunicação com a OpenF1 API."""


class OpenF1Client:
    """Encapsula operações de rede e consumo de dados junto à OpenF1 API."""

    def __init__(
        self,
        base_url: str = "https://api.openf1.org/v1",
        timeout_seconds: int = 15,
        max_retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        """Inicializa o cliente com políticas de timeout e retries exponenciais."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds

        if session is not None:
            self._session = session
        else:
            self._session = requests.Session()
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)

    def _get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Executa requisição GET autenticada e parametrizada com timeout explícito.

        Args:
            endpoint: Caminho relativo do endpoint (ex: '/sessions').
            params: Dicionário opcional de parâmetros de query string.

        Returns:
            Lista de dicionários brutos retornados pela API.

        Raises:
            OpenF1ClientError: Em caso de falha de conexão ou código HTTP de erro.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        logger.debug(
            "Requisitando endpoint OpenF1: %s com params: %s", url, clean_params
        )

        try:
            response = self._session.get(url, params=clean_params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.warning(
                    "Resposta inesperada da API (não-lista) para URL %s", url
                )
                return []
            return data
        except requests.RequestException as exc:
            logger.error("Falha na chamada à OpenF1 API [%s]: %s", url, str(exc))
            raise OpenF1ClientError(f"Erro ao consultar OpenF1 ({url}): {exc}") from exc

    def fetch_meetings(
        self,
        year: int | None = None,
        country_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Recupera lista de Grandes Prêmios e testes do calendário."""
        params: dict[str, Any] = {}
        if year is not None:
            params["year"] = year
        if country_name is not None:
            params["country_name"] = country_name
        return self._get("meetings", params)

    def fetch_sessions(
        self,
        meeting_key: int | str | None = None,
        year: int | None = None,
        session_name: str | None = None,
        session_key: int | str | None = None,
    ) -> list[dict[str, Any]]:
        """Recupera lista de sessões de pista com filtros opcionais."""
        params: dict[str, Any] = {}
        if meeting_key is not None:
            params["meeting_key"] = meeting_key
        if year is not None:
            params["year"] = year
        if session_name is not None:
            params["session_name"] = session_name
        if session_key is not None:
            params["session_key"] = session_key
        return self._get("sessions", params)

    def fetch_drivers(self, session_key: int | str) -> list[dict[str, Any]]:
        """Recupera os pilotos participantes de determinada sessão."""
        return self._get("drivers", {"session_key": session_key})

    def fetch_laps(
        self,
        session_key: int | str,
        driver_number: int | None = None,
    ) -> list[dict[str, Any]]:
        """Recupera cronometragens volta a volta para a sessão informada."""
        params: dict[str, Any] = {"session_key": session_key}
        if driver_number is not None:
            params["driver_number"] = driver_number
        return self._get("laps", params)

    def fetch_car_data(
        self,
        session_key: int | str,
        driver_number: int,
        speed_gte: float | None = None,
    ) -> list[dict[str, Any]]:
        """Recupera telemetria dos sensores do carro em alta frequência (~3.7 Hz)."""
        params: dict[str, Any] = {
            "session_key": session_key,
            "driver_number": driver_number,
        }
        if speed_gte is not None:
            params["speed>="] = speed_gte
        return self._get("car_data", params)

    def fetch_weather(
        self,
        session_key: int | str | None = None,
        meeting_key: int | str | None = None,
    ) -> list[dict[str, Any]]:
        """Recupera dados meteorológicos medidos durante o evento."""
        params: dict[str, Any] = {}
        if session_key is not None:
            params["session_key"] = session_key
        if meeting_key is not None:
            params["meeting_key"] = meeting_key
        return self._get("weather", params)

    def fetch_session_results(self, session_key: int | str) -> list[dict[str, Any]]:
        """Recupera classificação final homologada para a sessão."""
        return self._get("session_result", {"session_key": session_key})
