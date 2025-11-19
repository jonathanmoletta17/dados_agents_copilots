import pandas as pd

def inspecionar_conteudo_real():
    """Inspeciona o conteúdo real dos tickets para entender a estrutura"""
    
    print("=== INSPEÇÃO DO CONTEÚDO REAL ===\n")
    
    # Carregar o arquivo original
    try:
        df = pd.read_excel('todos_tickets_atual.xlsx')
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        return
    
    print(f"Total de tickets: {len(df)}")
    print(f"Colunas disponíveis: {list(df.columns)}")
    
    # Verificar os primeiros 10 tickets completos
    print("\n=== PRIMEIROS 10 TICKETS COMPLETOS ===")
    for i in range(min(10, len(df))):
        print(f"\n--- TICKET {i+1} ---")
        for col in df.columns:
            valor = df.iloc[i][col]
            if pd.notna(valor):
                print(f"{col}: {str(valor)[:100]}{'...' if len(str(valor)) > 100 else ''}")
            else:
                print(f"{col}: (vazio)")
        print("-" * 80)
    
    # Procurar por padrões específicos
    print("\n=== PROCURANDO PADRÕES ESPECÍFICOS ===")
    
    padroes_procurados = [
        "Dados do formulário",
        "Dados Gerais",
        "TIPO :",
        "ORGANIZAÇÃO :",
        "1)",
        "2)",
        "3)",
        ":",
        "Formulário",
        "formulário"
    ]
    
    for padrao in padroes_procurados:
        encontrados = 0
        for idx, row in df.iterrows():
            for col in df.columns:
                if pd.notna(row[col]) and padrao in str(row[col]):
                    encontrados += 1
                    break
        print(f"'{padrao}': encontrado em {encontrados} tickets")
    
    # Verificar tickets com descrições longas
    print("\n=== TICKETS COM DESCRIÇÕES MAIS LONGAS ===")
    if 'Descricao' in df.columns:
        df_sorted = df.dropna(subset=['Descricao']).copy()
        df_sorted['desc_length'] = df_sorted['Descricao'].astype(str).str.len()
        df_sorted = df_sorted.sort_values('desc_length', ascending=False)
        
        print("Top 5 tickets com descrições mais longas:")
        for i, (idx, row) in enumerate(df_sorted.head(5).iterrows()):
            print(f"\n{i+1}. ID: {row.get('ID', idx)}")
            print(f"   Título: {row.get('Titulo', 'Sem título')}")
            print(f"   Tamanho: {row['desc_length']} caracteres")
            print(f"   Conteúdo: {str(row['Descricao'])[:200]}...")

if __name__ == "__main__":
    inspecionar_conteudo_real()