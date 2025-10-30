# Configuração de Agendamento Automático - Pipeline GLPI

Este documento fornece instruções para configurar a execução automática do pipeline de extração e análise de dados GLPI a cada 60 minutos.

## 📋 Opções Disponíveis

### 1. Script de Execução Única (`scheduler.py`)
- **Uso**: Executa o pipeline uma única vez
- **Comando**: `python scheduler.py`
- **Ideal para**: Testes e execuções manuais

### 2. Script de Execução Contínua (`continuous_scheduler.py`)
- **Uso**: Executa continuamente, rodando o pipeline a cada 60 minutos
- **Comando**: `python continuous_scheduler.py`
- **Ideal para**: Servidores dedicados ou execução em segundo plano

### 3. Windows Task Scheduler (Recomendado)
- **Uso**: Agendamento nativo do Windows
- **Ideal para**: Ambientes de produção e estações de trabalho

## 🔧 Configuração do Windows Task Scheduler

### Passo 1: Abrir o Agendador de Tarefas
1. Pressione `Win + R`
2. Digite `taskschd.msc` e pressione Enter
3. Ou procure por "Agendador de Tarefas" no menu Iniciar

### Passo 2: Criar Nova Tarefa
1. No painel direito, clique em **"Criar Tarefa..."**
2. **NÃO** use "Criar Tarefa Básica" - use "Criar Tarefa" para ter mais opções

### Passo 3: Configurar Aba "Geral"
- **Nome**: `Pipeline GLPI - Extração Automática`
- **Descrição**: `Execução automática do pipeline de extração e análise de dados GLPI a cada 60 minutos`
- **Opções de Segurança**:
  - ☑️ Executar estando o usuário conectado ou não
  - ☑️ Executar com privilégios mais altos
  - **Configurar para**: Windows 10/Windows Server 2016

### Passo 4: Configurar Aba "Disparadores"
1. Clique em **"Novo..."**
2. **Iniciar a tarefa**: Segundo uma agenda
3. **Configurações**:
   - ☑️ Diariamente
   - **Iniciar**: [Data atual]
   - **Hora de início**: 00:00:00 (ou horário desejado)
   - **Repetir a cada**: 1 hora
   - **Por um período de**: 1 dia
   - ☑️ Habilitado
4. Clique em **"OK"**

### Passo 5: Configurar Aba "Ações"
1. Clique em **"Novo..."**
2. **Ação**: Iniciar um programa
3. **Programa/script**: 
   ```
   python
   ```
4. **Adicionar argumentos**:
   ```
   scheduler.py
   ```
5. **Iniciar em**:
   ```
   C:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\scripts\python
   ```
6. Clique em **"OK"**

### Passo 6: Configurar Aba "Condições"
- **Energia**:
  - ☐ Iniciar a tarefa apenas se o computador estiver conectado à energia CA
  - ☐ Parar se o computador alternar para energia da bateria
  - ☑️ Ativar o computador para executar esta tarefa

- **Rede**:
  - ☐ Iniciar apenas se a seguinte conexão de rede estiver disponível

### Passo 7: Configurar Aba "Configurações"
- ☑️ Permitir que a tarefa seja executada sob demanda
- ☑️ Executar a tarefa assim que possível após um início agendado perdido
- ☑️ Se a tarefa falhar, reiniciar a cada: 1 minuto
- **Tentar reiniciar até**: 3 vezes
- **Parar a tarefa se ela for executada por mais de**: 30 minutos
- **Se a instância em execução não terminar quando solicitado, forçar parada**
- ☑️ Se a tarefa não estiver agendada para ser executada novamente, exclua-a após: 30 dias

### Passo 8: Finalizar
1. Clique em **"OK"**
2. Digite a senha do usuário se solicitado
3. A tarefa aparecerá na lista do Agendador de Tarefas

## 🧪 Testando a Configuração

### Teste Manual da Tarefa
1. No Agendador de Tarefas, localize sua tarefa
2. Clique com o botão direito e selecione **"Executar"**
3. Verifique se a execução foi bem-sucedida na aba "Histórico"

### Verificação de Logs
- **Log do Scheduler**: `scheduler.log`
- **Logs do Pipeline**: Verifique os logs gerados pelo `main.py`

## 📁 Estrutura de Arquivos

```
scripts/python/
├── scheduler.py                    # Execução única
├── continuous_scheduler.py         # Execução contínua
├── scheduler.log                   # Log do scheduler
├── main.py                        # Pipeline principal
├── extrair_todos_tickets.py       # Extração de tickets
├── extrair_metricas_tickets_otimizado.py  # Análise de métricas
└── CONFIGURACAO_AGENDAMENTO.md    # Este arquivo
```

## 🔍 Monitoramento

### Verificar Status da Tarefa
1. Abra o Agendador de Tarefas
2. Localize sua tarefa na lista
3. Verifique:
   - **Status**: Pronto/Em execução
   - **Última Execução**: Data e hora
   - **Próxima Execução**: Próximo agendamento
   - **Resultado da Última Execução**: Código de saída

### Logs de Execução
- **Scheduler Log**: `scheduler.log` - Contém logs detalhados de cada execução
- **Windows Event Log**: Logs do sistema Windows sobre a tarefa agendada

## ⚠️ Solução de Problemas

### Problema: Tarefa não executa
**Soluções**:
1. Verificar se o Python está no PATH do sistema
2. Verificar permissões do usuário
3. Testar execução manual: `python scheduler.py`
4. Verificar logs do Windows Event Viewer

### Problema: Pipeline falha
**Soluções**:
1. Verificar conectividade com a API GLPI
2. Verificar permissões de escrita no diretório de dados
3. Verificar logs em `scheduler.log`
4. Testar execução manual do `main.py`

### Problema: Execuções sobrepostas
**Solução**: O `scheduler.py` possui mecanismo de lock que previne execuções simultâneas

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `scheduler.log`
2. Testar execução manual dos scripts
3. Verificar configurações do Agendador de Tarefas
4. Consultar documentação do projeto no `README.md`

---

**Nota**: Este sistema foi projetado para funcionar de forma autônoma. Uma vez configurado, o pipeline será executado automaticamente a cada 60 minutos, mantendo os dados sempre atualizados.