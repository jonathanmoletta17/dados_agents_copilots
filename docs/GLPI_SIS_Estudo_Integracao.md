# Estudo de Integração Formulários ↔ GLPI (SIS Manutenção e Conservação)

## Escopo e Garantias
- Modo somente leitura: sem alterar código em produção, sem criar/editar/excluir chamados reais, sem commits.
- Objetivo: consolidar conhecimento e plano de integração entre formulários do portal e criação de Tickets no GLPI SIS.
- Segredos não expostos: apenas nomes de variáveis de ambiente (`GLPI_SIS_URL`, `GLPI_SIS_APP_TOKEN`, `GLPI_SIS_USER_TOKEN`).

## Arquitetura Atual (Aplicação)
- Login: `external-projects/demandas-mobilidade-clone/lib/screens/login_screen.dart` chama `AppState.authenticate`.
- Estado/serviço:
  - `external-projects/demandas-mobilidade-clone/lib/state/app_state.dart` coordena autenticação mock e fila offline local.
  - `external-projects/demandas-mobilidade-clone/lib/services/glpi_api_service.dart` contém simulação e exemplos comentados de API real.
- Catálogo de serviços e navegação:
  - Catálogo: `external-projects/demandas-mobilidade-clone/lib/screens/service_catalog_screen.dart`.
  - Dados: `external-projects/demandas-mobilidade-clone/lib/data/service_data.dart`.
  - Rotas para formulários: `external-projects/demandas-mobilidade-clone/lib/widgets/service_card.dart`.
- Formulários:
  - Template-base: `external-projects/demandas-mobilidade-clone/lib/screens/form_template.dart`.
  - Campos reutilizáveis: `custom_text_field`, `custom_dropdown_field`, `anexar_arquivo_widget` em `external-projects/.../widgets/*`.
  - Telas específicas por categoria em `external-projects/.../screens/*_form_screen.dart`.
- Submissão atual: mock no frontend (apenas `SnackBar` e `print`). Integração real com GLPI não está ligada aos formulários.

## Inventário de Formulários e Campos
- Campos padrão (do `FormTemplate`):
  - "Este atendimento é para quem?" (select, obrigatório): valores "Para mim", "Para outra Pessoa".
  - "Qual o nome desta pessoa? (glpiselect)" (texto, obrigatório condicional).
  - "Localização" (select, obrigatório quando incluído).
  - "Telefone de Contato" (texto, obrigatório).
  - "Urgência" (select, opcional): "3 - Média (Padrão)", "1 - Baixa", "5 - Alta".
  - "Tipo" (select, obrigatório): opções por serviço.
  - "Assunto" (texto, obrigatório).
  - "Descrição" (texto multilinha, obrigatório).
  - "Anexar Arquivo" (arquivo, opcional; sem upload).
- Campos extras por serviço:
  - Vidraçaria: "Tipo de Atendimento" (Instalação/Medição/Remoção/Troca).
  - Projeto: "Divisão / Departamento".
- Variações:
  - Jardinagem/Limpeza/Copa: urgência desativada.
  - Elevadores: localização desativada.

## API GLPI – Autenticação e Ticket
- Autenticação suportada:
  - `GET /apirest.php/initSession` com `Authorization: user_token <token>` + `App-Token`: retorna `session_token`.
  - Alternativas (dependem de política local): `Authorization: Basic base64(login:password)` ou `POST` com JSON `{login,password}`.
- Criação de Ticket (`POST /apirest.php/Ticket`):
  - Cabeçalhos: `Session-Token`, `App-Token`, `Content-Type: application/json`.
  - `input` relevante:
    - `name` (string, obrigatório), `content` (string, obrigatório).
    - `type` (1=Incidente, 2=Requisição).
    - `urgency`, `impact`, `priority` (1..5/6).
    - `itilcategories_id` (ID), `entities_id` (ID), `requesttypes_id` (ID).
    - `_users_id_requester` (ID), `locations_id` (ID).
- Enums (GLPI):
  - `status`: 1=Novo, 2=Processando (Atribuído), 3=Planejado, 4=Em espera, 5=Resolvido, 6=Fechado, 10=Aprovação.
  - `type`: 1=Incidente, 2=Requisição.
  - `urgency/impact/priority`: 1=Muito Baixa … 5=Muito Alta (6=Maior aplicável em prioridade/urgência).
- Metadados:
  - Categorias: `GET /ITILCategory` (paginar com `Range`).
  - Localizações: `GET /Location`.
  - Tipos de solicitação: `GET /RequestType`.
  - Usuários: `GET /User`.

## Leituras Reais no GLPI SIS (Somente Leitura)
- Sessão via `user_token` criada e encerrada no final.
- Amostras obtidas:
  - ITILCategory (id→nome): 1 Ar Condicionado, 22 Elétrica, 17 Elevadores, 27 Troca, 26 Readequação, 6 Remanejo, 29 Suporte, 2/23 Conserto, 4/24 Instalação, 28 Descarte, 7 Outras atividades.
  - Location (id→nome): 8 Palácio Piratini, 19 Defesa Civil - Andrade Neves, 20 11º Andar, 22 15º Andar, 30 3º Andar, 1 Casa Civil 1005, 10 Casa Branca, 11 Casa Militar, 18 GVG - Edifício Guaiba - 11º Andar, 27 Limpeza, 31 Jardinagem.
  - RequestType: 1 Helpdesk, 7 Formulário (entre outros).
- Observações de Tickets reais (leitura): conteúdo `content` frequentemente inclui blocos "Dados Gerais"/"Detalhamento" e mostra categorias/localizações expandidas por nome.

## Mapeamento Campo ↔ GLPI (Regra)
- `Assunto` → `name` (string, obrigatório).
- `Descrição` + Telefone + Atendimento/Nome + Localização + Extras → `content` (string, obrigatório).
- `Tipo` (UI) → `itilcategories_id` (ID; resolver nome→ID por leitura/busca).
- `Localização` (UI) → `locations_id` (ID; resolver por leitura/busca).
- `Urgência` (UI) → `urgency` (numérico; ex.: “3 - Média (Padrão)” → 3).
- Atendimento/Nome → `_users_id_requester` (ID; “Para mim” = usuário da sessão; “Para outra Pessoa” buscar via `User`, senão registrar nome em `content`).
- `entities_id` derivado da sessão/usuário; `requesttypes_id` conforme política (Helpdesk=1 ou Formulário=7).
- `Anexo`: upload pós-criação (`Document_Item`), multipart.

## Dicionários nome→ID (Parciais e Estratégia de Expansão)
- Categorias principais já mapeadas (nome→ID):
  - Ar Condicionado → 1; Elétrica → 22; Elevadores → 17; Troca → 27; Readequação → 26; Remanejo → 6; Suporte → 29; Conserto → 2/23; Instalação → 4/24; Descarte → 28; Outras atividades → 7.
- Localizações principais já mapeadas (nome→ID):
  - Palácio Piratini → 8; Defesa Civil - Andrade Neves → 19; 11º Andar → 20; 15º Andar → 22; 3º Andar → 30; Casa Civil 1005 → 1; Casa Branca → 10; Casa Militar → 11; GVG - Ed. Guaiba - 11º Andar → 18; Limpeza → 27; Jardinagem → 31.
- RequestType (nome→ID): Helpdesk → 1; Formulário → 7.
- Expansão para subcategorias específicas (ex.: "Troca de Lâmpada", "Vidro Quebrado"):
  - Usar leitura adicional por busca textual (Search items) de `ITILCategory`/`Location` para resolver IDs das opções específicas dos formulários não presentes na lista plana.
  - Consolidar dicionários finais por formulário após coleta.

## Plano de Implementação por Categoria
- Etapas comuns (para todas):
  - Inventário de campos VIS e ajustes (extras, condicionais).
  - Resolver nome→ID de Categoria (Tipo) e Localização; fixar `requesttypes_id` (1 ou 7); mapear urgência para valor numérico.
  - Implementar mapeador no backend (builder de `input`).
  - Teste prático em homologação (criação real e validação de campos); upload de anexo onde aplicável.
- Ar-Condicionado:
  - Categoria geral 1; subcategorias (ex.: "Aparelho Não Liga", "Vazamento") por busca; localização por nome.
- Elétrica:
  - Categoria geral 22; subcategorias (ex.: "Troca de Lâmpada", "Curto Circuito"); localização por nome.
- Vidraçaria:
  - Subcategorias (ex.: "Vidro Quebrado", "Manutenção de Esquadria"); extra "Tipo de Atendimento" em `content` (ou modelar subcategoria, se existir); localização por nome.
- Elevadores:
  - Categoria 17; sem localização; detalhamentos por subcategorias, se aplicável.
- Jardinagem/Limpeza/Copa:
  - Urgência desativada; resolver subcategorias e localização por nome.
- Marcenaria/Mensageria/Pedreiro/Pintura/Projeto/Técnico de Redes/Carregadores:
  - Seguir padrão; tratar extras (Projeto: "Divisão/Departamento"; incluir em `content`/alinhar com entidade).

## Contrato do Backend
- `POST /api/tickets`
  - Entrada: payload dos formulários (campos VIS + categoria).
  - Processamento: resolver nome→ID, converter enums, montar `input`, autenticar e `POST /Ticket`, retornar `ticket_id`.
  - Pós-criação: endpoint para upload de documento.
- Serviços internos:
  - `GLPIClient` (init/kill session, leitura de metadados, createTicket, uploadDocument).
  - `MetadataCache` e `NameToIdResolver` (categoria/localização/request type).

## Fluxo de Integração
- Usuário logado escolhe categoria → formulário específico.
- Usuário preenche e envia.
- Backend recebe payload, aplica mapeamento e autentica com `user_token + app_token`.
- Backend `POST /Ticket` + resposta com `ticket_id`.
- Backend opcionalmente faz upload de anexo.
- Frontend exibe sucesso/erro.

## Segurança, Validação e Logs
- Não expor tokens/URL interna; segredos somente no backend.
- Validação pré-GLPI: obrigatórios e coerência de tipos/IDs.
- Resiliência: retry/backoff; fila offline no backend.
- Logs com mascaramento; auditoria por `ticket_id`; sanitização de `content`.

## Checklist Final
- Inventário completo de formulários e campos.
- Resumo da API GLPI (autenticação, criação de ticket, enums, metadados).
- Levantamento real (categorias, localizações, tipos de solicitação) em leitura.
- Mapeamento campo↔GLPI com regras e estratégia de nome→ID.
- Planos por categoria com etapas de implementação e testes.
- Arquitetura e fluxo de integração (frontend→backend→GLPI).
- Pontos de atenção de segurança, validação e UX.

## Observação de Autenticação
- Testes de `initSession` com usuário/senha (Basic/POST) foram rejeitados neste ambiente, sugerindo política local restritiva para essas credenciais.
- Leituras e operações planejadas devem usar `user_token + app_token` com sessão temporária.
## Tabelas nome→ID por Categoria (parciais)

### Ar-Condicionado — Tipos (ITILCategory)
| Rótulo do Formulário | ID GLPI | Nome GLPI | Observações |
|---|---|---|---|
| Manutenção Preventiva Agendada | N/A | N/A | Requer busca em subcategoria/termo composto |
| Aparelho Não Liga | N/A | N/A | Requer busca em subcategoria/termo composto |
| Vazamento/Gotejamento | N/A | N/A | Requer busca em subcategoria/termo composto |
| Barulho Anormal | N/A | N/A | Requer busca em subcategoria/termo composto |

### Ar-Condicionado — Localizações (Location)
| Rótulo do Formulário | ID GLPI | Nome GLPI | Observações |
|---|---|---|---|
| Sala/Escritório | N/A | N/A | Resolver por correspondência aproximada ("Escritório/Sala") |
| Sala de Reunião | N/A | N/A | Resolver por correspondência aproximada ("Sala") |
| Área Técnica/Servidores | N/A | N/A | Resolver por correspondência aproximada ("Área Técnica/Servidores") |

### Elétrica — Tipos (ITILCategory)
| Rótulo do Formulário | ID GLPI | Nome GLPI | Observações |
|---|---|---|---|
| Troca de Lâmpada | N/A | N/A | Requer busca em subcategoria/termo composto |
| Tomada Queimada | N/A | N/A | Requer busca em subcategoria/termo composto |
| Problema em Quadro Elétrico | N/A | N/A | Requer busca em subcategoria/termo composto |
| Curto Circuito | N/A | N/A | Requer busca em subcategoria/termo composto |

### Vidraçaria — Tipos (ITILCategory)
| Rótulo do Formulário | ID GLPI | Nome GLPI | Observações |
|---|---|---|---|
| Vidro Quebrado | N/A | N/A | Requer busca em subcategoria/termo composto |
| Manutenção de Esquadria | N/A | N/A | Requer busca em subcategoria/termo composto |
| Troca de Borracha/Vedação | N/A | N/A | Requer busca em subcategoria/termo composto |

### Carregadores — Exemplos confirmados por leitura (ITILCategory)
| Rótulo Observado | ID GLPI | Nome GLPI | Fonte |
|---|---|---|---|
| Carregadores | 55 | Conservação > Carregadores | Link em Ticket (leitura) |
| Movimentação de Insumos | 56 | Conservação > Carregadores > Movimentação de Insumos | Link em Ticket (leitura) |
| Movimentação Mobiliário | 103 | Conservação > Carregadores > Movimentação Mobiliário | Link em Ticket (leitura) |

### Mensageria — Exemplos confirmados por leitura (ITILCategory)
| Rótulo Observado | ID GLPI | Nome GLPI | Fonte |
|---|---|---|---|
| Mensageria | 128 | Conservação > Mensageria | Link em Ticket (leitura) |
| Movimentação de Documentos | 129 | Conservação > Mensageria > Movimentação Documentos | Link em Ticket (leitura) |

### Principais Categorias (confirmadas por leitura)
| ID GLPI | Nome GLPI |
|---|---|
| 1 | Ar Condicionado |
| 22 | Elétrica |
| 17 | Elevadores |
| 27 | Troca |
| 26 | Readequação |
| 6 | Remanejo |
| 29 | Suporte |
| 2 | Conserto |
| 23 | Conserto |
| 4 | Instalação |
| 24 | Instalação |
| 28 | Descarte |
| 7 | Outras atividades |

### Principais Localizações (confirmadas por leitura)
| ID GLPI | Nome GLPI |
|---|---|
| 8 | Palácio Piratini |
| 19 | Defesa Civil - Andrade Neves |
| 20 | 11º Andar |
| 22 | 15º Andar |
| 30 | 3º Andar |
| 1 | Casa Civil 1005 |
| 10 | Casa Branca |
| 11 | Casa Militar |
| 18 | GVG - Edificio Guaiba - 11º Andar |
| 27 | Limpeza |
| 31 | Jardinagem |

### Notas de Resolução
- As opções de “Tipo” dos formulários que não apareceram nas listas planas exigem busca dirigida por termos compostos e/ou navegação de subárvores de `ITILCategory`.
- As opções de “Localização” genéricas (ex.: “Sala/Escritório”, “Sala de Reunião”) requerem correspondência aproximada com nomes de `Location` existentes no GLPI.
- Todas as coletas e validações são realizadas com sessão temporária (`user_token + app_token`) e encerradas em seguida, em modo leitura.

## Proposta de Estrutura-Alvo do App (somente documentação)

### Diretrizes de Simplificação
- Manter: `lib/` (telas, widgets, serviços, estado, dados), `assets/images/`, `pubspec.yaml`, `analysis_options.yaml`, plataformas alvo (Android/iOS).
- Simplificar: substituir múltiplas telas específicas por configuração (um único `FormTemplate` dirigível por dados), manter “Meus Chamados” como placeholder até o backend.
- Remover do repositório da app: SDK Flutter (`external-projects/flutter-sdk/flutter`), zips de SDK (`flutter_windows_*.zip`), plataformas não-alvo (web/linux/macos/windows) se o foco for mobile.
- Opcional: adiar `test/` se houver urgência de simplificação (recomendado manter a médio prazo).

### Estrutura-Alvo (proposta)
- `lib/`
  - `features/auth/login_screen.dart` — tela de login
  - `features/catalog/service_catalog_screen.dart` — catálogo e navegação
  - `features/forms/form_template.dart` — formulário genérico
  - `features/forms/config/` — opções por categoria (flags, listas, extras)
  - `services/glpi_client.dart` — contrato/mock (integração real no backend)
  - `state/app_state.dart` — estado (apenas o necessário ao frontend)
  - `widgets/` — campos reutilizáveis (texto, select, anexo)
- `assets/images/` — logos
- `android/`, `ios/` — plataformas alvo
- `pubspec.yaml`, `analysis_options.yaml`

### Itens Irrelevantes ao Escopo (explicações)
- `external-projects/flutter-sdk/flutter`: checkout do SDK Flutter, não pertence ao repositório da aplicação; o SDK deve ser instalado no ambiente.
- `external-projects/flutter_windows_*.zip`: pacotes de distribuição do SDK; não devem ser versionados junto com a app.
- `web/`, `linux/`, `macos/`, `windows/` dentro do app: gerados por scaffold multi-plataforma; dispensáveis se o alvo é apenas Android/iOS.
- Múltiplas telas por serviço: replicam `FormTemplate` com poucas diferenças; podem ser substituídas por configuração única e manutenção centralizada.

### Plano de Migração (sem implementação)
- Etapa 1: inventariar telas/arquivos que permanecem (login, catálogo, `FormTemplate`, widgets, estado mínimo, serviço mock) e os que se tornam configuração.
- Etapa 2: extrair opções por categoria (flags e listas) para `features/forms/config/` sem alterar UI/UX.
- Etapa 3: remover (do projeto) plataformas não-alvo e artefatos de SDK, mantendo apenas Android/iOS.
- Etapa 4: documentar contrato do backend (`POST /api/tickets`, metadados e upload de anexo) e mover lógica real de GLPI para servidor.
- Etapa 5: validar funcionalidade end-to-end em homologação (somente leitura para metadados e criação controlada de tickets quando apropriado).
