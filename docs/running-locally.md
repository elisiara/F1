```markdown
# Running locally

## Requisitos

- Python 3.12
- Poetry

## Instalação

1. Copie o arquivo de exemplo de variáveis de ambiente:

```bash
cp .env.example .env
```

2. Instale dependências:

```bash
poetry install --with dev
```

3. Rodar a dashboard (Streamlit):

```bash
poetry run streamlit run src/f1/dashboard.py
```

4. Rodar testes unitários:

```bash
poetry run pytest tests/unit/
```
```
