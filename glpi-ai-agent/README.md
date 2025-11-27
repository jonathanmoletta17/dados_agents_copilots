# GLPI AI Agent

Este projeto é um agente autônomo que integra o GLPI com modelos de IA locais (via Ollama) para automatizar a categorização de chamados.

## Funcionalidades

- **Webhook API**: Recebe notificações de novos chamados do GLPI.
- **Integração com Ollama**: Analisa o título e descrição do chamado usando LLMs locais (ex: Llama3).
- **Categorização Automática**: Sugere e atualiza a categoria do chamado no GLPI se a confiança for alta.
- **Suporte Multi-Contexto**: Configurável para diferentes ambientes GLPI (ex: DTIC, SIS).

## Estrutura do Projeto

- `src/main.py`: Ponto de entrada da aplicação FastAPI.
- `src/api/webhook.py`: Endpoint do webhook que recebe eventos do GLPI.
- `src/services/ai_service.py`: Lógica principal de orquestração (Busca chamado -> Analisa com IA -> Atualiza GLPI).
- `src/clients/`: Clientes para GLPI e Ollama.
- `src/config/`: Configurações centralizadas via variáveis de ambiente.

## Pré-requisitos

- Docker e Docker Compose
- Servidor Ollama rodando (localmente ou em rede acessível) com o modelo desejado (ex: `llama3`).

## Configuração

1. Copie o arquivo de exemplo de ambiente:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas credenciais do GLPI e configurações do Ollama.

## Como Rodar

### Via Docker Compose

```bash
docker-compose up -d --build
```

O serviço estará rodando na porta `8000`.

### Desenvolvimento Local

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Configuração no GLPI

Configure o plugin de Webhook do GLPI para enviar eventos de "Ticket" (Adicionar) para:
`http://<IP-DO-SERVIDOR>:8001/api/v1/webhook/ticket`

## Cache de Categorias

O agente implementa cache em memória para categorias do GLPI, reduzindo chamadas redundantes à API.

- **TTL padrão:** 5 minutos (300 segundos)
- **Configurável via:** `CATEGORY_CACHE_TTL_SECONDS` no `.env`
- **Comportamento:**
  - Primeira requisição: busca categorias do GLPI e popula cache
  - Requisições subsequentes: usa cache (resposta instantânea)
  - Após TTL: refresh automático na próxima requisição

**Exemplo de configuração:**
```bash
# Cache de 10 minutos
CATEGORY_CACHE_TTL_SECONDS=600
```

**Logs do cache:**
- `🔄 Category cache updated from GLPI` - Cache foi atualizado
- `📦 Using cached categories` - Usando cache (modo debug)

## Prompt Otimizado

O prompt enviado à IA foi otimizado seguindo boas práticas de classificação com LLMs:

- **Instruções explícitas** para escolher exatamente uma categoria da lista
- **Regras estritas** para prevenir invenção de categorias novas
- **Formato de saída simples** (apenas o nome da categoria, sem explicações)
- **Temperatura baixa (0.2)** para respostas determinísticas
- **Validação case-insensitive** para correspondência flexível

Isso garante:
- ✅ Classificação mais consistente
- ✅ Menos rejeições por categorias inexistentes
- ✅ Melhor aderência às categorias reais do GLPI

## Logs

Os logs da aplicação são exibidos no stdout e podem ser visualizados via Docker logs:
```bash
docker-compose logs -f
```
