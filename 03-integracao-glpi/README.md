# Integração GLPI

Projeto de integração com banco de dados SQLite e sincronização.

## Estrutura
- `database/` - Banco SQLite e schemas
- `etl/` - Scripts de ETL
- `sync/` - Scripts de sincronização

## Uso
```bash
# Executar ETL
python etl/extrair_todos_tickets.py

# Banco de dados: database/glpi.sqlite
```
