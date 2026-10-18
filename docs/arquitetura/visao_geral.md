# Arquitetura do Sistema e Fluxo de Dados

A arquitetura do projeto adota o padrão canônico **`src/` Layout**, promovendo isolamento estrito de responsabilidades e direção unidirecional de dependências.

---

## 🏗️ Camadas da Aplicação

```mermaid
flowchart TD
    subgraph External ["Fontes Externas"]
        API["OpenF1 REST API (v1)"]
    end

    subgraph Core ["Pacote src/f1"]
        Config["config/settings.py<br/>(Settings imutável com caminhos Pathlib)"]
        Domain["domain/models.py<br/>(Dataclasses tipadas e contratos)"]
        Utils["utils/logging_utils.py<br/>(Logger sem print)"]

        subgraph IO_Layer ["Camada de I/O"]
            Connector["connectors/openf1_client.py<br/>(OpenF1Client com Retry e Timeouts)"]
        end

        subgraph Transformations ["Transformações Puras (Zero I/O)"]
            T_Sessions["transformations/sessions.py"]
            T_Laps["transformations/laps.py"]
            T_Telemetry["transformations/telemetry.py"]
        end

        subgraph Services ["Orquestração de Negócios"]
            Service["services/f1_service.py<br/>(F1DataService)"]
        end

        subgraph Entrypoints ["Pontos de Entrada"]
            CLI["pipelines/run_pipeline.py<br/>(CLI com argparse)"]
        end
    end

    subgraph Storage ["Data Lake Local"]
        Bronze["data/raw/ (JSON)"]
        Silver["data/processed/ (Parquet Particionado)"]
    end

    API -->|HTTP GET com Retry| Connector
    Config -.-> Connector
    Config -.-> Service
    Utils -.-> Connector
    Utils -.-> Service
    Connector --> Service
    Service --> Bronze
    Service --> Domain
    Service --> Transformations
    Transformations --> Service
    Service --> Silver
    CLI --> Service
```

---

## 🔒 Regras de Isolamento e Fronteiras Modulares

1. **Transformações Puras (Zero I/O)**:
   - Funções sob `src/f1/transformations/` são 100% determinísticas e puras.
   - Proibido importar bibliotecas de rede (`requests`, `urllib3`) ou realizar operações em disco dentro das transformações.
2. **Conectores Especializados**:
   - Módulos sob `src/f1/connectors/` cuidam exclusivamente de transporte de rede, timeouts explícitos, retries exponenciais e mapeamento de erros HTTP para exceções de domínio (`OpenF1ClientError`).
3. **Modelos de Domínio Tipados**:
   - `src/f1/domain/models.py` define dataclasses imutáveis para as entidades do ecossistema da Fórmula 1 (Meeting, Session, Driver, Lap, TelemetrySample, WeatherSample).
4. **Camada de Serviços (Coordenação)**:
   - `F1DataService` orquestra a extração de dados brutos, a aplicação das transformações e a persistência idempotente colunar em Parquet.
5. **Ausência de Efeitos Colaterais na Importação**:
   - Nenhum módulo dispara conexões de rede ou cria arquivos no momento em que é importado.

