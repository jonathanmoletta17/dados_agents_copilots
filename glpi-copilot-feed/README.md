# GLPI Copilot Feed

Backend Python para exportação de dados do GLPI (DTIC) para CSVs consumíveis pelo Microsoft Copilot Studio.

## Arquitetura

```
PostgreSQL (glpi_data) → db_extract.py → export_csv.py → CSVs → OneDrive/SharePoint
```

## Arquivos Gerados

O sistema gera 3 arquivos CSV otimizados para análise:

1.  **`dtic_tickets_detalhe.csv`**:One linha por ticket, com todas as dimensões de negócio (sem texto livre sensível).
2.  **`dtic_metricas_mensais.csv`**: Métricas agregadas por mês (abertos, resolvidos, backlog).
3.  **`dtic_rankings.csv`**: Rankings de técnicos, entidades e categorias.

## Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar `.env`

Renomeie `.env.example` para `.env` e preencha as credenciais do PostgreSQL:

```env
PGHOST=localhost
PGPORT=5432
PGDATABASE=glpi_data
PGUSER=glpi_user
PGPASSWORD=sua_senha_aqui
ENABLE_SHAREPOINT_UPLOAD=false
```

### 3. Executar

```bash
python job_glpi_export.py
```

Os CSVs serão gerados na pasta `output/`.

## Modo de Publicação

**Opção B (Recomendado para Fase 1)**: OneDrive Sincronizado

*   Configure o OneDrive para sincronizar uma biblioteca do SharePoint.
*   Aponte a pasta `output/` para essa biblioteca sincronizada.
*   Ao rodar o job, os arquivos são automaticamente enviados para o SharePoint.

## Estrutura do Projeto

```
glpi-copilot-feed/
├── src/
│   ├── db_extract.py       # Conexão PostgreSQL e extração de dados
│   ├── export_csv.py       # Lógica de transformação e geração de CSVs
│   └── sharepoint_upload.py # (Opcional) Upload via Microsoft Graph API
├── job_glpi_export.py      # Script principal (orquestrador)
├── requirements.txt        # Dependências Python
├── .env.example            # Template de variáveis de ambiente
└── README.md               # Este arquivo
```

## Troubleshooting

### Erro: "Credenciais do banco não configuradas"
- Verifique se o arquivo `.env` existe na raiz do projeto.
- confirate que `PGUSER` e `PGPASSWORD` estão preenchidos.

### Erro: "connection refused"
- Verifique se o PostgreSQL está rodando (`docker ps`).
- Confirme a porta 5432 está mapeada corretamente.
