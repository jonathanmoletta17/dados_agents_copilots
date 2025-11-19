# GLPI API Atlas

Mapeamento completo da API REST do GLPI com documentação OpenAPI, SDK Python e exemplos.

## Estrutura
- `docs/` - Documentação OpenAPI e markdown
- `sdk/` - Client SDK Python
- `examples/` - Exemplos de uso
- `collections/` - Coleções Postman/Insomnia

## Uso Rápido
```python
from glpi_client import GLPIClient

client = GLPIClient(url="https://glpi.example.com", app_token="seu_token")
client.init_session(user_token="seu_user_token")

tickets = client.tickets.list()
```
