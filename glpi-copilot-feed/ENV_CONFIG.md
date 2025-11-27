# Configuração do .env para glpi-copilot-feed

## ⚠️ IMPORTANTE: Credenciais do Banco

Este projeto precisa se conectar ao PostgreSQL que roda no Docker. As credenciais devem corresponder às configuradas no `glpi-data-service/.env`.

### Opção 1: Usar as mesmas credenciais do glpi-data-service

Se você já tem o `glpi-data-service` rodando, copie as credenciais de lá:

```bash
# Credenciais do Banco de Dados (PostgreSQL)
PGHOST=localhost
PGPORT=5432
PGDATABASE=glpi_data
PGUSER=glpi_user
PGPASSWORD=<COPIE_DA glpi-data-service/.env>
```

### Opção 2: Credenciais padrão

Se você não alterou o `.env` do `glpi-data-service`, use:

```bash
PGUSER=glpi_user
PGPASSWORD=glpi_secure_password_2024
```

### Configuração da API GLPI

Copie também as credenciais da API GLPI DTIC do `glpi-data-service/.env`:

```bash
GLPI_DTIC_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_DTIC_APP_TOKEN=<COPIE_DO_glpi-data-service/.env>
GLPI_DTIC_USER_TOKEN=<COPIE_DO_glpi-data-service/.env>
```

## Testando a Conexão

Antes de rodar o job completo, teste a conexão:

```bash
python test_connection.py
```

Se der erro "connection refused" ou "authentication failed":
1. Verifique se o Docker está rodando: `docker ps | findstr glpi-postgres`
2. Verifique se as credenciais no `.env` correspondem às do `glpi-data-service`
3. Se necessário, copie o `.env` do `glpi-data-service` como base
