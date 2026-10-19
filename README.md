# 🏎️ Engenharia de Dados Fórmula 1 (OpenF1 Pipeline)

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/badge/linter%20%26%20formatter-ruff-orange.svg)](https://astral.sh/ruff)
[![Pytest](https://img.shields.io/badge/tests-pytest%20(93%25%20cov)-green.svg)](https://docs.pytest.org/)
[![MkDocs Material](https://img.shields.io/badge/docs-mkdocs%20material-red.svg)](https://squidfunk.github.io/mkdocs-material/)

Pipeline robusto, modular e tipado de **Engenharia de Dados** para ingestão, validação contratual, transformações analíticas puras e persistência colunar particionada de dados históricos e telemetria da **Fórmula 1**, consumindo a [OpenF1 REST API (v1)](https://api.openf1.org/v1/).

---

## 🏛️ Arquitetura e Estrutura do Projeto

O projeto adota rigorosamente a arquitetura de **Layout `src/`**, garantindo separação inegociável entre camadas de rede/IO, contratos de domínio, transformações puras e orquestração.

```text
.
├── pyproject.toml              # Metadados, dependências e configurações oficiais
├── poetry.lock                 # Lockfile com resolução exata de dependências
├── mkdocs.yml                  # Configuração da documentação técnica MkDocs
├── .env.example                # Modelo de variáveis de ambiente
├── src/
│   └── f1/                     # Pacote principal da aplicação
│       ├── __init__.py
│       ├── dashboard.py        # composition root Streamlit
        ├── config/             # Configurações imutáveis e paths tipados (Settings)
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── domain/             # Dataclasses imutáveis e schemas (Meeting, Session, Lap...)
│       │   ├── __init__.py
│       │   └── models.py
│       ├── connectors/         # I/O puro e resiliente com retries exponenciais e timeouts
│       │   ├── __init__.py
│       │   └── openf1_client.py
│       ├── transformations/    # Transformações puras, determinísticas e sem I/O
│       │   ├── __init__.py
│       │   ├── sessions.py
│       │   ├── laps.py
│       │   └── telemetry.py
│       ├── services/           # Orquestração do ciclo E-V-T-L e escrita Parquet
│       │   ├── __init__.py
│       │   └── f1_service.py
│       ├── pipelines/          # CLI executável com argparse
│       │   ├── __init__.py
│       │   └── run_pipeline.py
│       └── utils/              # Logging estruturado sem uso de print()
│           ├── __init__.py
│           └── logging_utils.py
├── tests/
│   ├── conftest.py             # Fixtures globais com payloads mockados
│   └── unit/                   # Testes unitários puros com 93% de cobertura
│       ├── test_config.py
│       ├── test_domain.py
│       ├── test_connectors.py
│       ├── test_transformations.py
│       ├── test_services.py
│       └── test_pipelines.py
└── docs/                       # Documentação técnica viva MkDocs Material
    ├── index.md
    ├── arquitetura/
    │   ├── visao_geral.md
    │   └── padroes_dados.md
    ├── conectores/
    │   └── openf1.md
    ├── pipelines/
    │   └── telemetria.md
    └── desenvolvimento/
        ├── setup.md
        └── qualidade.md
```

---

## ⚡ Guia Rápido de Instalação

### Pré-requisitos
- Python `>= 3.12`
- Poetry `>= 2.0`

> ⚠️ **Importante**: Conforme a política do projeto, **não utilize `pip install`**. Todas as dependências devem ser gerenciadas pelo Poetry.

```bash
# 1. Instalar todas as dependências declaradas no lockfile
poetry install

# 2. Conferir informações do ambiente virtual
poetry env info
```

---

## 🚀 Execução do Pipeline

O pipeline pode ser executado via CLI através do Poetry:

```bash
# Executa para a última sessão disponível na OpenF1
poetry run python -m f1.pipelines.run_pipeline --session-key latest

# Executa para uma temporada e sessão específica
poetry run python -m f1.pipelines.run_pipeline --year 2023 --session-key 9161

# Especifica um piloto para telemetria em alta frequência (ex: Verstappen #1)
poetry run python -m f1.pipelines.run_pipeline --session-key 9161 --driver 1

# Ajuda e listagem de argumentos
poetry run python -m f1.pipelines.run_pipeline --help
```

### 💾 Estrutura de Particionamento (Data Lake Local)

Os dados processados são gravados de forma colunar e particionada no diretório `data/`:

- **Bronze (Raw JSON)**: `data/raw/{entidade}_{id}.json`
- **Silver (Parquet Particionado)**:
  - `data/processed/meetings/year={year}/meetings.parquet`
  - `data/processed/sessions/year={year}/sessions.parquet`
  - `data/processed/laps/session_key={session_key}/laps.parquet`
  - `data/processed/telemetry/session_key={session_key}/driver={driver_number}/telemetry.parquet`

---

## 🧪 Qualidade, Linting e Testes

Todos os critérios de qualidade são garantidos por automações:

```bash
# Executar a suíte de testes com cobertura mínima obrigatória de 50% (atual: >90%)
poetry run pytest

# Executar linter e organizador de imports
poetry run ruff check .

# Verificar formatação estrita
poetry run ruff format --check .

# Compilar documentação técnica em modo estrito
poetry run mkdocs build --strict
```

# Como executar a dashboard localmente

1. Instalar dependências:
   poetry install --with dev

2. Rodar a dashboard:
   poetry run streamlit run src/f1/dashboard.py

---

## 📖 Documentação Completa

Para navegar pela documentação técnica interativa:

```bash
poetry run mkdocs serve
```
Acesse no navegador: `http://127.0.0.1:8000`
