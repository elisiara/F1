"""
Dashboard Streamlit minimal integrando com F1DataService / OpenF1Client.

Este arquivo funciona como composition root da UI, aplica cache ao serviço
e cache de dados por sessão. A implementação é deliberadamente simples e
respeita a separação de camadas do projeto (UI -> services -> connectors).
"""

from typing import Any

import pandas as pd
import streamlit as st

from f1.config.settings import get_settings
from f1.connectors.openf1_client import OpenF1Client
from f1.services.f1_service import F1DataService
from f1.utils.logging_utils import get_logger

logger = get_logger(__name__)


@st.cache_resource
def build_service() -> F1DataService:
    """Constrói e cacheia a instância do serviço orquestrador."""
    settings = get_settings()
    client = OpenF1Client(
        base_url=settings.openf1_base_url,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.max_retries,
    )
    return F1DataService(client=client, settings=settings)


@st.cache_data(ttl=300)
def load_session_overview(session_key: str) -> dict[str, Any]:
    """
    Carrega dados de sessão (meta) e Top N voltas.
    Retorna dicionário com chaves: session, drivers, top_laps (DataFrame).
    """
    service = build_service()
    sessions = service.client.fetch_sessions(session_key=session_key)
    if not sessions:
        return {"session": None, "drivers": [], "top_laps": pd.DataFrame()}

    session = sessions[0]
    resolved_key = session.get("session_key", session_key)

    drivers = service.client.fetch_drivers(session_key=resolved_key)
    raw_laps = service.client.fetch_laps(session_key=resolved_key)

    try:
        from f1.transformations.laps import filter_valid_laps
    except Exception:
        valid = [r for r in raw_laps if r.get("lap_duration") is not None]
    else:
        valid = filter_valid_laps(raw_laps)

    df = pd.DataFrame(valid)
    if not df.empty and "lap_duration" in df.columns:
        top_laps = df.sort_values("lap_duration").head(10).reset_index(drop=True)
    else:
        top_laps = pd.DataFrame()

    return {"session": session, "drivers": drivers, "top_laps": top_laps}


def render_top_laps(df: pd.DataFrame) -> None:
    """Renderiza tabela simples de Top N voltas."""
    if df.empty:
        st.info("Nenhuma volta disponível para esta sessão.")
        return
    st.dataframe(df)


def main() -> None:
    st.set_page_config(page_title="F1 Dashboard", layout="wide")
    st.title("F1 Dashboard (OpenF1)")

    service = build_service()

    years = [2023, 2024, 2025]
    year = st.sidebar.selectbox("Temporada", years, index=0)

    meetings = service.client.fetch_meetings(year=year)
    meeting_options = [m.get("meeting_name", str(m.get("meeting_key"))) for m in meetings]
    meeting_choice = (
        st.sidebar.selectbox("GP / Meeting", meeting_options) if meeting_options else None
    )

    meeting_key = None
    if meeting_choice:
        for m in meetings:
            if m.get("meeting_name") == meeting_choice:
                meeting_key = m.get("meeting_key")
                break

    sessions = []
    if meeting_key is not None:
        sessions = service.client.fetch_sessions(meeting_key=meeting_key)
    session_options = [s.get("session_name", str(s.get("session_key"))) for s in sessions]
    session_choice = st.sidebar.selectbox("Sessão", session_options) if session_options else None

    session_key = None
    if session_choice:
        for s in sessions:
            if s.get("session_name") == session_choice:
                session_key = s.get("session_key")
                break

    if not session_key:
        session_key = st.sidebar.text_input("Session key (ou 'latest')", value="latest")

    overview = load_session_overview(str(session_key))

    st.subheader("Top 10 voltas mais rápidas")
    render_top_laps(overview.get("top_laps", pd.DataFrame()))

    st.subheader("Resumo da sessão")
    sess = overview.get("session")
    if sess:
        st.write(sess)
    else:
        st.info("Sessão não encontrada.")


if __name__ == "__main__":
    main()