# OpenF1 API — Documentação Resumida

> **Fonte Oficial:** [openf1.org/docs](https://openf1.org/docs/)  
> **Repositório:** [github.com/br-g/openf1](https://github.com/br-g/openf1)  
> **Base URL:** `https://api.openf1.org/v1/`

---

## 1. Visão Geral

A **OpenF1** é uma API aberta e gratuita que disponibiliza telemetria em alta frequência, cronometragem, dinâmica de pista e dados históricos da **Fórmula 1** em formatos **JSON** (padrão) e **CSV**.

### Principais Características
- **Acesso Gratuito**: Dados históricos (a partir da temporada de **2023**) são públicos e **não exigem autenticação** ou API Key.
- **Dados em Tempo Real**: Sessões ao vivo exigem subscrição paga via token.
- **Frequência de Amostragem**:
  - Telemetria de carro (`car_data`) e coordenadas de rastreamento (`location`): ~**3.7 Hz**.
  - Intervalos entre carros (`intervals`): ~**4 segundos** (durante corridas).
  - Meteorologia (`weather`): a cada **1 minuto**.
- **Chave Dinâmica `latest`**: Pode-se usar o valor literal `latest` nos parâmetros `session_key` ou `meeting_key` para buscar automaticamente a última sessão ou evento registrado.

---

## 2. Filtragem e Formatação de Dados

### 2.1. Filtros por Atributo e Operadores de Comparação
Qualquer atributo retornado pelo endpoint (com exceção de arrays aninhados) pode ser utilizado como filtro na *query string* da URL.

| Operador | URL Codificada / Exemplo | Descrição |
| :--- | :--- | :--- |
| `=` | `driver_number=55` | Igualdade estrita |
| `>=` | `speed>=315` ou `speed%3E%3D315` | Maior ou igual |
| `<=` | `position<=3` ou `position%3C%3D3` | Menor ou igual |
| `>` | `lap_duration>90` | Estritamente maior |
| `<` | `tyre_age_at_start<10` | Estritamente menor |

*Exemplo combinado:*
```bash
https://api.openf1.org/v1/laps?session_key=9222&driver_number=55&is_pit_out_lap=true&lap_duration>=120
```

### 2.2. Filtro Temporal (Time-based Filtering)
Os parâmetros de data suportam intervalos e aceitam qualquer formato compatível com o parser ISO 8601 (como `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SS` ou com fuso UTC/offset).

```bash
https://api.openf1.org/v1/sessions?date_start>=2023-09-01&date_end<=2023-09-30
```

### 2.3. Exportação para CSV
Para receber os dados tabulares em formato CSV em vez de JSON, basta adicionar o parâmetro `csv=true`:
```bash
https://api.openf1.org/v1/sessions?year=2023&csv=true
```

---

## 3. Modelo de Dados e Chaves Relacionais

Para fins de Engenharia de Dados e modelagem dimensional/relacional, a API orbita em torno de 3 entidades centrais:

```
[ Meeting (meeting_key) ]
         │
         ▼
[ Session (session_key) ]
         │
         ├───▶ [ Driver (driver_number) ]
         │           │
         │           ├──▶ Laps, Stints, Pit, Position, Intervals, Overtakes
         │           └──▶ Car Data, Location (Telemetria 3.7Hz)
         │
         └───▶ [ Race Control, Weather ]
```

- **`meeting_key`**: Identificador do fim de semana de GP ou sessão de testes (ex: GP da Itália).
- **`session_key`**: Identificador da atividade de pista (ex: Treino Livre 1, Qualificação, Corrida).
- **`driver_number`**: Número permanente do piloto na temporada (ex: `1` para Verstappen, `44` para Hamilton, `16` para Leclerc).

---

## 4. Catálogo Detalhado de Endpoints

### 4.1. Calendário e Sessões

#### `/v1/meetings`
Retorna dados de Grandes Prêmios e testes coletivos de pré-temporada.
- **Atributos principais:** `meeting_key`, `meeting_name`, `meeting_official_name`, `year`, `location`, `country_name`, `country_code`, `circuit_key`, `circuit_short_name`, `circuit_type`, `date_start`, `date_end`, `gmt_offset`, `circuit_image`, `circuit_info_url`.
- **Exemplo:** `https://api.openf1.org/v1/meetings?year=2024&country_name=Monaco`

#### `/v1/sessions`
Retorna as sessões individuais associadas a cada evento.
- **Atributos principais:** `session_key`, `meeting_key`, `session_name` (`Practice 1`, `Qualifying`, `Sprint`, `Race`), `session_type`, `date_start`, `date_end`, `gmt_offset`, `location`, `circuit_key`, `year`.
- **Exemplo:** `https://api.openf1.org/v1/sessions?country_name=Belgium&session_name=Race&year=2023`

---

### 4.2. Pilotos e Campeonatos

#### `/v1/drivers`
Dados cadastrais dos pilotos participantes em determinada sessão.
- **Atributos principais:** `driver_number`, `session_key`, `meeting_key`, `full_name`, `first_name`, `last_name`, `name_acronym` (ex: `VER`, `HAM`), `broadcast_name`, `team_name`, `team_colour` (código hexadecimal da cor da equipe, ex: `3671C6`), `headshot_url` (foto de perfil).
- **Exemplo:** `https://api.openf1.org/v1/drivers?session_key=latest`

#### `/v1/championship_drivers` *(Beta)*
Classificação e pontuação do campeonato de pilotos antes e depois de cada corrida.
- **Atributos principais:** `driver_number`, `session_key`, `meeting_key`, `position_start`, `position_current`, `points_start`, `points_current`.
- **Exemplo:** `https://api.openf1.org/v1/championship_drivers?session_key=9839`

#### `/v1/championship_teams` *(Beta)*
Classificação e pontuação do campeonato de construtores.
- **Atributos principais:** `team_name`, `session_key`, `meeting_key`, `position_start`, `position_current`, `points_start`, `points_current`.
- **Exemplo:** `https://api.openf1.org/v1/championship_teams?session_key=9839`

---

### 4.3. Classificação, Grid e Voltas

#### `/v1/starting_grid`
Grid de largada confirmado para a corrida.
- **Atributos principais:** `session_key`, `meeting_key`, `driver_number`, `position`, `lap_duration`.
- **Exemplo:** `https://api.openf1.org/v1/starting_grid?session_key=latest&position<=10`

#### `/v1/session_result`
Resultado final oficial publicado após a conclusão da sessão.
- **Atributos principais:** `position`, `driver_number`, `session_key`, `meeting_key`, `number_of_laps`, `duration` (tempo total de corrida ou melhor volta no treino/quali), `gap_to_leader`, `dnf` (Did Not Finish), `dns` (Did Not Start), `dsq` (Desclassificado).
- **Exemplo:** `https://api.openf1.org/v1/session_result?session_key=latest&position<=3`

#### `/v1/laps`
Dados completos de tempos volta a volta de cada piloto.
- **Atributos principais:** `session_key`, `meeting_key`, `driver_number`, `lap_number`, `lap_duration`, `duration_sector_1`, `duration_sector_2`, `duration_sector_3`, `i1_speed` (velocidade no intermediário 1), `i2_speed`, `st_speed` (velocidade no Speed Trap), `is_pit_out_lap`, `date_start`, `segments_sector_1`, `segments_sector_2`, `segments_sector_3`.
- **Exemplo:** `https://api.openf1.org/v1/laps?session_key=9161&driver_number=63&lap_number=8`

> **Mapeamento de Cores dos Mini-Setores (`segments_sector_1..3`):**
> | Código numérico | Significado / Cor |
> | :--- | :--- |
> | `0` | Não disponível |
> | `2048` | **Amarelo** (Setor mais lento que a sua própria melhor marca) |
> | `2049` | **Verde** (Melhor marca pessoal no setor) |
> | `2051` | **Roxo** (Melhor marca absoluta de toda a sessão) |
> | `2064` | Pit lane |

---

### 4.4. Estratégia de Pneus e Boxes

#### `/v1/stints`
Segmentos contínuos de uso de um jogo de pneus na pista.
- **Atributos principais:** `driver_number`, `session_key`, `meeting_key`, `stint_number`, `compound` (`SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET`), `tyre_age_at_start` (voltas acumuladas pelo jogo antes do stint), `lap_start`, `lap_end`.
- **Exemplo:** `https://api.openf1.org/v1/stints?session_key=9165`

#### `/v1/pit`
Registros de passagens pelo pit lane.
- **Atributos principais:** `session_key`, `meeting_key`, `driver_number`, `lap_number`, `date`, `stop_duration` (tempo do carro parado trocando pneus; disponível a partir de US GP 2024), `lane_duration` (tempo total gasto trafegando pelo pit lane).
- **Exemplo:** `https://api.openf1.org/v1/pit?session_key=9877`

---

### 4.5. Dinâmica de Corrida em Tempo Real

#### `/v1/position`
Evolução da posição do piloto em pista e mudanças ao longo da sessão.
- **Atributos principais:** `date`, `driver_number`, `session_key`, `meeting_key`, `position`.
- **Exemplo:** `https://api.openf1.org/v1/position?session_key=latest&driver_number=4`

#### `/v1/intervals`
Diferenças de tempo entre competidores durante as corridas (~4s de atualização).
- **Atributos principais:** `date`, `driver_number`, `session_key`, `meeting_key`, `interval` (diferença em segundos para o carro à frente ou `+1 LAP`), `gap_to_leader` (diferença em segundos para o líder ou `null` para o líder).
- **Exemplo:** `https://api.openf1.org/v1/intervals?session_key=9165`

#### `/v1/overtakes`
Registros de ultrapassagens confirmadas em pista.
- **Atributos principais:** `date`, `session_key`, `meeting_key`, `overtaking_driver_number` (piloto que ultrapassou), `overtaken_driver_number` (piloto ultrapassado), `position` (nova posição conquistada).
- **Exemplo:** `https://api.openf1.org/v1/overtakes?session_key=9636&position=1`

---

### 4.6. Telemetria e Rastreamento Cartesiano (~3.7 Hz)

#### `/v1/car_data`
Métricas dos sensores do carro em alta frequência.
- **Atributos principais:** `date`, `driver_number`, `session_key`, `meeting_key`, `speed` (km/h), `rpm` (rotações do motor), `n_gear` (marcha engatada: 1 a 8), `throttle` (aceleração de 0 a 100%), `brake` (pressão/acionamento de freio: 0 ou 100), `drs` (código de status do sistema DRS).
- **Exemplo:** `https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=300`

> **Tabela de Interpretação dos Estados do DRS:**
> | Valor DRS | Estado |
> | :--- | :--- |
> | `0` ou `1` | DRS Fechado / Desligado |
> | `8` | DRS Detectado (permitido acionamento na zona de ativação) |
> | `10`, `12`, `14` | DRS Aberto / Ativo |

#### `/v1/location`
Coordenadas espaciais 3D aproximadas dos carros no circuito.
- **Atributos principais:** `date`, `driver_number`, `session_key`, `meeting_key`, `x`, `y`, `z` (coordenadas cartesianas da pista).
- **Exemplo:** `https://api.openf1.org/v1/location?session_key=9161&driver_number=81`

---

### 4.7. Direção de Prova, Rádio e Clima

#### `/v1/race_control`
Mensagens emitidas pela direção de prova (FIA Race Control).
- **Atributos principais:** `date`, `session_key`, `meeting_key`, `category` (`Flag`, `SafetyCar`, `Drs`, `CarEvent`, `SessionStatus`), `flag` (`GREEN`, `YELLOW`, `DOUBLE YELLOW`, `RED`, `CHEQUERED`), `scope` (`Track`, `Sector`, `Driver`), `sector`, `qualifying_phase`, `driver_number`, `message`.
- **Exemplo:** `https://api.openf1.org/v1/race_control?flag=RED`

#### `/v1/team_radio`
Gravações de áudio dos rádios entre piloto e engenheiro de pista.
- **Atributos principais:** `date`, `session_key`, `meeting_key`, `driver_number`, `recording_url` (link para download/stream do arquivo de áudio em formato `.mp3` / `.wav`).
- **Exemplo:** `https://api.openf1.org/v1/team_radio?session_key=9158&driver_number=11`
- *Nota:* A disponibilidade de rádios diminuiu a partir de 2026 devido a restrições de fornecimento de feed da FOM.

#### `/v1/weather`
Condições meteorológicas aferidas ao redor do autódromo (atualizado a cada minuto).
- **Atributos principais:** `date`, `session_key`, `meeting_key`, `air_temperature` (°C), `track_temperature` (°C), `humidity` (%), `pressure` (mbar), `rainfall` (`0` ou `1`), `wind_speed` (m/s), `wind_direction` (graus: 0 a 360°).
- **Exemplo:** `https://api.openf1.org/v1/weather?meeting_key=latest`

---

## 5. Exemplos de Código

### 5.1. cURL
```bash
# Obter as 5 melhores voltas de uma sessão
curl -s "https://api.openf1.org/v1/laps?session_key=9161&lap_duration>0" | jq 'sort_by(.lap_duration) | .[0:5]'
```

### 5.2. Python com Pandas
```python
import pandas as pd
import requests

# 1. Buscar a última sessão realizada
sessions_url = "https://api.openf1.org/v1/sessions?session_key=latest"
session = requests.get(sessions_url).json()[0]
session_key = session["session_key"]
print(f"Sessão: {session['session_name']} - {session['location']} ({session_key})")

# 2. Carregar dados de telemetria de um piloto específico
car_url = f"https://api.openf1.org/v1/car_data?session_key={session_key}&driver_number=1&speed>=250"
car_data = requests.get(car_url).json()

# 3. Converter diretamente para DataFrame
df_telemetry = pd.DataFrame(car_data)
print(df_telemetry[["date", "speed", "rpm", "n_gear", "throttle", "drs"]].head())
```

---

## 6. Sumário Rápido de Endpoints

| Endpoint | Descrição | Frequência / Gatilho |
| :--- | :--- | :--- |
| [`/v1/meetings`](#41-calendário-e-sessões) | Finais de semana de GP e testes coletivos | Estático por GP |
| [`/v1/sessions`](#41-calendário-e-sessões) | Sessões individuais (TL, Quali, Sprint, Corrida) | Estático por Sessão |
| [`/v1/drivers`](#42-pilotos-e-campeonatos) | Pilotos, números, fotos e equipes | Por sessão |
| [`/v1/championship_drivers`](#42-pilotos-e-campeonatos) | Pontos e posições de pilotos no campeonato | Por corrida |
| [`/v1/championship_teams`](#42-pilotos-e-campeonatos) | Pontos e posições de construtores | Por corrida |
| [`/v1/starting_grid`](#43-classificação-grid-e-voltas) | Grid oficial de largada da corrida | Pré-corrida |
| [`/v1/session_result`](#43-classificação-grid-e-voltas) | Classificação final, tempos e status (DNF/DSQ) | Pós-sessão |
| [`/v1/laps`](#43-classificação-grid-e-voltas) | Cronometragem volta a volta, setores e speed trap | Por volta |
| [`/v1/stints`](#44-estratégia-de-pneus-e-boxes) | Conjuntos de pneus utilizados e durabilidade | Por troca de pneu |
| [`/v1/pit`](#44-estratégia-de-pneus-e-boxes) | Duração de pit stop e passagem pelo pit lane | Por parada |
| [`/v1/position`](#45-dinâmica-de-corrida-em-tempo-real) | Posição relativa em pista ao longo do tempo | Dinâmico |
| [`/v1/intervals`](#45-dinâmica-de-corrida-em-tempo-real) | Diferença de tempo para o líder e para o carro à frente | A cada ~4 segundos |
| [`/v1/overtakes`](#45-dinâmica-de-corrida-em-tempo-real) | Manobras de ultrapassagem confirmadas | Por ocorrência |
| [`/v1/car_data`](#46-telemetria-e-rastreamento-cartesiano-37-hz) | Telemetria (velocidade, RPM, acelerador, freio, DRS, marcha) | Alta freq (~3.7 Hz) |
| [`/v1/location`](#46-telemetria-e-rastreamento-cartesiano-37-hz) | Coordenadas cartesianas espaciais (x, y, z) | Alta freq (~3.7 Hz) |
| [`/v1/race_control`](#47-direção-de-prova-rádio-e-clima) | Incidentes, bandeiras e mensagens da direção de prova | Por evento |
| [`/v1/team_radio`](#47-direção-de-prova-rádio-e-clima) | Áudios de comunicação das equipes com pilotos | Por transmissão |
| [`/v1/weather`](#47-direção-de-prova-rádio-e-clima) | Temperatura da pista/ar, vento, chuva e pressão | A cada 1 minuto |

