# Padrões de Qualidade, Linting e Testes

Este projeto adota critérios estritos de qualidade de software para garantir confiabilidade, legibilidade e cobertura de testes.

---

## 🔍 Linting e Formatação com Ruff

O **Ruff** é a ferramenta centralizada para análise estática e formatação de código.

### Comandos de Verificação:

```bash
# 1. Executar análise estática (linter)
poetry run ruff check .

# 2. Corrigir automaticamente violações seguras do linter
poetry run ruff check . --fix

# 3. Organizar os imports alfabeticamente (isort)
poetry run ruff check . --select I --fix

# 4. Formatar o código-fonte
poetry run ruff format .

# 5. Checagem estrita de formatação (modo CI)
poetry run ruff format --check .
```

---

## 🧪 Testes Automatizados com Pytest

O **Pytest** integrado ao **pytest-cov** monitora a execução de testes e a cobertura global de código.

### Regra de Cobertura Mínima:
- O projeto exige cobertura **mínima global de 50%** das linhas de `src/f1`.
- Caso a cobertura caia abaixo deste limiar, o comando `poetry run pytest` falhará com erro.

### Comandos de Testes:

```bash
# 1. Executar toda a suíte de testes com validação automática de cobertura
poetry run pytest

# 2. Executar testes exibindo linhas não cobertas
poetry run pytest -v --cov-report=term-missing

# 3. Executar arquivo de teste específico
poetry run pytest tests/unit/test_transformations.py
```

---

## 📚 Validação da Documentação com MkDocs

Toda alteração de código ou documentação deve ser validada no modo estrito:

```bash
# Servidor local com recarregamento dinâmico
poetry run mkdocs serve

# Compilação estrita (qualquer link quebrado causa falha)
poetry run mkdocs build --strict
```

