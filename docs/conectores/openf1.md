# Conector OpenF1 API

O módulo `f1.connectors.openf1_client` fornece a classe `OpenF1Client`, responsável pelo consumo seguro e resiliente da [OpenF1 API](https://api.openf1.org/v1/).

---

## ⚙️ Características Técnicas

- **Base URL Oficial**: `https://api.openf1.org/v1`
- **Timeouts Obrigatórios**: Cada chamada HTTP possui um timeout explícito configurável (padrão de 15 segundos), prevenindo o travamento indefinido de pipelines.
- **Retries com Backoff Exponencial**: Utiliza `HTTPAdapter` com `urllib3.util.retry.Retry` configurado para retentar automaticamente falhas transitórias nos códigos HTTP `429`, `500`, `502`, `503` e `504`.
- **Tratamento de Exceções**: Todas as falhas de rede (`requests.RequestException`) são interceptadas, registradas no logger e convertidas na exceção semântica `OpenF1ClientError`.

---

## 📋 Catálogo de Métodos do Cliente

```python
from f1.connectors.openf1_client import OpenF1Client

client = OpenF1Client()

# 1. Calendário de Grandes Prêmios
meetings = client.fetch_meetings(year=2023, country_name="Italy")

# 2. Sessões de Pista
sessions = client.fetch_sessions(meeting_key=1219, session_name="Race")

# 3. Pilotos da Sessão
drivers = client.fetch_drivers(session_key=9161)

# 4. Cronometragem Volta a Volta
laps = client.fetch_laps(session_key=9161, driver_number=1)

# 5. Telemetria em Alta Frequência (~3.7 Hz)
telemetry = client.fetch_car_data(session_key=9161, driver_number=1, speed_gte=300.0)

# 6. Meteorologia
weather = client.fetch_weather(session_key=9161)

# 7. Classificação Final Homologada
results = client.fetch_session_results(session_key=9161)
```

---

## 🚨 Tratamento de Erros

Caso a API retorne um status code de erro ou a conexão falhe após o número máximo de retries configurados:

```python
from f1.connectors.openf1_client import OpenF1Client, OpenF1ClientError

client = OpenF1Client(timeout_seconds=5, max_retries=2)

try:
    sessions = client.fetch_sessions(year=2023)
except OpenF1ClientError as exc:
    # Registra o incidente sem vazar dados sensíveis
    print(f"Erro capturado pelo pipeline: {exc}")
```

