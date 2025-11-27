# Automação de Categorização de Tickets GLPI com IA Local

Este projeto implementa um serviço automatizado para analisar tickets abertos no GLPI e sugerir/atualizar a categoria correta utilizando Inteligência Artificial (LLM Local).

## 🚀 Onde está rodando?

O serviço está rodando em um container Docker na sua máquina local:
- **Endereço Local:** `http://localhost:8000`
- **Endereço na Rede:** `http://10.72.16.3:8000` (Use este IP para configurar Webhooks no GLPI)
- **Container Name:** `glpi-service`
- **Modelo de IA:** `llama3` (rodando via Ollama na porta 11434 do host)

---

## 🛠️ Como Testar e Usar

Existem duas formas de funcionamento simultâneas:

### 1. Automático (Recomendado para Produção)
Se você tiver permissão de administrador no GLPI, configure o plugin **Webhooks**:
- **URL:** `http://10.72.16.3:8000/api/v1/webhook/ticket`
- **Eventos:** `Ticket` -> `Add` (Adicionar)
- **Ação:** O GLPI enviará o ticket instantaneamente para o serviço assim que for criado.

### 2. Polling (Modo de Varredura - Já Ativo!)
Mesmo sem configurar o Webhook, o sistema possui um robô (`AIWorker`) que roda a cada **60 segundos**.
- **Como testar:**
    1. Abra um ticket no GLPI.
    2. Deixe a categoria como "Não atribuído" (ou escolha uma errada para testar correção).
    3. Aguarde até 1 minuto.
    4. Atualize a página do ticket. A categoria terá sido preenchida.

---

## 🏗️ Arquitetura do Projeto

```mermaid
graph TD
    GLPI[Servidor GLPI Produção] -- Webhook (Instantâneo) --> API[FastAPI Service (Docker)]
    API -- Varredura (60s) --> GLPI
    API -- Consulta --> Ollama[Ollama Local (Llama3)]
    Ollama -- Sugestão --> API
    API -- Atualiza Categoria --> GLPI
```

### Componentes Chave:
1.  **`src/api/routes/webhook.py`**: Recebe notificações do GLPI e enfileira processamento em background.
2.  **`src/workers/ai_worker.py`**: Robô que busca tickets sem categoria ativamente (garante que nada seja perdido).
3.  **`src/services/ai_service.py`**: Núcleo lógico. Busca mapa de categorias do GLPI, consulta a IA e aplica regras de negócio.
4.  **`src/ai_client/client.py`**: Cliente otimizado para comunicar com Ollama.

---

## 🔧 Comandos Úteis

### Verificar Logs (Monitoramento)
Para ver o que o robô está fazendo em tempo real:
```bash
docker logs -f glpi-service
```
*Procure por linhas com "🤖 AI Worker"*

### Reiniciar Serviço
Se precisar reiniciar:
```bash
docker-compose restart glpi-service
```

### Parar Serviço
```bash
docker-compose down
```

---

## 📋 Requisitos e Instalação

### Pré-requisitos
1.  **Docker & Docker Compose** instalados.
2.  **Ollama** instalado e rodando na porta 11434.
3.  Modelo `llama3` baixado (`ollama pull llama3`).

### Instalação
O ambiente já está configurado via `docker-compose.yml`.
Para recriar do zero:
```bash
docker-compose up -d --build
```

### Configuração (.env)
O arquivo `.env` na raiz controla tudo:
```env
# Credenciais GLPI
GLPI_DTIC_URL=http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php
GLPI_DTIC_APP_TOKEN=...
GLPI_DTIC_USER_TOKEN=...

# Configuração IA
AI_SERVICE_URL=http://host.docker.internal:11434/api/generate
AI_MODEL_NAME=llama3:latest
```

---

## ⚠️ Solução de Problemas Comuns

**1. A IA não atualizou o ticket**
- Verifique se o ticket já tinha uma categoria (o robô ignora tickets já categorizados, a menos que a regra de correção seja ativada).
- Verifique os logs: `docker logs glpi-service`.
- Confirme se o Ollama está rodando: `curl http://localhost:11434`.

**2. Erro de Banco de Dados nos Logs**
- Você pode ver erros como `FATAL: password authentication failed for user "glpi_user"`.
- **Ignore.** Isso se refere ao módulo de estatísticas (Sync Worker) que tenta conectar num banco local Postgres. **A funcionalidade de IA é independente e não é afetada por isso.**

**3. Timeout**
- O processamento da IA pode levar alguns segundos. O worker tem timeout configurado para não travar a fila.
