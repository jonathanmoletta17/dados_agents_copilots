# Projeto GLPI - Suite de Ferramentas

Este repositório contém três projetos distintos relacionados ao GLPI (Gerenciador de Problemas e Inventário), agora organizados de forma limpa e profissional.

## 📁 Estrutura do Projeto

### 📋 01-glpi-api-atlas
**Mapeamento completo da API REST do GLPI**

- **Documentação OpenAPI**: Especificação completa dos endpoints
- **SDK Python**: Cliente Python para integração com a API GLPI
- **Exemplos**: Scripts de exemplo para uso da API
- **Coleções**: Arquivos Postman/Insomnia para testes

**Uso rápido:**
```python
from glpi_client import GLPIClient

client = GLPIClient(url="https://glpi.example.com", app_token="seu_token")
client.init_session(user_token="seu_user_token")
tickets = client.tickets.list()
```

### 📊 02-analise-dados-glpi  
**Análise e limpeza de dados de tickets**

- **Dados brutos**: CSVs originais exportados do GLPI
- **Dados processados**: Arquivos limpos e tratados (XLSX/CSV)
- **Scripts**: Ferramentas de limpeza e análise
- **Relatórios**: Métricas e análises geradas

**Arquivo principal:** `data/processed/todos_tickets_limpos_preciso.xlsx`

### 🔄 03-integracao-glpi
**Integração com banco de dados e sincronização**

- **Banco de dados**: SQLite com schema otimizado
- **ETL**: Scripts de extração, transformação e carga
- **Sincronização**: Automação de processos

**Banco principal:** `database/glpi.sqlite`

## 🚀 Começando

1. **Escolha seu projeto**: Cada pasta é independente
2. **Requisitos**: Veja os requirements específicos de cada projeto
3. **Documentação**: Cada projeto tem seu próprio README com instruções

## 📋 Status de Organização

✅ **Concluído** - Estrutura reorganizada e limpa  
✅ **Removidos** - 24 arquivos desnecessários  
✅ **Organizados** - 3 projetos claramente separados  
✅ **Documentados** - READMEs específicos para cada projeto

## 🎯 Objetivos Alcançados

- **Separação clara** de responsabilidades entre projetos
- **Eliminação de duplicatas** e arquivos temporários  
- **Estrutura profissional** e fácil de navegar
- **Preservação** de todo o trabalho importante realizado

## 📚 Documentação Adicional

- Veja `REORGANIZACAO_PROJETO.md` para detalhes da reorganização
- Cada subprojeto tem documentação específica em seu README
- Documentos técnicos estão em `.trae/documents/`

---

**💡 Dica**: Cada projeto pode ser usado independentemente. O API Atlas fornece acesso programático, a Análise de Dados trabalha com exportes CSV, e a Integração mantém um banco sincronizado.