import pandas as pd
from src.api_extract import get_tasks, get_problems, get_changes
from src.db_extract import get_connection, load_dtic_tickets
import os

def validate():
    print("=== INICIANDO VALIDAÇÃO DE DADOS ===")
    
    # 1. Validate Tickets Count (DB vs API is hard because API fetch is heavy, 
    # but we can compare DB vs CSV generated if we trust the CSV generation logic)
    # Actually, let's compare DB vs CSV output for Tickets.
    
    print("\n--- 1. Validação de Tickets (DB Local vs CSV Gerado) ---")
    try:
        df_db = load_dtic_tickets()
        count_db = len(df_db)
        print(f"Tickets no Banco (dtic.tickets): {count_db}")
        
        csv_path = os.path.join("output", "dtic_tickets_detalhe.csv")
        if os.path.exists(csv_path):
            df_csv = pd.read_csv(csv_path, sep=';')
            count_csv = len(df_csv)
            print(f"Tickets no CSV (dtic_tickets_detalhe.csv): {count_csv}")
            
            if count_db == count_csv:
                print("✅ MATCH: Contagem de tickets coincide.")
            else:
                print(f"❌ MISMATCH: Diferença de {abs(count_db - count_csv)} tickets.")
        else:
            print("⚠️ CSV de tickets não encontrado para comparação.")
    except Exception as e:
        print(f"Erro na validação de tickets: {e}")

    # 2. Validate Tasks (API vs DB)
    # We will fetch from API (sample or count) and check if DB table has data.
    print("\n--- 2. Validação de Tarefas (API vs DB) ---")
    try:
        # Check DB
        engine = get_connection()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM dtic.tickettasks"))
            count_db_tasks = result.scalar()
        print(f"Tarefas no Banco (dtic.tickettasks): {count_db_tasks}")
        
        # We won't fetch all from API here to save time, but we can check if it's > 0
        if count_db_tasks > 0:
             print("✅ Dados de tarefas presentes no banco.")
        else:
             print("⚠️ Tabela de tarefas vazia no banco.")

    except Exception as e:
        print(f"Erro na validação de tarefas: {e}")
        # Table might not exist yet
        print("ℹ️ Tabela dtic.tickettasks pode não existir ainda.")

    # 3. Validate Problems (API vs DB)
    print("\n--- 3. Validação de Problemas (API vs DB) ---")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM dtic.problems"))
            count_db_probs = result.scalar()
        print(f"Problemas no Banco (dtic.problems): {count_db_probs}")
    except Exception as e:
         print(f"Erro/Tabela inexistente: {e}")

    # 4. Validate Changes (API vs DB)
    print("\n--- 4. Validação de Mudanças (API vs DB) ---")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM dtic.changes"))
            count_db_changes = result.scalar()
        print(f"Mudanças no Banco (dtic.changes): {count_db_changes}")
    except Exception as e:
         print(f"Erro/Tabela inexistente: {e}")

    print("\n=== VALIDAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    from sqlalchemy import text
    validate()
