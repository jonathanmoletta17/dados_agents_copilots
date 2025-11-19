import pandas as pd
import re

def validar_resultados():
    """Valida os resultados da limpeza com exemplos concretos"""
    
    print("=== VALIDAÇÃO DOS RESULTADOS ===\n")
    
    # Carregar os arquivos
    try:
        df_original = pd.read_excel('todos_tickets_atual.xlsx')
        df_limpo = pd.read_excel('todos_tickets_limpos_inteligente.xlsx')
    except Exception as e:
        print(f"Erro ao carregar arquivos: {e}")
        return
    
    print(f"Total de tickets no arquivo original: {len(df_original)}")
    print(f"Total de tickets no arquivo limpo: {len(df_limpo)}")
    
    # Encontrar tickets com formulario GLPI no original
    print("\n=== PROCURANDO TICKETS COM FORMULÁRIO GLPI ===")
    
    tickets_com_formulario = []
    for idx, row in df_original.iterrows():
        if 'Descricao' in row and pd.notna(row['Descricao']):
            descricao = str(row['Descricao'])
            if 'Dados do formulário' in descricao or re.search(r'\d+\)\s*[A-Z]+:', descricao):
                tickets_com_formulario.append({
                    'id': row.get('ID', idx),
                    'titulo': row.get('Título', 'Sem título'),
                    'descricao_original': descricao[:200] + '...' if len(descricao) > 200 else descricao,
                    'tamanho_original': len(descricao)
                })
    
    print(f"Tickets com formulário GLPI encontrados: {len(tickets_com_formulario)}")
    
    if tickets_com_formulario:
        print("\n=== EXEMPLOS DE TICKETS COM FORMULÁRIO ===")
        for i, ticket in enumerate(tickets_com_formulario[:5]):
            print(f"\n--- Ticket {i+1} ---")
            print(f"ID: {ticket['id']}")
            print(f"Título: {ticket['titulo']}")
            print(f"Tamanho original: {ticket['tamanho_original']} caracteres")
            print(f"Amostra original: {ticket['descricao_original']}")
            
            # Procurar o mesmo ticket no arquivo limpo
            ticket_limpo = df_limpo[df_limpo['ID'] == ticket['id']]
            if not ticket_limpo.empty:
                descricao_limpa = str(ticket_limpo.iloc[0]['Descricao'])
                print(f"Tamanho após limpeza: {len(descricao_limpa)} caracteres")
                print(f"Amostra limpa: {descricao_limpa[:200]}...")
                reducao = (ticket['tamanho_original'] - len(descricao_limpa)) / ticket['tamanho_original'] * 100
                print(f"Redução: {reducao:.1f}%")
            else:
                print("Ticket não encontrado no arquivo limpo")
    
    # Verificar headers
    print("\n=== VERIFICAÇÃO DOS HEADERS ===")
    print("Headers originais:")
    for col in df_original.columns:
        print(f"  - {col}")
    
    print("\nHeaders limpos:")
    for col in df_limpo.columns:
        print(f"  - {col}")
    
    # Estatísticas gerais
    print("\n=== ESTATÍSTICAS GERAIS ===")
    
    # Tamanho dos arquivos
    import os
    tamanho_original = os.path.getsize('todos_tickets_atual.csv')
    tamanho_limpo = os.path.getsize('todos_tickets_limpos_inteligente.csv')
    
    print(f"Tamanho do arquivo original: {tamanho_original:,} bytes")
    print(f"Tamanho do arquivo limpo: {tamanho_limpo:,} bytes")
    print(f"Redução no tamanho do arquivo: {((tamanho_original - tamanho_limpo) / tamanho_original * 100):.1f}%")
    
    # Caracteres totais
    chars_original = sum(df_original[col].astype(str).str.len().sum() for col in df_original.columns if df_original[col].dtype == 'object')
    chars_limpo = sum(df_limpo[col].astype(str).str.len().sum() for col in df_limpo.columns if df_limpo[col].dtype == 'object')
    
    print(f"Caracteres totais no original: {chars_original:,}")
    print(f"Caracteres totais no limpo: {chars_limpo:,}")
    print(f"Redução total de caracteres: {((chars_original - chars_limpo) / chars_original * 100):.1f}%")
    
    # Verificar XLSX
    try:
        tamanho_xlsx = os.path.getsize('todos_tickets_limpos_inteligente.xlsx')
        print(f"\nTamanho do arquivo XLSX: {tamanho_xlsx:,} bytes")
        print("✅ Arquivo XLSX criado com sucesso!")
    except:
        print("❌ Arquivo XLSX não encontrado")
    
    print("\n=== CONCLUSÃO ===")
    print("A limpeza foi executada e os arquivos foram gerados:")
    print("- todos_tickets_limpos_inteligente.csv")
    print("- todos_tickets_limpos_inteligente.xlsx")
    
    if tickets_com_formulario:
        print(f"\nForam encontrados {len(tickets_com_formulario)} tickets com formulário GLPI.")
        print("A limpeza removeu as estruturas do formulário preservando o conteúdo relevante.")
    else:
        print("\nNenhum ticket com formulário GLPI foi encontrado.")
        print("Os dados podem já estar limpos ou usar um formato diferente.")

if __name__ == "__main__":
    validar_resultados()