# Documentação da Estrutura de Dados

**Total de registros:** 2841
**Total de colunas:** 22

## Estrutura das Colunas

| Coluna | Tipo | Valores Únicos | Dados Ausentes | Descrição |
|--------|------|----------------|----------------|----------|
| id | Int64 | 2841 | 0 (0.0%) | Identificador único do ticket |
| titulo | object | 1430 | 0 (0.0%) | Título/assunto do ticket |
| descricao | object | 2766 | 16 (0.6%) | Descrição detalhada do problema |
| status | category | 6 | 0 (0.0%) | Status atual do ticket |
| prioridade | Int64 | 4 | 0 (0.0%) | Nível de prioridade (1-5) |
| urgencia | Int64 | 3 | 0 (0.0%) | Nível de urgência (1-5) |
| impacto | Int64 | 4 | 0 (0.0%) | Nível de impacto (1-5) |
| categoria | category | 50 | 0 (0.0%) | Categoria do problema |
| entidade | category | 38 | 0 (0.0%) | Entidade/departamento solicitante |
| requerente | object | 393 | 0 (0.0%) | Usuário que abriu o ticket |
| tecnico | object | 20 | 0 (0.0%) | Técnico responsável |
| grupo | category | 6 | 0 (0.0%) | Grupo técnico responsável |
| data_criacao | datetime64[ns] | 2772 | 0 (0.0%) | Data e hora de criação |
| data_modificacao | datetime64[ns] | 2824 | 0 (0.0%) | Data e hora da última modificação |
| data_solucao | datetime64[ns] | 2725 | 90 (3.2%) | Data e hora da solução |
| data_fechamento | datetime64[ns] | 1078 | 1753 (61.7%) | Data e hora do fechamento |
| tempo_solucao_min | int64 | 2315 | 0 (0.0%) | Tempo para solução em minutos |
| tempo_fechamento_min | int64 | 827 | 0 (0.0%) | Tempo para fechamento em minutos |
| satisfacao | float64 | 0 | 2841 (100.0%) | Avaliação de satisfação |
| tipo | Int64 | 2 | 0 (0.0%) | Tipo do ticket |
| localizacao | int64 | 39 | 0 (0.0%) | Localização física |
| validacao | int64 | 3 | 0 (0.0%) | Status de validação |
