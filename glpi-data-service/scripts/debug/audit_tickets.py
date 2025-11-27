import sys
import json
from src.config import config
from src.glpi_client.client import GLPIClient

def audit_tickets():
    print("Iniciando auditoria do ticket 5087 no contexto SIS...")
    
    # Configuração SIS
    base_url = config.get_base_url('sis')
    app_token = config.get_app_token('sis')
    user_token = config.get_user_token('sis')
    
    if not all([base_url, app_token, user_token]):
        print("Erro: Credenciais SIS incompletas.")
        return

    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)
    
    try:
        tickets_to_check = [5090]
        results = {}
        
        for tid in tickets_to_check:
            print(f"Consultando ticket {tid}...")
            try:
                ticket = client.get_ticket_details(tid)
                
                # Buscar atores (requerente)
                users = client.make_request(f"Ticket/{tid}/Ticket_User")
                requesters = [u for u in users if u.get('type') == 1] # Type 1 = Requester
                
                ticket['actors_requesters'] = requesters
                results[tid] = ticket
            except Exception as e:
                print(f"Erro ao buscar ticket {tid}: {e}")
                results[tid] = {"error": str(e)}
        
        print("\n--- RESULTADOS DA AUDITORIA ---\n")
        with open('audit_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Resultados salvos em audit_results.json")
        
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        client.close_session()

if __name__ == "__main__":
    audit_tickets()
