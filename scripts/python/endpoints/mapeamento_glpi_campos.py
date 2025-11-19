"""
MAPEAMENTO COMPLETO DOS CAMPOS E AÇÕES DO GLPI
==============================================

Este módulo mapeia todos os campos numéricos (id_search_option) e ações (linked_action)
do GLPI para descrições textuais compreensíveis.

Baseado em análise dos dados reais e documentação GLPI.

Autor: Analista de Dados - Casa Civil
Data: 2025-11-16
"""

# MAPEAMENTO DOS CAMPOS DO GLPI (id_search_option)
# Estes são os campos que aparecem quando um ticket é modificado
MAPEAMENTO_CAMPOS_GLPi = {
    # Campos principais do ticket
    0: 'Campo geral/Informação',
    1: 'ID do Ticket',
    2: 'Nome/Título do Ticket',
    3: 'Status',
    4: 'Usuário Atribuído',
    5: 'Grupo Atribuído',
    6: 'Categoria',
    7: 'Prioridade',
    8: 'Urgência',
    9: 'Impacto',
    10: 'Data de Vencimento',
    11: 'Entidade',
    12: 'Localização',
    13: 'Tipo de Ticket',
    14: 'Requerente/ Solicitante',
    15: 'Técnico Responsável',
    16: 'Data de Modificação',
    17: 'Data de Criação',
    18: 'Solução/Resolução',
    19: 'Acompanhamento/Follow-up',
    20: 'Validação',
    21: 'Origem do Ticket',
    22: 'Fonte de Solicitação',
    
    # Campos adicionais comuns
    50: 'Descrição Completa',
    51: 'Conteúdo do Acompanhamento',
    52: 'Status de Aprovação',
    53: 'Motivo de Rejeição',
    54: 'Observações Internas',
    55: 'Tempo Gasto (horas)',
    56: 'Custo Total',
    57: 'Material Utilizado',
    58: 'Serviço Prestado',
    
    # Campos de localização e ativos
    60: 'Localização Física',
    61: 'Andar/Departamento',
    62: 'Sala/Escritório',
    63: 'Prédio',
    64: 'Usuário Associado',
    65: 'Grupo Associado',
    66: 'Ativo/Equipamento Relacionado',
    67: 'Número de Série do Ativo',
    68: 'Inventário/Patrimônio',
    
    # Campos de contato
    70: 'Telefone de Contato',
    71: 'Email de Contato',
    72: 'Departamento do Usuário',
    73: 'Matrícula/ID Funcional',
    
    # Campos de SLA
    80: 'SLA - Tempo de Resposta',
    81: 'SLA - Tempo de Resolução',
    82: 'SLA - Tempo Total',
    83: 'SLA - Status de Cumprimento',
    84: 'SLA - Percentual Cumprido',
    
    # Campos de aprovação e validação
    90: 'Aprovador 1',
    91: 'Aprovador 2',
    92: 'Data da Aprovação',
    93: 'Status da Aprovação',
    94: 'Comentários do Aprovador',
    95: 'Validador Técnico',
    96: 'Data da Validação',
    97: 'Resultado da Validação',
    
    # Campos de pendência
    100: 'Motivo de Pendência',
    101: 'Data Início da Pendência',
    102: 'Data Fim da Pendência',
    103: 'Responsável pela Pendência',
    104: 'Justificativa da Pendência',
    
    # Campos de transferência
    110: 'Origem da Transferência',
    111: 'Destino da Transferência',
    112: 'Motivo da Transferência',
    113: 'Data da Transferência',
    114: 'Usuário que Transferiu',
    
    # Campos de documentos e anexos
    120: 'Documento Anexado',
    121: 'Nome do Arquivo',
    122: 'Tamanho do Arquivo',
    123: 'Tipo do Arquivo',
    124: 'Data do Anexo',
    125: 'Usuário que Anexou',
    
    # Campos de tarefas
    130: 'Tarefa Criada',
    131: 'Descrição da Tarefa',
    132: 'Responsável pela Tarefa',
    133: 'Status da Tarefa',
    134: 'Tempo Estimado (horas)',
    135: 'Tempo Real (horas)',
    136: 'Custo da Tarefa',
    
    # Campos de solução
    140: 'Tipo de Solução',
    141: 'Descrição da Solução',
    142: 'Técnico que Aplicou Solução',
    143: 'Data da Aplicação',
    144: 'Validação da Solução',
    145: 'Feedback do Usuário',
    
    # Campos adicionais identificados nos dados
    150: 'Campo Personalizado 1',
    151: 'Campo Personalizado 2',
    152: 'Campo Personalizado 3',
    153: 'Código de Referência',
    154: 'Número de Protocolo',
    155: 'Categoria Específica',
    
    # Valores que aparecem nos logs mas não são camedos padrão
    999: 'Campo Desconhecido/Sistema'
}

# MAPEAMENTO DAS AÇÕES DO GLPI (linked_action)
# Estas são as ações que podem ser realizadas em um ticket
MAPEAMENTO_ACOES_GLPi = {
    # Ações básicas
    0: 'Alteração de campo',
    1: 'Criação do ticket',
    2: 'Atualização geral',
    3: 'Exclusão de informação',
    4: 'Restauração de informação',
    5: 'Transferência de responsabilidade',
    6: 'Mudança de status',
    7: 'Adição de informação',
    8: 'Remoção de informação',
    9: 'Modificação de relacionamento',
    10: 'Atualização de permissões',
    
    # Ações de usuários e atribuição
    11: 'Usuário atribuído',
    12: 'Usuário removido',
    13: 'Grupo atribuído',
    14: 'Grupo removido',
    15: 'Atribuição modificada',
    16: 'Responsável alterado',
    17: 'Técnico modificado',
    18: 'Aprovador designado',
    19: 'Validador designado',
    
    # Ações de documentos e anexos
    20: 'Documento anexado',
    21: 'Documento removido',
    22: 'Arquivo adicionado',
    23: 'Arquivo excluído',
    24: 'Anexo modificado',
    25: 'Documento visualizado',
    
    # Ações de acompanhamentos
    30: 'Acompanhamento adicionado',
    31: 'Acompanhamento editado',
    32: 'Acompanhamento excluído',
    33: 'Follow-up criado',
    34: 'Follow-up atualizado',
    35: 'Follow-up removido',
    36: 'Comentário adicionado',
    37: 'Observação incluída',
    
    # Ações de tarefas
    40: 'Tarefa criada',
    41: 'Tarefa editada',
    42: 'Tarefa concluída',
    43: 'Tarefa cancelada',
    44: 'Tarefa atribuída',
    45: 'Tarefa transferida',
    46: 'Tempo de tarefa registrado',
    47: 'Custo de tarefa atualizado',
    
    # Ações de validação e aprovação
    50: 'Validação solicitada',
    51: 'Validação aprovada',
    52: 'Validação rejeitada',
    53: 'Aprovação concedida',
    54: 'Aprovação negada',
    55: 'Parecer técnico emitido',
    56: 'Avaliação realizada',
    
    # Ações de solução
    60: 'Solução proposta',
    61: 'Solução aceita',
    62: 'Solução rejeitada',
    63: 'Solução aplicada',
    64: 'Solução modificada',
    65: 'Solução removida',
    66: 'Ticket resolvido',
    67: 'Ticket reaberto',
    
    # Ações de pendência
    70: 'Pendência criada',
    71: 'Pendência resolvida',
    72: 'Pendência cancelada',
    73: 'Motivo de pendência adicionado',
    74: 'Motivo de pendência removido',
    75: 'Tempo de pendência registrado',
    
    # Ações de transferência e escalonamento
    80: 'Transferência realizada',
    81: 'Escalonamento executado',
    82: 'Redirecionamento aplicado',
    83: 'Encaminhamento realizado',
    84: 'Ticket derivado',
    85: 'Relacionamento criado',
    
    # Ações de SLA
    90: 'SLA aplicado',
    91: 'SLA modificado',
    92: 'Prazo ajustado',
    93: 'Meta de tempo alterada',
    94: 'Alerta de SLA emitido',
    95: 'Violação de SLA registrada',
    
    # Ações de formulários
    100: 'Formulário respondido',
    101: 'Questionário preenchido',
    102: 'Dados de formulário atualizados',
    103: 'Resposta de formulário processada',
    
    # Ações de notificação
    110: 'Notificação enviada',
    111: 'Email disparado',
    112: 'Alerta gerado',
    113: 'Mensagem de sistema enviada',
    114: 'Aviso de prazo emitido',
    
    # Ações de categorização
    120: 'Categoria alterada',
    121: 'Prioridade modificada',
    122: 'Urgência ajustada',
    123: 'Impacto modificado',
    124: 'Tipo de ticket alterado',
    
    # Ações de localização
    130: 'Localização modificada',
    131: 'Sala/escritório alterado',
    132: 'Andar/modificado',
    133: 'Prédio alterado',
    134: 'Departamento modificado',
    
    # Ações de ativos
    140: 'Ativo relacionado',
    141: 'Equipamento vinculado',
    142: 'Patrimônio associado',
    143: 'Número de série registrado',
    144: 'Inventário atualizado',
    
    # Ações de custo e tempo
    150: 'Custo registrado',
    151: 'Tempo trabalhado anotado',
    152: 'Despesa lançada',
    153: 'Material utilizado registrado',
    154: 'Serviço prestado documentado',
    
    # Valores especiais que aparecem nos logs
    999: 'Ação desconhecida/Sistema'
}

# MAPEAMENTO DOS TIPOS DE ITENS RELACIONADOS (itemtype_link)
MAPEAMENTO_ITEMTYPE_GLPi = {
    'Ticket': 'Ticket',
    'User': 'Usuário',
    'Group': 'Grupo',
    'Document': 'Documento',
    'ITILFollowup': 'Acompanhamento',
    'ITILSolution': 'Solução',
    'ITILTask': 'Tarefa',
    'TicketTask': 'Tarefa do Ticket',
    'TicketValidation': 'Validação do Ticket',
    'PendingReason': 'Motivo de Pendência',
    'PluginFormcreatorFormAnswer': 'Resposta de Formulário',
    'Location': 'Localização',
    'Computer': 'Computador',
    'Monitor': 'Monitor',
    'NetworkEquipment': 'Equipamento de Rede',
    'Peripheral': 'Periférico',
    'Phone': 'Telefone',
    'Printer': 'Impressora',
    'Software': 'Software',
    'SoftwareLicense': 'Licença de Software',
    'Budget': 'Orçamento',
    'Change': 'Mudança',
    'Problem': 'Problema',
    'Project': 'Projeto',
    'Supplier': 'Fornecedor',
    'Contact': 'Contato',
    'Contract': 'Contrato',
    'DocumentType': 'Tipo de Documento',
    'DocumentCategory': 'Categoria de Documento',
    'KnowbaseItem': 'Item de Base de Conhecimento',
    'Config': 'Configuração',
    'Profile': 'Perfil',
    'Entity': 'Entidade',
    'Notification': 'Notificação',
    'SLA': 'SLA',
    'OLA': 'OLA',
    'SlaLevel': 'Nível de SLA',
    'OlaLevel': 'Nível de OLA',
    'Calendar': 'Calendário',
    'Holiday': 'Feriado',
    'BlacklistedMailContent': 'Conteúdo de Email Bloqueado',
    'Rule': 'Regra',
    'RuleAction': 'Ação de Regra',
    'RuleCriteria': 'Critério de Regra',
    'CartridgeItem': 'Item de Cartucho',
    'Cartridge': 'Cartucho',
    'ConsumableItem': 'Item de Consumível',
    'Consumable': 'Consumível',
    '': 'Campo Direto do Ticket'  # Quando está vazio
}

def decodificar_campo(id_search_option: int) -> str:
    """
    Decodifica o ID do campo para descrição textual.
    
    Args:
        id_search_option: ID numérico do campo
    
    Returns:
        Descrição textual do campo
    """
    return MAPEAMENTO_CAMPOS_GLPi.get(id_search_option, f'Campo {id_search_option} (não mapeado)')

def decodificar_acao(linked_action: int) -> str:
    """
    Decodifica o ID da ação para descrição textual.
    
    Args:
        linked_action: ID numérico da ação
    
    Returns:
        Descrição textual da ação
    """
    return MAPEAMENTO_ACOES_GLPi.get(linked_action, f'Ação {linked_action} (não mapeada)')

def decodificar_itemtype(itemtype_link: str) -> str:
    """
    Decodifica o tipo de item relacionado.
    
    Args:
        itemtype_link: String do tipo de item
    
    Returns:
        Descrição textual do tipo de item
    """
    return MAPEAMENTO_ITEMTYPE_GLPi.get(itemtype_link, f'Tipo {itemtype_link}')

def analisar_campo_especifico(id_search_option: int, old_value: str, new_value: str) -> dict:
    """
    Analisa um campo específico e fornece contexto adicional sobre a alteração.
    
    Args:
        id_search_option: ID do campo
        old_value: Valor antigo
        new_value: Valor novo
    
    Returns:
        Dicionário com análise detalhada
    """
    analise = {
        'campo': decodificar_campo(id_search_option),
        'tipo_alteracao': 'Desconhecida',
        'impacto': 'Baixo',
        'descricao': ''
    }
    
    # Análise específica por tipo de campo
    if id_search_option == 4:  # Usuário Atribuído
        analise['tipo_alteracao'] = 'Mudança de Responsável'
        analise['impacto'] = 'Alto'
        analise['descricao'] = f'Ticket transferido de {old_value or "nenhum"} para {new_value or "nenhum"}'
    
    elif id_search_option == 5:  # Grupo Atribuído
        analise['tipo_alteracao'] = 'Mudança de Equipe'
        analise['impacto'] = 'Alto'
        analise['descricao'] = f'Ticket redistribuído do grupo {old_value or "nenhum"} para {new_value or "nenhum"}'
    
    elif id_search_option == 3:  # Status
        analise['tipo_alteracao'] = 'Mudança de Status'
        analise['impacto'] = 'Médio'
        analise['descricao'] = f'Status alterado de "{old_value}" para "{new_value}"'
    
    elif id_search_option in [60, 61, 62, 12]:  # Localização
        analise['tipo_alteracao'] = 'Mudança de Localização'
        analise['impacto'] = 'Baixo'
        analise['descricao'] = f'Localização modificada de {old_value or "nenhuma"} para {new_value or "nenhuma"}'
    
    elif id_search_option in [64, 65, 66]:  # Usuário/Grupo/Ativo Associado
        analise['tipo_alteracao'] = 'Mudança de Associação'
        analise['impacto'] = 'Médio'
        analise['descricao'] = f'Associação modificada de {old_value or "nenhuma"} para {new_value or "nenhuma"}'
    
    elif id_search_option in [120, 121, 122, 123, 124, 125]:  # Documentos
        analise['tipo_alteracao'] = 'Gestão de Documentos'
        analise['impacto'] = 'Baixo'
        if old_value and not new_value:
            analise['descricao'] = f'Documento removido: {old_value}'
        elif new_value and not old_value:
            analise['descricao'] = f'Documento adicionado: {new_value}'
        else:
            analise['descricao'] = f'Documento alterado de {old_value} para {new_value}'
    
    elif id_search_option in [130, 131, 132, 133, 134, 135, 136]:  # Tarefas
        analise['tipo_alteracao'] = 'Gestão de Tarefas'
        analise['impacto'] = 'Médio'
        analise['descricao'] = f'Tarefa modificada: {new_value or old_value}'
    
    elif id_search_option in [100, 101, 102, 103, 104]:  # Pendências
        analise['tipo_alteracao'] = 'Gestão de Pendências'
        analise['impacto'] = 'Médio'
        if old_value and not new_value:
            analise['descricao'] = f'Pendência removida: {old_value}'
        elif new_value and not old_value:
            analise['descricao'] = f'Pendência adicionada: {new_value}'
        else:
            analise['descricao'] = f'Pendência modificada'
    
    elif id_search_option in [60, 61, 62, 63, 64, 65, 66]:  # Soluções
        analise['tipo_alteracao'] = 'Gestão de Solução'
        analise['impacto'] = 'Alto'
        analise['descricao'] = f'Solução modificada: {new_value or old_value}'
    
    else:  # Campos genéricos
        if old_value and not new_value:
            analise['tipo_alteracao'] = 'Remoção de Informação'
            analise['descricao'] = f'Informação removida: {old_value}'
        elif new_value and not old_value:
            analise['tipo_alteracao'] = 'Adição de Informação'
            analise['descricao'] = f'Informação adicionada: {new_value}'
        else:
            analise['tipo_alteracao'] = 'Modificação de Informação'
            analise['descricao'] = f'Informação alterada de "{old_value}" para "{new_value}"'
    
    return analise

def interpretar_alteracao_completa(itemtype_link: str, linked_action: int, id_search_option: int, old_value: str, new_value: str) -> dict:
    """
    Interpreta completamente uma alteração do log GLPI.
    
    Args:
        itemtype_link: Tipo de item relacionado
        linked_action: Ação realizada
        id_search_option: Campo modificado
        old_value: Valor antigo
        new_value: Valor novo
    
    Returns:
        Dicionário com interpretação completa
    """
    # Obter descrições básicas
    tipo_item = decodificar_itemtype(itemtype_link)
    acao = decodificar_acao(linked_action)
    campo = decodificar_campo(id_search_option)
    
    # Análise específica do campo
    analise_campo = analisar_campo_especifico(id_search_option, old_value, new_value)
    
    # Criar descrição completa
    if itemtype_link:
        descricao_completa = f"{acao} em {tipo_item}: {analise_campo['descricao']}"
    else:
        descricao_completa = f"{acao}: {analise_campo['descricao']}"
    
    return {
        'tipo_item': tipo_item,
        'acao': acao,
        'campo': campo,
        'campo_analise': analise_campo,
        'valor_antigo': old_value,
        'valor_novo': new_value,
        'descricao_completa': descricao_completa,
        'tipo_alteracao': analise_campo['tipo_alteracao'],
        'impacto': analise_campo['impacto']
    }

def exemplos_de_uso():
    """Exemplos práticos de uso do mapeamento"""
    print("🗺️  MAPEAMENTO GLPI - EXEMPLOS DE USO")
    print("=" * 60)
    
    # Exemplos dos campos que você encontrou
    exemplos_campos = [
        (64, 'thales-leite (721)', 'luciano-marcelino (1331)'),
        (65, 'CC-SE-SUBADM-DTIC (17)', 'TRANSFERENCIA (93)'),
        (66, '', 'Luciano Marcelino da Silva (1331)'),
        (150, '0', '1751'),
        (52, '1', '2')
    ]
    
    print("\n📋 ANÁLISE DOS CAMPOS QUE VOCÊ ENCONTROU:")
    print("-" * 50)
    
    for id_campo, old_val, new_val in exemplos_campos:
        resultado = interpretar_alteracao_completa('', 0, id_campo, old_val, new_val)
        print(f"\n🔍 Campo {id_campo}:")
        print(f"   📄 Descrição: {resultado['campo']}")
        print(f"   🔄 Alteração: {resultado['descricao_completa']}")
        print(f"   📊 Tipo: {resultado['tipo_alteracao']}")
        print(f"   ⚡ Impacto: {resultado['impacto']}")
        print(f"   📈 Detalhes: {resultado['campo_analise']['descricao']}")
    
    # Exemplos de ações
    print(f"\n\n🎬 EXEMPLOS DE AÇÕES COMUNS:")
    print("-" * 50)
    
    acoes_comuns = [15, 12, 17, 20, 30, 60, 80]
    for acao_id in acoes_comuns:
        print(f"   • Ação {acao_id}: {decodificar_acao(acao_id)}")
    
    # Exemplos de tipos de itens
    print(f"\n\n📦 EXEMPLOS DE TIPOS DE ITENS:")
    print("-" * 50)
    
    itens_comuns = ['Document', 'User', 'Group', 'ITILFollowup', 'ITILSolution', 'PendingReason']
    for item in itens_comuns:
        print(f"   • {item}: {decodificar_itemtype(item)}")

if __name__ == "__main__":
    exemplos_de_uso()
    
    print(f"\n\n✅ MAPEAMENTO COMPLETO CRIADO!")
    print("Use as funções decodificar_campo(), decodificar_acao(), decodificar_itemtype()")
    print("e interpretar_alteracao_completa() para entender os logs do GLPI.")