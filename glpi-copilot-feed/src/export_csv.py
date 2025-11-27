import os
import pandas as pd
import numpy as np
from datetime import datetime
from src.db_extract import load_dtic_tickets

def ensure_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def calculate_monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera métricas mensais agregadas por ano_mes, entidade e grupo_nivel.
    Métricas: tickets_abertos, tickets_resolvidos, backlog_final, tempo_medio_resolucao_horas.
    """
    # Garantir que datas estão em datetime E remover timezone para comparação
    df['criado_em'] = pd.to_datetime(df['criado_em']).dt.tz_localize(None)
    df['solucionado_em'] = pd.to_datetime(df['solucionado_em']).dt.tz_localize(None)
    
    # Definir range de meses (do primeiro criado até hoje)
    if df.empty:
        return pd.DataFrame()

    min_date = df['criado_em'].min()
    max_date = datetime.now()
    months = pd.date_range(start=min_date, end=max_date, freq='MS') # Month Start

    metrics_list = []

    # Pre-calculate status mapping for resolution
    # Resolvidos: SOLUCIONADO, FECHADO
    resolved_mask = df['status'].isin(['SOLUCIONADO', 'FECHADO'])

    # Agrupamentos desejados
    # Para simplificar e não explodir a cardinalidade, vamos fazer:
    # 1. Geral (Entidade='TODAS', Nivel='TODOS')
    # 2. Por Entidade (Nivel='TODOS')
    # 3. Por Nivel (Entidade='TODAS')
    
    # Lista de combinações de dimensões para iterar
    # (entidade_filter, nivel_filter) -> se None, considera 'TODOS'
    
    # Extrair valores únicos para iteração
    entidades = df['entidade'].dropna().unique()
    niveis = df['grupo_nivel'].dropna().unique()

    # Estrutura para iterar meses
    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        ano_mes = month_start.strftime('%Y-%m')
        
        # Filtros base de tempo
        # Tickets abertos no mês: criado_em entre month_start e month_end
        created_in_month = (df['criado_em'] >= month_start) & (df['criado_em'] <= month_end)
        
        # Tickets resolvidos no mês: solucionado_em entre month_start e month_end
        resolved_in_month = (df['solucionado_em'] >= month_start) & (df['solucionado_em'] <= month_end)
        
        # Backlog final: Criado <= month_end AND (Solucionado > month_end OR Solucionado IS NULL)
        backlog_cond = (df['criado_em'] <= month_end) & (
            (df['solucionado_em'] > month_end) | (df['solucionado_em'].isna())
        )

        # Função auxiliar para calcular e adicionar linha
        def add_metric_row(sub_df_created, sub_df_resolved, sub_df_backlog, ent_label, lvl_label):
            abertos = len(sub_df_created)
            resolvidos = len(sub_df_resolved)
            backlog = len(sub_df_backlog)
            
            # Tempo médio (apenas dos resolvidos no mês)
            tempo_medio = 0.0
            if resolvidos > 0 and 'tempo_para_resolver' in sub_df_resolved.columns:
                # Converter segundos para horas
                # tempo_acao_total ou tempo_para_resolver? O prompt pede "tempo_resolucao".
                # Vamos usar tempo_acao_total se disponível (tempo real trabalhado) ou diff de datas.
                # Melhor usar a diferença de datas para "Lead Time"
                lead_times = (sub_df_resolved['solucionado_em'] - sub_df_resolved['criado_em']).dt.total_seconds() / 3600
                tempo_medio = lead_times.mean()

            metrics_list.append({
                'ano_mes': ano_mes,
                'entidade': ent_label,
                'grupo_nivel': lvl_label,
                'tickets_abertos': abertos,
                'tickets_resolvidos': resolvidos,
                'backlog_final': backlog,
                'tempo_medio_resolucao_horas': round(tempo_medio, 2)
            })

        # 1. Geral
        add_metric_row(df[created_in_month], df[resolved_in_month], df[backlog_cond], 'TODAS', 'TODOS')

        # 2. Por Entidade
        for ent in entidades:
            # Filtra DFs
            f_created = df[created_in_month & (df['entidade'] == ent)]
            f_resolved = df[resolved_in_month & (df['entidade'] == ent)]
            f_backlog = df[backlog_cond & (df['entidade'] == ent)]
            add_metric_row(f_created, f_resolved, f_backlog, ent, 'TODOS')

        # 3. Por Nivel
        for lvl in niveis:
            f_created = df[created_in_month & (df['grupo_nivel'] == lvl)]
            f_resolved = df[resolved_in_month & (df['grupo_nivel'] == lvl)]
            f_backlog = df[backlog_cond & (df['grupo_nivel'] == lvl)]
            add_metric_row(f_created, f_resolved, f_backlog, 'TODAS', lvl)

    # Filtrar linhas zeradas (não agregam valor analítico)
    df_result = pd.DataFrame(metrics_list)
    df_result = df_result[
        (df_result['tickets_abertos'] > 0) | 
        (df_result['tickets_resolvidos'] > 0) | 
        (df_result['backlog_final'] > 0)
    ]
    return df_result

def generate_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera rankings consolidados.
    """
    rankings_list = []
    
    # Filtro de período: Total desde 2023
    df_2023 = df[df['criado_em'] >= '2023-01-01']
    periodo = 'total_desde_2023'

    if df_2023.empty:
        return pd.DataFrame()

    # Helper para agregar
    def add_ranking(dimension, tipo_ranking):
        counts = df_2023[dimension].value_counts().reset_index()
        counts.columns = ['chave', 'tickets_total']
        counts['tipo_ranking'] = tipo_ranking
        counts['periodo'] = periodo
        # Reordenar colunas
        counts = counts[['tipo_ranking', 'periodo', 'chave', 'tickets_total']]
        return counts

    # Gerar rankings
    rank_tecnicos = add_ranking('tecnico', 'tecnico')
    # Filtrar técnicos inativos (padrão User <ID>)
    rank_tecnicos = rank_tecnicos[
        ~rank_tecnicos['chave'].str.contains(r'User \d+', regex=True, na=False)
    ]
    rankings_list.append(rank_tecnicos)
    
    rankings_list.append(add_ranking('entidade', 'entidade'))
    rankings_list.append(add_ranking('categoria', 'categoria'))
    if 'grupo_nivel' in df_2023.columns:
        rankings_list.append(add_ranking('grupo_nivel', 'grupo_nivel'))

    return pd.concat(rankings_list)

from src.api_extract import get_tasks, get_problems, get_changes, get_followups_count
from src.db_load import load_data_to_db

def generate_effort_metrics(df_tickets: pd.DataFrame, output_dir: str):
    """
    Gera métricas de esforço técnico cruzando Tickets (Banco) com Tarefas (API).
    """
    print("Gerando CSV de Esforço Técnico...")
    
    # Buscar tarefas da API
    try:
        df_tasks = get_tasks()
    except Exception as e:
        print(f"⚠️ Erro ao buscar tarefas da API: {e}")
        return

    if df_tasks.empty:
        print("⚠️ Nenhuma tarefa encontrada.")
        return

    # === SALVAR TAREFAS NO BANCO ===
    try:
        print("Salvando tarefas no banco de dados...")
        load_data_to_db(df_tasks, 'tickettasks', if_exists='replace')
    except Exception as e:
        print(f"⚠️ Erro ao salvar tarefas no banco: {e}")

    # Processar Tarefas
    # actiontime vem em segundos. Converter para horas.
    if 'actiontime' in df_tasks.columns:
        df_tasks['horas_trabalhadas'] = pd.to_numeric(df_tasks['actiontime'], errors='coerce').fillna(0) / 3600
    else:
        df_tasks['horas_trabalhadas'] = 0

    # Agrupar por Ticket
    # tickets_id é a chave estrangeira na tarefa
    effort_by_ticket = df_tasks.groupby('tickets_id')['horas_trabalhadas'].sum().reset_index()
    effort_by_ticket.columns = ['glpi_id', 'horas_trabalhadas']
    
    # Garantir tipo int para merge
    effort_by_ticket['glpi_id'] = pd.to_numeric(effort_by_ticket['glpi_id'], errors='coerce').fillna(0).astype('int64')
    
    # Cruzar com Tickets (para ter categoria, entidade, etc)
    # df_tickets tem 'glpi_id'
    df_merged = pd.merge(df_tickets, effort_by_ticket, on='glpi_id', how='inner')
    
    # Calcular Eficiência (Horas Trabalhadas / Tempo Resolução)
    # Tempo Resolução já existe em df_tickets como 'tempo_resolucao_horas'
    if 'tempo_resolucao_horas' in df_merged.columns:
        # Evitar divisão por zero
        df_merged['eficiencia_percentual'] = df_merged.apply(
            lambda x: (x['horas_trabalhadas'] / x['tempo_resolucao_horas'] * 100) 
            if x['tempo_resolucao_horas'] > 0 else 0, axis=1
        )
        df_merged['eficiencia_percentual'] = df_merged['eficiencia_percentual'].round(2)
        
    # Selecionar colunas finais
    cols = ['glpi_id', 'ano_mes', 'entidade', 'grupo_nivel', 'tecnico', 'categoria', 
            'tempo_resolucao_horas', 'horas_trabalhadas', 'eficiencia_percentual']
    
    final_cols = [c for c in cols if c in df_merged.columns]
    
    path = os.path.join(output_dir, "dtic_esforco_tecnico.csv")
    df_merged[final_cols].to_csv(path, index=False, encoding='utf-8-sig', sep=';')
    print(f"Salvo: {path}")

def generate_problems_changes(output_dir: str):
    """
    Gera CSV unificado de Problemas e Mudanças (ITIL).
    """
    print("Gerando CSV de Problemas e Mudanças...")
    try:
        df_probs = get_problems()
        df_changes = get_changes()
    except Exception as e:
        print(f"⚠️ Erro ao buscar Problemas/Mudanças: {e}")
        return

    # === SALVAR NO BANCO ===
    try:
        if not df_probs.empty:
            print("Salvando problemas no banco de dados...")
            load_data_to_db(df_probs, 'problems', if_exists='replace')
        
        if not df_changes.empty:
            print("Salvando mudanças no banco de dados...")
            load_data_to_db(df_changes, 'changes', if_exists='replace')
    except Exception as e:
        print(f"⚠️ Erro ao salvar no banco: {e}")

    items = []
    
    # Mapeamento de Status GLPI (Padrão)
    status_map = {
        1: 'Novo',
        2: 'Em Atendimento (Atribuído)',
        3: 'Planejado',
        4: 'Pendente',
        5: 'Solucionado',
        6: 'Fechado'
    }

    # Padronizar Problemas
    if not df_probs.empty:
        for _, row in df_probs.iterrows():
            st_id = row.get('status')
            items.append({
                'tipo': 'PROBLEMA',
                'id': row.get('id'),
                'titulo': row.get('name'),
                'status': status_map.get(st_id, st_id), # Nome ou ID se não achar
                'data_criacao': row.get('date'),
                'data_modificacao': row.get('date_mod')
            })
            
    # Padronizar Mudanças
    if not df_changes.empty:
        for _, row in df_changes.iterrows():
            st_id = row.get('status')
            items.append({
                'tipo': 'MUDANCA',
                'id': row.get('id'),
                'titulo': row.get('name'),
                'status': status_map.get(st_id, st_id),
                'data_criacao': row.get('date'),
                'data_modificacao': row.get('date_mod')
            })
            
    if items:
        df_itil = pd.DataFrame(items)
        path = os.path.join(output_dir, "dtic_problemas_mudancas.csv")
        df_itil.to_csv(path, index=False, encoding='utf-8-sig', sep=';')
        print(f"Salvo: {path}")
    else:
        print("⚠️ Nenhum Problema ou Mudança encontrado.")

def enrich_details_with_api(df_tickets: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona contagem de interações (Followups) ao dataframe de detalhes.
    """
    print("Enriquecendo dados com contagem de interações (API)...")
    try:
        # Retorna DF com [tickets_id, count]
        counts = get_followups_count()
        if not counts.empty:
            counts.columns = ['glpi_id', 'qtd_interacoes']
            # Garantir tipo int para merge
            counts['glpi_id'] = pd.to_numeric(counts['glpi_id'], errors='coerce').fillna(0).astype('int64')
            
            # Merge left para manter todos os tickets
            df_tickets = pd.merge(df_tickets, counts, on='glpi_id', how='left')
            df_tickets['qtd_interacoes'] = df_tickets['qtd_interacoes'].fillna(0).astype(int)
    except Exception as e:
        print(f"⚠️ Erro ao buscar followups: {e}")
        
    return df_tickets

def generate_all_csvs(output_dir: str) -> None:
    """
    Carrega tickets da DTIC, enriquece com API, gera os CSVs.
    """
    ensure_output_dir(output_dir)
    
    print("Carregando dados do banco...")
    df = load_dtic_tickets()
    
    if df.empty:
        print("Aviso: Nenhum dado encontrado no banco.")
        return

    # --- ENRIQUECIMENTO (API) ---
    # Adiciona qtd_interacoes
    df = enrich_details_with_api(df)

    # --- 1. Detalhe ---
    print("Gerando CSV de Detalhe...")
    cols_detalhe = [
        'glpi_id', 'ano', 'mes', 'ano_mes', 'status',
        'categoria', 'entidade', 'grupo', 'grupo_nivel', 'tecnico', 
        'requerente', 'criado_em', 'solucionado_em', 'fechado_em'
    ]
    
    if 'solucionado_em' in df.columns and 'criado_em' in df.columns:
        df['tempo_resolucao_horas'] = (df['solucionado_em'] - df['criado_em']).dt.total_seconds() / 3600
        df['tempo_resolucao_horas'] = df['tempo_resolucao_horas'].round(2)
        cols_detalhe.append('tempo_resolucao_horas')
    
    # Adicionar nova métrica se existir
    if 'qtd_interacoes' in df.columns:
        cols_detalhe.append('qtd_interacoes')

    cols_final = [c for c in cols_detalhe if c in df.columns]
    
    path_detalhe = os.path.join(output_dir, "dtic_tickets_detalhe.csv")
    df[cols_final].to_csv(path_detalhe, index=False, encoding='utf-8-sig', sep=';')
    print(f"Salvo: {path_detalhe}")

    # --- 2. Métricas Mensais ---
    print("Gerando CSV de Métricas Mensais...")
    df_metrics = calculate_monthly_metrics(df)
    path_metrics = os.path.join(output_dir, "dtic_metricas_mensais.csv")
    df_metrics.to_csv(path_metrics, index=False, encoding='utf-8-sig', sep=';')
    print(f"Salvo: {path_metrics}")

    # --- 3. Rankings ---
    print("Gerando CSV de Rankings...")
    df_rankings = generate_rankings(df)
    path_rankings = os.path.join(output_dir, "dtic_rankings.csv")
    df_rankings.to_csv(path_rankings, index=False, encoding='utf-8-sig', sep=';')
    print(f"Salvo: {path_rankings}")
    
    # --- 4. Esforço Técnico (Novo) ---
    generate_effort_metrics(df, output_dir)
    
    # --- 5. Problemas e Mudanças (Novo) ---
    generate_problems_changes(output_dir)

if __name__ == "__main__":
    generate_all_csvs("output")
