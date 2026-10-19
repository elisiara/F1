# Review de Ajustes para Dashboard Streamlit e `src/f1/dashboard.py`

Data: 2026-10-19
Status: rascunho para execução posterior

## Objetivo

Este documento define um conjunto de ajustes focados para integrar ao projeto já planejado em `.agents/plan.md` a necessidade de uma dashboard interativa em Streamlit, sem reescrever a solução do zero.

A intenção é manter a arquitetura e as convenções do projeto, mas inserir o ponto de entrada da UI em `src/f1/dashboard.py`, conectar com a camada de serviços e manter o restante do pipeline e a estrutura do projeto íntegros.

## Escopo do review

A revisão deve observar os seguintes princípios:

- Não reescrever o projeto inteiro.
- Manter a arquitetura em camadas definida em `.agents/plan.md`.
- Adicionar a dashboard em Streamlit como camada de apresentação, sem abrir brecha para dependência reversa.
- Integrar `dashboard.py` com entidades e serviços já previstos, especialmente `F1DashboardService` / `OpenF1Client` / `domain` / `processing`.
- Trabalhar em ajustes incrementais, sem desvirtuar o plano principal de engenharia de dados.

## Observações do problema detectado

O plano em `.agents/plan.md` está fortemente orientado para pipeline ETL/analítico (OpenF1 API → transformações → parquet / serviços) e não previa explicitamente:

- UI Streamlit,
- dashboard em `src/f1/dashboard.py`,
- uso de `@st.cache_resource` e `@st.cache_data`,
- visualização de Top N voltas, pilotos, equipes e sessão.

A estrutura de domínio e repositórios proposta em um plano complementar (pasted.txt) já indica a direção correta para uma dashboard simples e bem integrada:

- `src/f1/domain/models.py`
- `src/f1/domain/repositories.py`
- `src/f1/domain/services.py`
- `src/f1/processing/lap_processor.py`
- `src/f1/ingestion/http_client.py`
- `src/f1/ingestion/openf1_client.py`
- `src/f1/dashboard.py`

Logo, o ajuste precisa ser de encaixe, e não de recomeço.

## Ajustes que devem ser realizados

### 1) Criar `src/f1/dashboard.py`

O arquivo deve funcionar como composition root da aplicação Streamlit.

Responsabilidades esperadas:

- instanciar `HttpClient` com timeout e configuration defaults;
- instanciar os repositórios concretos da OpenF1;
- construir `F1DashboardService` via injeção de dependência;
- expor UI para selecionar temporada, meeting e session;
- renderizar tabela de Top 10 voltas mais rápidas;
- exibir cards por piloto/equipe/tempo;
- aplicar `@st.cache_resource` ao service;
- aplicar `@st.cache_data` aos resultados por sessão.

Estrutura desejada:

```python
# src/f1/dashboard.py
import streamlit as st

from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    DriverRepositoryOpenF1,
    LapRepositoryOpenF1,
    MeetingRepositoryOpenF1,
    SessionRepositoryOpenF1,
)
from f1.utils.config import get_settings
from f1.utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_resource
def build_service() -> F1DashboardService:
    settings = get_settings()
    client = HttpClient(
        base_url=settings.OPENF1_BASE_URL,
        timeout=settings.OPENF1_TIMEOUT,
    )
    meetings = MeetingRepositoryOpenF1(client)
    sessions = SessionRepositoryOpenF1(client)
    drivers = DriverRepositoryOpenF1(client)
    laps = LapRepositoryOpenF1(client)
    return F1DashboardService(meetings, sessions, drivers, laps)


@st.cache_data(ttl=300)
def load_session_overview(session_key: str):
    service = build_service()
    return service.get_session_overview(session_key)


def main() -> None:
    st.set_page_config(page_title="F1 Dashboard", layout="wide")
    st.title("F1 Dashboard OpenF1")

    service = build_service()
    years = [2023, 2024, 2025]
    year = st.sidebar.selectbox("Temporada", years)

    meetings = service.list_meetings(year)
    meeting = st.sidebar.selectbox("GP", [m.meeting_name for m in meetings])
    meeting_key = next(m.meeting_key for m in meetings if m.meeting_name == meeting)

    sessions = service.list_sessions(meeting_key)
    session = st.sidebar.selectbox("Sessão", [s.session_name for s in sessions])
    session_key = next(s.session_key for s in sessions if s.session_name == session)

    overview = load_session_overview(session_key)

    st.subheader("Top 10 voltas mais rápidas")
    # render dataframe / tabela

    st.subheader("Resumo da sessão")
    # render cards


if __name__ == "__main__":
    main()
```

### 2) Ajustar dependências em `pyproject.toml`

O plano de engenharia do projeto indica Poetry e Ruff; para a dashboard Streamlit, acrescentar dependências específicas do frontend leve:

- `streamlit` com versão compatível, preferencialmente `<2.0.0`
- `pandas` com pin `<3`
- `python-dotenv` se o projeto usar `.env`

Exemplo de ajuste:

```toml
[tool.poetry.dependencies]
python = "^3.12"
streamlit = "<2.0.0"
pandas = "<3"
python-dotenv = "^1.0.1"
```

Esses ajustes devem ser feitos sem quebrar a estrutura de dependências já apresentada em `.agents/plan.md` (Poetry + dev + docs).

### 3) Garantir a arquitetura correta

A regra de dependência continua válida:

- UI (`dashboard.py`) depende de `domain/services.py`.
- `domain` continua sem depender de infraestrutura.
- `ingestion` e `processing` entregam dados e processamento sem acoplamento ao Streamlit.

Não deve haver import direto de `streamlit` em `domain`, `processing` ou `ingestion`.

### 4) Evitar reescrita do pipeline

A dashboard deve consumir os serviços e repositórios existentes, e não substituir o fluxo analítico principal.

Em outras palavras:

- ETL e pipeline continuam existindo;
- dashboard apenas consulta o serviço de domínio e renderiza resultados;
- alterações devem ser principalmente em:
  - `src/f1/dashboard.py`
  - `pyproject.toml`
  - `docs` de execução local
  - testes mínimos para a UI/composição

### 5) Atualizar docs de execução local

Precisa haver documentação para rodar a dashboard localmente:

- `poetry install --with dev`
- `poetry run streamlit run src/f1/dashboard.py`

Se houver documentação MkDocs, adicionar página de execução local e no `mkdocs.yml` incluir o item relevante.

### 6) Adicionar testes mínimos de dashboard

Não é necessário testar o Streamlit em profundidade. O ideal é validar a composição e o comportamento mínimo:

- teste de criação do serviço (`build_service`)
- teste de montagem do overview por sessão usando mock de serviço
- teste de formatação da tabela de top laps
- teste de ausência de `print` e uso de logger

Exemplo de um teste simples:

```python
from f1.dashboard import build_service


def test_build_service_returns_singleton_like_instance():
    svc1 = build_service()
    svc2 = build_service()
    assert svc1 is svc2
```

## Checklist de execução posterior

### Fase 1 — Ajustes de dependência
- [ ] verificar `pyproject.toml`
- [ ] adicionar `streamlit <2.0.0`
- [ ] ajustar `pandas <3`
- [ ] confirmar `python-dotenv` e config de ambiente

### Fase 2 — Dashboard
- [ ] criar `src/f1/dashboard.py`
- [ ] conectar `HttpClient` + repos + `F1DashboardService`
- [ ] aplicar cache `@st.cache_resource` e `@st.cache_data`
- [ ] renderizar sessão/meeting/year
- [ ] renderizar top laps e cards de resumo

### Fase 3 — Qualidade
- [ ] verificar imports absolutos `from f1...`
- [ ] usar `get_logger(__name__)`
- [ ] manter todas as funções públicas com type hints
- [ ] garantir que não haja `print()`
- [ ] rodar `ruff check .`

### Fase 4 — Testes
- [ ] criar testes unitários mínimos para dashboard
- [ ] rodar `pytest tests/unit/`
- [ ] verificar cobertura ≥ 50%

### Fase 5 — Documentação
- [ ] atualizar docs de execução local
- [ ] atualizar mkdocs nav se necessário
- [ ] confirmar instruções do `README.md`

## Critério de conclusão

O ajuste está completo quando:

- há um `src/f1/dashboard.py` funcional;
- projeto continua respeitando a arquitetura em camadas;
- Streamlit está integrado sem quebrar o pipeline;
- `ruff` e `pytest` passam;
- documentação de execução local está clara;
- não houve reescrita massiva da estrutura já planejada.

## Observação final

Essa correção deve ser tratada como uma expansão do plano existente, e não como um novo projeto. O objetivo é adicionar a camada de apresentação na forma certa, mantendo-se fiel ao que foi já definido em `.agents/plan.md` e ao padrão de engenharia descrito em `.claude/SKILL.md`.
