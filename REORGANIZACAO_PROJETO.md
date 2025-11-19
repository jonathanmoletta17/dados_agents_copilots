# Estrutura de Organização do Projeto GLPI

## Análise da Situação Atual

O projeto atual está desorganizado com três projetos distintos misturados:

### 1. Projeto GLPI API Atlas (Mapeamento da API)
- **Documentação**: `.trae/documents/`, `docs/`, `openapi/`
- **SDK Python**: `sdk/python/glpi_client/`
- **Coleções**: `collections/` (Postman/Insomnia)
- **Exemplos**: `examples/`

### 2. Projeto Análise de Dados (CSVs e Limpeza)
- **Dados brutos**: `scripts/dados/tickets_completos/todos_tickets_atual.csv`
- **Dados limpos**: Vários arquivos XLSX/CSV gerados
- **Scripts de limpeza**: Múltiplos arquivos `limpar_tickets_*.py`
- **Relatórios**: `scripts/dados/metricas_csv/`

### 3. Projeto Integração/Banco de Dados
- **Banco SQLite**: `scripts/db/glpi.sqlite`
- **Scripts ETL**: `scripts/python/db/`
- **Scripts de extração**: Vários arquivos de coleta

## Proposta de Reorganização

```
bd_cau/
├── 01-glpi-api-atlas/          # Projeto de Mapeamento da API GLPI
│   ├── docs/                   # Documentação OpenAPI e markdown
│   ├── sdk/                    # Client SDK Python
│   ├── examples/               # Exemplos de uso da API
│   ├── collections/            # Postman/Insomnia collections
│   └── tests/                  # Testes do SDK
│
├── 02-analise-dados-glpi/      # Projeto de Análise de Dados
│   ├── data/                   # Dados brutos e processados
│   │   ├── raw/               # CSVs originais
│   │   ├── processed/         # CSVs/XLSX limpos
│   │   └── reports/           # Relatórios gerados
│   ├── scripts/               # Scripts de limpeza e análise
│   └── notebooks/             # Análises Jupyter (se necessário)
│
├── 03-integracao-glpi/         # Projeto de Integração/Banco
│   ├── database/              # SQLite e schemas
│   ├── etl/                   # Scripts de ETL
│   └── sync/                  # Scripts de sincronização
│
└── shared/                    # Utilitários compartilhados
    └── utils/                  # Funções comuns
```

## Arquivos a Manter/Apagar

### Manter:
- Documentação oficial do projeto API Atlas
- SDK Python funcional
- Dados originais e scripts de limpeza final
- Banco SQLite e scripts ETL funcionais

### Apagar:
- Arquivos de backup desnecessários (*_anterior.csv)
- Scripts duplicados de limpeza (manter apenas o final)
- Arquivos temporários de processamento
- Várias versões do mesmo relatório

## Próximos Passos
1. Criar estrutura de diretórios
2. Mover arquivos para pastas apropriadas
3. Apagar arquivos desnecessários
4. Atualizar referências nos scripts
5. Testar funcionalidade