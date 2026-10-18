# Plano de Implementação: Projeto de Engenharia de Dados F1 (OpenF1 Pipeline)

## 1. Visão Geral e Objetivos

O objetivo deste projeto é construir uma solução robusta, modular, tipada e orientada a boas práticas de **Engenharia de Dados** para ingestão, validação, transformação analítica e persistência de dados históricos e de telemetria da **Fórmula 1**, utilizando a [OpenF1 API](https://api.openf1.org/v1/) como fonte de dados.

O projeto segue rigorosamente o padrão de engenharia definido em [`SKILL.md`](./SKILL.md) e as especificações de dados de [`doc_api.md`](./doc_api.md):
- **Arquitetura `src/` Layout** com separação estrita de responsabilidades:
  - Conectores puros de I/O (`connectors/`) com tratamento resiliente de erros, retries exponenciais e timeouts obrigatórios;
  - Transformações puras e determinísticas (`transformations/`) com zero I/O;
  - Modelos de domínio e contratos fortemente tipados (`domain/`);
  - Serviços de negócio orquestradores (`services/`) e pontos de entrada executáveis (`pipelines/`);
  - Configurações centralizadas (`config/`) e utilitários técnicos (`utils/`).
- **Padrão de Dados (E-V-T-L)**: Extração (API OpenF1) ➔ Validação de Contrato ➔ Transformação Pura ➔ Carga (Armazenamento colunar particionado em Parquet).
- **Padrão de Qualidade Rigoroso**:
  - Linter e Formatação com **Ruff** (0 erros e 100% de conformidade com estilo PEP 8);
  - Testes unitários com **Pytest** e isolamento total de I/O via mocks;
  - Cobertura de testes mínima obrigatória de **50%** garantida por `pytest-cov`;
  - Documentação técnica viva com **MkDocs Material** compilada sem avisos (`mkdocs build --strict`).

---

## 2. Arquitetura do Sistema e Fluxo de Dados

```mermaid
flowchart TD
    subgraph External ["Fonte de Dados Externa"]
        API["OpenF1 REST API (v1)<br/>/meetings, /sessions, /drivers, /laps, /car_data, /weather"]
    end

    subgraph Core ["Pacote src/f1"]
        Config["config/settings.py<br/>(Settings, Paths, URLs, Timeouts)"]
        Domain["domain/models.py<br/>(Dataclasses, Schemas e Tipos)"]
        Utils["utils/logging_utils.py<br/>(Logger Estruturado)"]

        subgraph IO_Layer ["Camada de I/O"]
            Connector["connectors/openf1_client.py<br/>(OpenF1Client + Backoff + Timeouts)"]
        end

        subgraph Pure_Transformations ["Transformações Puras (Zero I/O)"]
            T_Sessions["transformations/sessions.py"]
            T_Laps["transformations/laps.py"]
            T_Telemetry["transformations/telemetry.py"]
        end

        subgraph Service_Layer ["Orquestração de Negócio"]
            Service["services/f1_service.py<br/>(Coordena Extração, Validação e Transformação)"]
        end

        subgraph Entrypoints ["Pontos de Entrada"]
            CLI["pipelines/run_pipeline.py<br/>(CLI de Execução do Pipeline)"]
        end
    end

    subgraph Storage ["Camada de Armazenamento (Data Lake Local)"]
        Bronze["data/raw/ (JSON/Payloads brutos)"]
        Silver["data/processed/ (Parquet particionado por ano/sessão)"]
    end

    API -->|HTTP GET com Timeout| Connector
    Config -.-> Connector
    Config -.-> Service
    Utils -.-> Connector
    Utils -.-> Service
    
    Connector -->|Dados Brutos list[dict]| Service
    Service -->|Salva Raw Opcional| Bronze
    
    Service -->|Aplica Contratos| Domain
    Service -->|Delega Dados| T_Sessions
    Service -->|Delega Dados| T_Laps
    Service -->|Delega Dados| T_Telemetry
    
    T_Sessions -->|Dados Limpos| Service
    T_Laps -->|Dados Limpos| Service
    T_Telemetry -->|Dados Limpos| Service
    
    Service -->|Gravação Idempotente Parquet| Silver
    CLI -->|Executa| Service
```

### Direção de Dependências e Princípios Arquiteturais:
1. `transformations` **nunca** importa `connectors`, `services` ou `pipelines`.
2. `domain` contém apenas tipos, dataclasses e contratos sem dependências de infraestrutura.
3. `connectors` cuida unicamente de comunicação de rede, tratamento de códigos HTTP e retries, sem lógica analítica.
4. `services` realiza a ponte entre I/O e transformações, garantindo atomicidade e persistência.

---

## 3. Decisões Técnicas e Dependências

> [!IMPORTANT]
> **Adição de Dependências de Produção ao `pyproject.toml`**  
> Para viabilizar a extração HTTP resiliente e a persistência colunar analítica (Parquet), propõe-se adicionar as seguintes bibliotecas oficiais no grupo de produção:
> - `requests = "^2.32.0"`: Cliente HTTP síncrono padrão;
> - `urllib3 = "^2.2.0"`: Configuração de pool de conexões e estratégias de Retry com backoff;
> - `pandas = "^2.2.0"` e `pyarrow = "^18.0.0"`: Manipulação tabular vetorizada e exportação em formato colunar Parquet particionado.
>
> *(Nota: Conforme a SKILL.md, estas adições devem ser gerenciadas via Poetry).*

> [!NOTE]
> **Estratégia de Persistência e Particionamento**  
> A persistência padrão será em arquivos **Parquet** particionados sob o diretório `data/processed/`, seguindo a hierarquia dimensional do OpenF1:
> - `data/processed/meetings/year={year}/meetings.parquet`
> - `data/processed/sessions/year={year}/sessions.parquet`
> - `data/processed/laps/session_key={session_key}/laps.parquet`
> - `data/processed/telemetry/session_key={session_key}/driver={driver_number}/telemetry.parquet`
> Essa estrutura permite reprocessamento idempotente (*overwrite* por partição) e consultas analíticas de alta performance.

---

## 4. Questões Abertas e Alinhamentos

1. **Escopo Inicial de Ingestão**: Deseja focar inicialmente no ciclo completo de **Sessões + Voltas (Laps) + Telemetria de Carro (Car Data)** de um GP específico (ex: GP da Itália / Monza 2023 ou última sessão disponível `session_key=latest`), expandindo posteriormente para clima, pit stops e ultrapassagens?
2. **Formato de Carga**: O formato Parquet particionado atende perfeitamente aos requisitos da pós-graduação, ou você gostaria de incluir também um banco analítico local embutido como **DuckDB**?

---

## 5. Plano de Mudanças e Fases de Implementação

A implementação será executada em fases incrementais, respeitando o ciclo de desenvolvimento: **Código ➔ Testes ➔ Ruff Check/Format ➔ Pytest com Cov ➔ MkDocs Build**.

---

### Fase 1: Configuração do Ambiente e Dependências

#### [MODIFY] `pyproject.toml`
- Adicionar dependências principais:
  ```toml
  [project]
  dependencies = [
      "requests>=2.32.0",
      "urllib3>=2.2.0",
      "pandas>=2.2.0",
      "pyarrow>=18.0.0",
  ]
  ```
- Manter regras existentes de `ruff`, `pytest` (cobertura mínima de 50%) e grupos `dev` e `docs`.

#### [NEW] `.env.example`
- Modelo de variáveis de ambiente do projeto (base URL da API, log level, timeouts, diretórios de dados).

---

### Fase 2: Configuração Centralizada e Utilitários de Log

#### [NEW] `src/f1/config/settings.py`
- Classe de configuração imutável baseada em `dataclass` ou propriedades tipadas:
  - `OPENF1_BASE_URL`: URL base (padrão: `https://api.openf1.org/v1`);
  - `REQUEST_TIMEOUT_SECONDS`: Padrão de 15 segundos;
  - `MAX_RETRIES`: Padrão de 3 tentativas;
  - `DATA_DIR`: Caminho raiz de dados gerenciado com `pathlib.Path`.

#### [NEW] `src/f1/utils/logging_utils.py`
- Utilitário unificado de logging com formatação limpa e níveis semânticos (`INFO`, `DEBUG`, `WARNING`, `ERROR`).
- Proibição estrita de uso de `print()`.

---

### Fase 3: Modelos de Domínio e Contratos

#### [NEW] `src/f1/domain/models.py`
- Contratos de dados e Dataclasses tipadas para entidades centrais da API:
  - `Meeting`: Detalhes do Grande Prêmio/evento (`meeting_key`, `circuit_short_name`, `country_name`, `year`);
  - `Session`: Sessão de treino, quali ou corrida (`session_key`, `meeting_key`, `session_name`, `date_start`);
  - `Driver`: Cadastro de piloto na sessão (`driver_number`, `full_name`, `name_acronym`, `team_name`, `team_colour`);
  - `Lap`: Métricas de volta (`session_key`, `driver_number`, `lap_number`, `lap_duration`, `duration_sector_1..3`, `is_pit_out_lap`);
  - `TelemetrySample`: Amostra de telemetria ~3.7Hz (`date`, `driver_number`, `speed`, `rpm`, `n_gear`, `throttle`, `brake`, `drs`);
  - `WeatherSample`: Condições meteorológicas (`air_temperature`, `track_temperature`, `humidity`, `rainfall`).

---

### Fase 4: Conector HTTP Resiliente (OpenF1 API)

#### [NEW] `src/f1/connectors/openf1_client.py`
- Implementação de `OpenF1Client` utilizando sessão com `HTTPAdapter` e `Retry` (`urllib3.util.retry.Retry`) com backoff exponencial para códigos 429, 500, 502, 503, 504.
- Métodos explícitos e tipados:
  - `fetch_meetings(year: int | None = None) -> list[dict[str, Any]]`
  - `fetch_sessions(meeting_key: int | str | None = None, year: int | None = None) -> list[dict[str, Any]]`
  - `fetch_drivers(session_key: int | str) -> list[dict[str, Any]]`
  - `fetch_laps(session_key: int | str, driver_number: int | None = None) -> list[dict[str, Any]]`
  - `fetch_car_data(session_key: int | str, driver_number: int, speed_gte: float | None = None) -> list[dict[str, Any]]`
  - `fetch_weather(meeting_key: int | str | None = None, session_key: int | str | None = None) -> list[dict[str, Any]]`
  - `fetch_session_results(session_key: int | str) -> list[dict[str, Any]]`
- Exceção customizada `OpenF1ClientError`.

---

### Fase 5: Transformações Puras (Zero I/O)

#### [NEW] `src/f1/transformations/sessions.py`
- Limpeza e parsing de sessões:
  - Normalização de timestamps UTC ISO 8601;
  - Filtro por tipo de sessão (`Race`, `Qualifying`, `Practice`);
  - Ordenação cronológica.

#### [NEW] `src/f1/transformations/laps.py`
- Validação e saneamento de voltas:
  - `filter_valid_laps`: Descarte de voltas nulas, sem tempo ou out-laps;
  - Identificação de voltas mais rápidas por piloto e geral;
  - Interpretação semântica dos mini-setores (`2048` = Amarelo, `2049` = Verde, `2051` = Roxo);
  - Cálculo de deltas entre voltas consecutivas.

#### [NEW] `src/f1/transformations/telemetry.py`
- Processamento determinístico de telemetria:
  - `calculate_speed_kph`: Conversão e validação física de velocidade;
  - `parse_drs_status`: Mapeamento do código numérico de DRS para status legível (`CLOSED`, `DETECTED`, `OPEN`);
  - `calculate_throttle_brake_percentages`: Validação de faixas `[0, 100]`;
  - Agregações estatísticas (velocidade máxima no speed trap, média de rotações, porcentagem de volta de pé cravado).

---

### Fase 6: Camada de Serviços e Persistência Colunar

#### [NEW] `src/f1/services/f1_service.py`
- Serviço coordenador `F1DataService`:
  - Recebe o `OpenF1Client` injetado via dependência;
  - Executa a extração dos dados de uma sessão ou GP;
  - Aplica as transformações puras;
  - Grava os dados tratados em formato Parquet particionado de maneira idempotente com `pyarrow` / `pandas`;
  - Garante logs estruturados de cada etapa (início, volume de registros, tempo decorrido, erros descartados).

---

### Fase 7: Ponto de Entrada Executável (CLI Pipeline)

#### [NEW] `src/f1/pipelines/run_pipeline.py`
- Entrypoint CLI executável via `poetry run python -m f1.pipelines.run_pipeline`:
  - Suporte a parâmetros via `argparse`:
    - `--year`: Ano da temporada (ex: 2023, 2024);
    - `--session-key`: Chave específica da sessão ou `latest`;
    - `--driver`: Número do piloto para extração de telemetria;
    - `--output-dir`: Diretório de saída customizado;
  - Tratamento elegante de exceções de saída com códigos de retorno adequados (`0` para sucesso, `1` para falha).

---

### Fase 8: Testes Unitários e Fixtures (Pytest + Cobertura >= 50%)

#### [NEW] `tests/conftest.py`
- Fixtures com payloads JSON mockados representativos da OpenF1 API:
  - `mock_sessions_response`
  - `mock_laps_response`
  - `mock_car_data_response`
  - Instância do cliente configurada com URLs de teste.

#### [NEW] `tests/unit/test_config.py`
- Validação do carregamento de configurações e diretórios padrão.

#### [NEW] `tests/unit/test_connectors.py`
- Testes unitários do `OpenF1Client` isolados com `unittest.mock.patch`:
  - Sucesso na chamada de sessões e voltas;
  - Comportamento em caso de erro HTTP 404, 500 e timeout (`OpenF1ClientError`);
  - Validação de passagem correta dos parâmetros de query.

#### [NEW] `tests/unit/test_transformations.py`
- Testes unitários completos e parametrizados (`@pytest.mark.parametrize`):
  - Conversões de velocidade e exceções em valores negativos;
  - Mapeamento de status DRS;
  - Filtragem de voltas válidas e descarte de voltas de pit/nulas;
  - Casos de borda: payloads vazios, tipos inconsistentes, tempos zerados.

#### [NEW] `tests/unit/test_services.py`
- Teste de orquestração do serviço utilizando mocks do conector e validação da escrita de arquivos temporários em Parquet.

---

### Fase 9: Documentação Técnica Completa (MkDocs Material)

#### [NEW] `mkdocs.yml`
- Configuração oficial do MkDocs Material conforme o padrão do `SKILL.md` (tema `material`, cores F1 racing red/slate, suporte a blocos de código com cópia, admonitions e mermaid).

#### [NEW] `docs/index.md`
- Apresentação geral do projeto, escopo acadêmico, objetivos e tecnologias.

#### [NEW] `docs/arquitetura/visao_geral.md`
- Diagrama arquitetural C4 / fluxo de dados e separação estrita de camadas.

#### [NEW] `docs/arquitetura/padroes_dados.md`
- Modelo dimensional OpenF1 (Meeting ➔ Session ➔ Driver ➔ Laps / Car Data) e padrões Parquet.

#### [NEW] `docs/conectores/openf1.md`
- Detalhes de integração com a OpenF1 API, endpoints suportados, política de retries e timeouts.

#### [NEW] `docs/pipelines/telemetria.md`
- Guia operacional de execução do pipeline e catálogo dos datasets gerados.

#### [NEW] `docs/desenvolvimento/setup.md`
- Guia para desenvolvedores: clonagem, instalação com Poetry e boas práticas.

#### [NEW] `docs/desenvolvimento/qualidade.md`
- Comandos obrigatórios de lint (`ruff`), formatação, suíte de testes (`pytest`) e build da documentação (`mkdocs build --strict`).

---

### Fase 10: Apresentação e README

#### [MODIFY] `README.md`
- Readme profissional e completo contendo:
  - Badge e resumo do projeto;
  - Tecnologias e ferramentas;
  - Instruções rápidas de instalação via Poetry;
  - Exemplos de comandos para rodar o pipeline;
  - Como rodar os linters e suíte de testes.

---

## 6. Plano de Verificação (Verification Plan)

A validação de cada etapa obedecerá aos critérios estritos da Seção 10 do `SKILL.md`:

### 1. Testes Automatizados e Cobertura
```bash
# Execução da suíte completa de testes com checagem de cobertura mínima de 50%
poetry run pytest

# Execução detalhada com linhas faltantes caso necessário
poetry run pytest -v --cov-report=term-missing
```

### 2. Linting e Formatação de Código
```bash
# Checagem de regras de linter e ordenação de imports
poetry run ruff check .

# Checagem estrita de formatação (sem alterações pendentes)
poetry run ruff format --check .
```

### 3. Validação Estrita da Documentação
```bash
# Build estrito da documentação MkDocs (qualquer link quebrado ou erro sintático falha o build)
poetry run mkdocs build --strict
```

### 4. Verificação Manual do Pipeline
```bash
# Execução de teste do pipeline CLI para a última sessão disponível
poetry run python -m f1.pipelines.run_pipeline --session-key latest

# Inspeção dos arquivos Parquet gerados no diretório data/processed/
ls -lh data/processed/
```

