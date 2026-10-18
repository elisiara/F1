# Pipeline de Telemetria e Cronometragem

Este documento descreve como operar o pipeline analítico de telemetria e cronometragem da Fórmula 1.

---

## 🚀 Como Executar o Pipeline

O pipeline pode ser executado diretamente via linha de comando utilizando o Poetry:

```bash
# Executa o pipeline para a última sessão disponível na OpenF1 API
poetry run python -m f1.pipelines.run_pipeline --session-key latest

# Executa para uma sessão específica informando o ano da temporada
poetry run python -m f1.pipelines.run_pipeline --year 2023 --session-key 9161

# Especifica um piloto exclusivo para a extração de telemetria (ex: Verstappen #1)
poetry run python -m f1.pipelines.run_pipeline --session-key 9161 --driver 1

# Personaliza o diretório de destino dos dados gravados
poetry run python -m f1.pipelines.run_pipeline --session-key 9161 --data-dir meu_data_lake
```

---

## 📊 Parâmetros do CLI

| Parâmetro | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `--year` | `int` | `None` | Ano da temporada. Quando informado, processa também `meetings` e `sessions`. |
| `--session-key` | `str` | `latest` | Chave numérica da sessão ou a string literal `latest`. |
| `--driver` | `int` | `None` | Número permanente do piloto para a ingestão de telemetria detalhada. |
| `--data-dir` | `str` | `data` | Nome da pasta raiz para gravação dos arquivos. |

---

## 📁 Artefatos Gerados no Data Lake Local

Ao término de uma execução com `--session-key 9161` e `--year 2023`, a seguinte estrutura colunar é gerada:

```text
data/
├── raw/
│   ├── meetings_2023.json
│   ├── sessions_2023.json
│   ├── laps_9161.json
│   └── telemetry_9161_driver_1.json
└── processed/
    ├── meetings/year=2023/meetings.parquet
    ├── sessions/year=2023/sessions.parquet
    ├── laps/session_key=9161/laps.parquet
    └── telemetry/session_key=9161/driver=1/telemetry.parquet
```

