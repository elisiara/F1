# Engenharia de Dados com Fórmula 1 (OpenF1 Pipeline)

Bem-vindo à documentação oficial do projeto de **Engenharia de Dados da Fórmula 1**, desenvolvido com foco em arquitetura modular, tipagem estática, resiliência de rede e conformidade com as melhores práticas de engenharia de software e dados.

---

## 🏎️ Visão Geral

O projeto implementa uma solução completa de ingestão, validação contratual, transformações puras e persistência analítica colunar em **Parquet**, consumindo a **OpenF1 REST API (v1)** — uma plataforma aberta com telemetria em alta frequência (~3.7 Hz), cronometragem e dinâmica de pista da F1.

```mermaid
flowchart LR
    A["OpenF1 REST API"] -->|HTTP GET com Retry| B["Conector Resiliente"]
    B -->|Validação de Domínio| C["Modelos Dataclass"]
    C -->|Transformações Puras| D["Métricas e Limpeza"]
    D -->|Carga Idempotente| E["Parquet Particionado"]
```

---

## 🎯 Objetivos Centrais

1. **Arquitetura `src/` Layout**: Separação estrita entre conector de I/O, modelos de domínio, transformações analíticas e serviços de negócio.
2. **Padrão E-V-T-L**: Extração com retries e timeouts ➔ Validação de contratos de dados ➔ Transformações determinísticas sem efeitos colaterais ➔ Carga particionada.
3. **Persistência Analítica Idempotente**: Armazenamento colunar em formato Parquet particionado por ano, sessão e piloto.
4. **Qualidade Contínua**: 100% de conformidade com o linter **Ruff**, suíte de testes com **Pytest** e cobertura mínima de 50% obrigatória.

---

## 🧭 Estrutura da Documentação

- [**Arquitetura - Visão Geral**](arquitetura/visao_geral.md): Princípios de design, fluxo de dados e separação em camadas.
- [**Padrões de Dados**](arquitetura/padroes_dados.md): Modelagem dimensional, partições e contratos.
- [**Conectores**](conectores/openf1.md): Especificação do cliente HTTP resiliente para a OpenF1 API.
- [**Pipelines**](pipelines/telemetria.md): Guia operacional para execução do pipeline analítico.
- [**Guia de Setup**](desenvolvimento/setup.md): Instruções passo a passo para instalação com Poetry.
- [**Qualidade e Testes**](desenvolvimento/qualidade.md): Comandos para execução de testes, validação de cobertura e linter.

