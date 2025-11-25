# Agente Copilot Studio para Análise de Tickets/Usuários (GLPI)

## Objetivo
- Carregar JSON(s) de tickets e usuários via API no início da conversa.
- Persistir dados em variáveis acessíveis durante toda a sessão.
- Permitir análises exploratórias, métricas e buscas específicas com respeito a limites oficiais e boas práticas.

## 1) Persistência de variáveis (Copilot Studio)
- Tipos/escopos principais:
  - Variáveis de conversa: válidas durante a sessão atual.
  - Variáveis de usuário: associadas ao usuário (dependem do canal/identidade) e podem persistir entre sessões.
  - Variáveis de bot (globais): disponíveis em qualquer tópico do bot.
  - Variáveis de tópico: escopo local ao tópico em execução.
- Inicialização automática:
  - Use o tópico de sistema “Conversation start”/“Greeting” para inicializar variáveis e contexto no início do chat.
- Armazenamento de JSON/objetos:
  - Suportado via ações/plug-ins e Power Fx, usando tipos Objeto/Registro e Lista/Tabela para manipular campos e coleções.

## 2) Carregamento de dados no início da conversa
- Padrão recomendado:
  - No tópico “Conversation start”, adicionar um nó “Call an action”.
  - A ação chama um fluxo Power Automate (HTTP/Conector) que busca `tickets` e `usuarios` em sua API.
  - O fluxo retorna saídas tipadas (JSON) ao bot; no tópico, mapear para variáveis de conversa.
- Mapeamento sugerido de variáveis:
  - `ticketsResumo` (objeto com contagens por status, prioridade, categorias).
  - `ticketsAbertos` (lista enxuta com campos-chave; carregar sob demanda se grande).
  - `ticketsFechados` (sob demanda por período/categoria).
  - `usuariosResumo` (perfil agregado, totais por equipe/setor).
  - `usuariosDetalhes` (sob demanda por usuário específico).
- Contrato de saída (exemplo conceitual):
```json
{
  "ticketsResumo": {
    "total": 842,
    "abertos": 132,
    "fechados": 710,
    "porPrioridade": { "Alta": 27, "Média": 69, "Baixa": 36 }
  },
  "usuariosResumo": {
    "total": 214,
    "equipes": [ { "nome": "Suporte", "membros": 38 }, { "nome": "Infra", "membros": 21 } ]
  }
}
```
- Passos práticos no canvas:
  - “Call an action” → fluxo “BootstrapGLPI”.
  - “Set variable” para salvar cada saída em variáveis de conversa.
  - Condições para tratar falhas e continuar com modo degradado.

## 3) Capacidades e limites (tamanho e contexto)
- Variáveis de conversa: sem número rígido público; na prática, respeite limites do canal e do modelo.
- Dataverse (persistência longa):
  - “Single line of text”: até 4.000 caracteres.
  - “Multiple lines of text”: até 1.048.576 caracteres.
- Canais (ex.: Microsoft Teams):
  - Mensagens de bot típicas ~28 KB por atividade (texto + payloads), planeje dividir/sumarizar.
- Modelos Azure OpenAI (GPT‑4o/4‑Turbo):
  - Janela de contexto grande (tipicamente 128k tokens). Todo o prompt (instruções + variáveis + histórico + RAG) deve caber.
- Recomendações:
  - Evite blobs grandes em variáveis; use RAG (trechos relevantes) e carregamento sob demanda.
  - Planeje orçamento de tokens (reserve ~20–30% para a resposta).

## 4) Orquestração de múltiplas variáveis (tickets/usuários)
- Padrão de mapeamento:
  - Visões agregadas: `ticketsResumo`, `usuariosResumo`.
  - Detalhes sob demanda: `ticketsDetalhes`, `usuariosDetalhes`.
- Seleção por intenção:
  - Métricas globais → use `ticketsResumo`/`usuariosResumo`.
  - Ticket específico → consulte/filtre em `ticketsDetalhes` por `id`/`status`/`categoria`.
  - Usuário específico → use `usuariosDetalhes` por `id`/`nome`.
- Estratégias:
  - Fragmentar por status/período (`ticketsAbertos`, `ticketsUltimos30Dias`).
  - Pré-agregar contagens e médias para respostas rápidas.
  - Paginação e janelas de tempo para históricos extensos.

## 5) Integração com ferramentas/“interpretador de código”
- Dentro do Copilot Studio:
  - Use Ações (Plugins/OpenAPI ou Power Automate) para delegar análises pesadas a um backend.
  - Passe variáveis JSON (`tickets`/`usuarios`) como entradas tipadas.
- Backend analítico (Azure OpenAI):
  - Assistants API com `code_interpreter` para executar Python com cálculos e gráficos.
  - Responses API com “function calling” para contratos JSON e execução determinística.
- Fluxo recomendado:
  - Copilot → Ação `analisaTickets` (POST com `tickets`, `usuario`, `escopo`).
  - Backend → análise (agrupamentos, SLAs, rankings) → devolve JSON de `metricas` e `insights`.
  - Copilot → resposta natural + opcional Adaptive Card com KPIs.

## 6) Exemplos e casos validados (oficial + comunidade)
- Variáveis (Copilot Studio/PVA): uso de objeto/JSON e mapeamento de saídas de ações.
- Tópico “Conversation start”: inicialização de contexto e carga de dados.
- Particionamento de variáveis: separar resumo vs detalhes e carregar sob demanda.
- Fluxos Power Automate: `HTTP`/Conector, `Parse JSON`, `Return value(s) to Copilot)` com saídas tipadas.

## 7) Guia de implementação (passo a passo)
1. Definir variáveis
   - Criar variáveis de conversa: `ticketsResumo`, `usuariosResumo`, `ticketsDetalhes`, `usuariosDetalhes`.
2. Fluxo de início (Conversation start)
   - Adicionar “Call an action” → fluxo `BootstrapGLPI`.
   - No fluxo: chamar API GLPI (tickets/usuários), `Parse JSON`, compor objetos enxutos.
   - Retornar saídas tipadas (ex.: `ticketsResumo`, `usuariosResumo`).
   - Mapear saídas para variáveis de conversa com “Set variable”.
3. Responder perguntas analíticas
   - Para métricas globais: usar `ticketsResumo`/`usuariosResumo` diretamente.
   - Para buscas específicas: chamar ação sob demanda (`BuscarTicketsPorPeriodo`, `BuscarUsuarioPorNome`) e preencher `ticketsDetalhes`/`usuariosDetalhes`.
4. Análises pesadas
   - Ação `analisaTickets` chama backend (Azure Functions) que usa Assistants `code_interpreter`.
   - Entradas: JSON `tickets`, `usuario`, filtros (período, status).
   - Saídas: `metricas` (contagens, tempos médios, rankings) e `insights`.

## Apêndice A: Esquema OpenAPI (ação analítica)
```json
{
  "openapi": "3.0.1",
  "info": { "title": "Serviço de Análise de Tickets", "version": "1.0.0" },
  "paths": {
    "/analisar-tickets": {
      "post": {
        "summary": "Analisa tickets e gera insights",
        "operationId": "analisaTickets",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "tickets": { "type": "array", "items": { "$ref": "#/components/schemas/Ticket" } },
                  "usuario": { "$ref": "#/components/schemas/Usuario" },
                  "filtros": { "type": "object" }
                },
                "required": ["tickets"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Resultado da análise",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "resumo": { "type": "string" },
                    "metricas": { "type": "object" },
                    "insights": { "type": "array", "items": { "type": "string" } }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Ticket": {
        "type": "object",
        "properties": {
          "id": { "type": "integer", "nullable": true },
          "titulo": { "type": "string" },
          "solicitante": { "type": "string" },
          "data": { "type": "string" },
          "prioridade": { "type": "string", "nullable": true },
          "status": { "type": "string", "nullable": true },
          "categoria": { "type": "string", "nullable": true }
        },
        "required": ["titulo", "solicitante", "data"]
      },
      "Usuario": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "nome": { "type": "string" },
          "perfil": { "type": "string" }
        },
        "required": ["id", "nome"]
      }
    }
  }
}
```

## Apêndice B: Fluxo Power Automate (bootstrap)
- Trigger: “When a flow is called from Copilot”.
- HTTP (GET/POST) → API GLPI (tickets/usuários).
- Parse JSON → schemas tipados.
- Compose → reduzir estrutura aos campos necessários.
- Return value(s) to Copilot → `ticketsResumo`, `usuariosResumo`.

## Apêndice C: Limites e governança
- Dataverse: 4.000 vs 1.048.576 caracteres para colunas de texto.
- Teams: planejar mensagens < ~28 KB por atividade.
- Azure OpenAI: janela de contexto grande; sempre reduzir e priorizar dados relevantes.
- Segurança: tokens/segredos apenas em conectores/flows; nunca em variáveis do bot.

