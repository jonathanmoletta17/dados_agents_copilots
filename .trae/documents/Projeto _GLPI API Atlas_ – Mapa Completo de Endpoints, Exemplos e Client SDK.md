## Objetivos
- Catalogar e padronizar TODA a API REST do GLPI (core + relacionamentos), com exemplos práticos, schemas, testes e um client SDK.
- Oferecer um repositório de referência duradouro para desenvolvimento, automação e integrações.
- Disponibilizar endpoints de conveniência (gateway) que agregam dados e mantêm um shape consistente para consumo por agentes.

## Escopo
- Autenticação: `initSession`, `killSession`, headers (`Session-Token`, `App-Token`).
- Core ITIL: `Ticket`, `ITILCategory`, `Entity`, `User`, `Group`, `Ticket_User`, `Group_Ticket`, `Followups` (diários), `Task` (Tarefa), `SLA/OLA`, `Problem`, `Change`.
- Inventário: `Computer`, `NetworkEquipment`, `Printer`, `Peripheral`, `Phone`, `Software`, `Location`, `Supplier`, `Contract`.
- Conhecimento: `KnowbaseItem` (base de conhecimento), `Document`.
- Busca e utilitários: `search`, listagens com `range`, `criteria`, `expand_dropdowns`, `get_hateoas`.
- Ações: `addItem`, `updateItem`, `deleteItem`, `massiveAction` (quando aplicável).

## Entregáveis
1. **Catálogo de Endpoints (OpenAPI + Markdown)**
   - Especificação OpenAPI 3 cobrindo recursos, parâmetros, schemas e respostas comuns.
   - Páginas por recurso com: rotas, query params, exemplos de request/response, erros típicos e boas práticas.
   - Postman/Insomnia collection gerados a partir do OpenAPI.
2. **Client SDK**
   - Biblioteca cliente (Python inicialmente) com wrappers: `list`, `get`, `search`, `create`, `update`, `delete` e utilitários (`range`, `criteria`, paginação, retries).
   - Tipagem leve (pydantic opcional) para validação de payloads.
3. **Gateway de Conveniência (Opcional)**
   - Pequeno serviço web com endpoints agregados (ex.: `/glpi/tickets` com join de nomes, filtros e paginação), retornando JSON padronizado.
4. **Exemplos Práticos**
   - Scripts por recurso: listar, buscar com critérios, criar/atualizar, vincular usuários/grupos, anexar documentos, registrar followup.
   - Receitas ITIL: abrir ticket, atribuir técnico/grupo, mudar status, adicionar solução, fechar, medir SLA.
5. **Testes e Validação**
   - Testes automatizados com fixtures e validação de contratos (respostas vs schemas).
   - Suíte de smoke/integrados com `Session-Token` real (variáveis de ambiente).
6. **Boas Práticas e Segurança**
   - Gestão de tokens por ambiente, rate limiting, tratamento de erros, retries exponenciais.
   - Sanitização de strings e logs sem segredos.

## Mapa de Recursos (núcleo)
- **Autenticação**
  - `GET /initSession` → obtém `session_token`.
  - `GET /killSession` → encerra sessão.
- **Tickets**
  - `GET /Ticket` (lista em blocos via `range`): filtros por `status`, `entities_id`, `itilcategories_id`, datas.
  - `GET /Ticket/{id}`: detalhes do ticket.
  - `POST /Ticket` / `PUT /Ticket/{id}` / `DELETE /Ticket/{id}`.
  - **Relacionamentos**:
    - `GET /Ticket_User` (type 1 requerente, 2 técnico) e `POST`/`DELETE` para vincular/desvincular.
    - `GET /Group_Ticket` (type 2 grupo técnico) e `POST`/`DELETE`.
  - **Diários/Followups**: `GET /ITILFollowup`, `POST` para registrar interação.
  - **Tarefas**: `GET /Task`, `POST`/`PUT` para planejar/registrar trabalho.
  - **Documentos**: `GET /Document`, anexar a um ticket.
- **Categorias/Entidades/Grupos/Usuários**
  - `GET /ITILCategory`, `GET /Entity`, `GET /Group`, `GET /User` (todos paginados por `range`).
  - CRUD conforme permissões.
- **Busca e Critérios**
  - `GET /search/{resource}` com `criteria[]`, `forcedisplay[]`, `range`, ordenação.
- **Inventário**
  - `GET /Computer`, `NetworkEquipment`, `Printer`, `Peripheral`, `Phone`, `Software`, `Location`, `Supplier`, `Contract`.
  - Ações de vinculação entre ativos e tickets.
- **ITIL Avançado**
  - `Problem`, `Change` e vínculos com `Ticket`.
- **Conhecimento**
  - `KnowbaseItem` para artigos e relação com tickets.

## Estrutura do Projeto
- `openapi/`: arquivo `glpi.yaml` com toda especificação.
- `docs/`: páginas por recurso com exemplos e receitas.
- `sdk/python/glpi_client/`: client com módulos por recurso.
- `examples/`: scripts por recurso e receitas ITIL.
- `gateway/`: serviço web opcional com endpoints agregados.
- `tests/`: unitários, contrato e integração.

## Padrões de Implementação
- **Paginação**: parâmetro `range` em blocos (ex.: `0-999`, `1000-1999`).
- **Desempenho**: `expand_dropdowns=false`, `get_hateoas=false` para respostas enxutas quando possível.
- **Campos Derivados**: nomes resolvidos via caches (`User`, `Group`, `Entity`, `ITILCategory`) e aplicados na camada gateway ou client.
- **Erros**: mapear códigos; respostas padronizadas `{status, code, message, request_id}`.
- **Segurança**: tokens somente em ambiente; sem persistência de segredos.

## Exemplos (por recurso)
- Tickets:
  - Listar últimos 6 meses: `GET /Ticket` com filtro por `date` (via client) e join de nomes.
  - Criar ticket mínimo: `POST /Ticket` com `name`, `content`, `itilcategories_id`, `entities_id`, `type`.
  - Atribuir técnico e grupo: `POST /Ticket_User` (type 2) e `POST /Group_Ticket` (type 2).
  - Fechar ticket: `PUT /Ticket/{id}` com `status=6` e `closedate`.
- Busca:
  - `GET /search/Ticket?criteria[0][field]=1&criteria[0][searchtype]=contains&criteria[0][value]=VPN` e `forcedisplay[]` para colunas extras.
- Inventário:
  - Vínculo de `Computer` ao ticket por campo de relacionamento.
- Documentos:
  - Upload e anexação a ticket por `Document` + link.

## Testes e Validação
- **Contrato**: validar respostas reais do GLPI contra schemas OpenAPI.
- **Funcionais**: receitas de ponta a ponta (abrir→atribuir→seguir→solucionar→fechar). 
- **Performance**: varredura paginada com caches locais; medição de tempo e volume.

## Roadmap de Implementação
1. Esqueleto do repositório e `glpi.yaml` (OpenAPI) mínimo com autenticação e `Ticket`.
2. Client Python (`list`, `get`, `search`, `create`, `update`, `delete`) com paginação `range`.
3. Catálogo de `User`, `Group`, `Entity`, `ITILCategory` e relacionamentos `Ticket_User`, `Group_Ticket`.
4. Exemplos práticos (scripts) e testes de contrato.
5. Expandir catálogo (Inventário, Problem, Change, Document, KnowbaseItem).
6. Gateway opcional com endpoints agregados (shape padronizado para agentes).
7. Hardening: segurança, logs, retries, documentação final.

## Requisitos
- Acesso ao GLPI com `App-Token` e `Session-Token`.
- Ambiente Python 3.10+; requests; (opcional) pydantic.
- Postman/Insomnia para gerar e manter coleções.

Posso iniciar criando o esqueleto com OpenAPI (autenticação + Ticket), client Python inicial e exemplos. Em seguida, expandimos recurso a recurso até cobrir todo o escopo descrito.