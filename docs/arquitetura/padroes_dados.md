# Padrões de Dados e Modelo Dimensional

Este documento descreve a modelagem dimensional dos dados consumidos da OpenF1 API e os padrões de persistência analítica em formato colunar Parquet.

---

## 🏎️ Modelo Conceitual OpenF1

A estrutura de entidades da Fórmula 1 na OpenF1 organiza-se de maneira estritamente hierárquica:

```text
[ Meeting (meeting_key) ] - Grande Prêmio ou evento de testes
       │
       ▼
[ Session (session_key) ] - Treino Livre, Qualificação, Sprint ou Corrida
       │
       ├───▶ [ Driver (driver_number) ] - Cadastro de pilotos na sessão
       │           │
       │           ├──▶ Laps (Voltas e parciais de setores)
       │           └──▶ Car Data (Telemetria a ~3.7 Hz: velocidade, RPM, marcha, acelerador, DRS)
       │
       └───▶ [ Weather ] - Clima e temperaturas de pista/ar
```

---

## 💾 Estratégia de Particionamento Colunar (Parquet)

Para maximizar a eficiência em consultas analíticas e garantir **idempotência de reprocessamento**, os dados tratados (camada Silver) são gravados em formato Apache Parquet seguindo o particionamento em estilo Hive:

| Entidade | Padrão do Caminho no Disco | Justificativa do Particionamento |
| :--- | :--- | :--- |
| **Meetings** | `data/processed/meetings/year={year}/meetings.parquet` | Partição anual por temporada |
| **Sessions** | `data/processed/sessions/year={year}/sessions.parquet` | Partição anual contendo todas as sessões do ano |
| **Laps** | `data/processed/laps/session_key={session_key}/laps.parquet` | Partição por sessão específica (ex: Corrida de Monza) |
| **Telemetry** | `data/processed/telemetry/session_key={session_key}/driver={driver_number}/telemetry.parquet` | Partição composta por sessão e piloto (~3.7 Hz gera alto volume de linhas) |

---

## 🛡️ Idempotência e Reprocessamento

- Executar a extração e transformação repetidas vezes para a mesma chave de partição (`session_key` ou `year`) realiza um **overwrite atômico da partição específica**.
- Isso evita duplicações de registros e assegura que re-execuções produzam sempre o mesmo resultado no destino final.

