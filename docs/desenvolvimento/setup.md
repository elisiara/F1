# Guia de Setup e Desenvolvimento

Instruções para configurar o ambiente de desenvolvimento local do projeto a partir de um clone limpo.

---

## 📋 Pré-requisitos

- **Python**: Versão `>= 3.12`
- **Poetry**: Versão `>= 2.0`
- **Git**

> [!WARNING]
> **Proibição Estrita do `pip`**:  
> Conforme estipulado no guia de engenharia (`SKILL.md`), **nunca utilize `pip install`**. Todas as dependências e ferramentas devem ser gerenciadas e executadas através do Poetry.

---

## 🛠️ Passo a Passo de Instalação

### 1. Clonar o Repositório e Navegar para a Pasta
```bash
git clone <url-do-repositorio>
cd F1
```

### 2. Verificar Versão do Poetry
```bash
poetry --version
```

### 3. Instalar Dependências do Projeto
```bash
# Instala o pacote raiz e os grupos de desenvolvimento e documentação
poetry install
```

### 4. Validar o Ambiente Virtual Criado
```bash
poetry env info
poetry run python --version
```

---

## ⚙️ Variáveis de Ambiente Opcionais

Copie o arquivo `.env.example` para `.env` se desejar customizar os parâmetros operacionais:

```bash
cp .env.example .env
```

Parâmetros disponíveis:
- `OPENF1_BASE_URL`: URL da API (padrão: `https://api.openf1.org/v1`)
- `REQUEST_TIMEOUT_SECONDS`: Timeout de requisição (padrão: `15`)
- `MAX_RETRIES`: Tentativas automáticas com backoff (padrão: `3`)
- `LOG_LEVEL`: Nível de log (`INFO`, `DEBUG`, `WARNING`, `ERROR`)
- `DATA_DIR`: Pasta raiz de dados (padrão: `data`)

