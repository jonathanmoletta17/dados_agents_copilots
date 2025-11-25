import requests
import json

# Configurações do GLPI SIS
GLPI_URL = "http://10.72.30.39/sis/apirest.php"
APP_TOKEN = "mRCtg3CLRX4lBbp0gJ3mUZgJAaG6azWZQGQJVq2f"
USER_TOKEN = "Rs1pLfsSMnqa5LQ5roph0Ne7xSiZafQdfbXeL3CN"

# IDs dos tickets para verificar
ticket_ids = [5050, 5051, 5052, 5056, 5064]

# Inicia sessão
session = requests.Session()
session.headers.update({
    'App-Token': APP_TOKEN,
    'Content-Type': 'application/json'
})

# Init session
init_response = session.get(
    f"{GLPI_URL}/initSession",
    headers={'Authorization': f'user_token {USER_TOKEN}'}
)

if init_response.status_code == 200:
    session_token = init_response.json()['session_token']
    session.headers.update({'Session-Token': session_token})
    
    print("✅ Sessão iniciada com sucesso!\n")
    
    # Verifica cada ticket
    for ticket_id in ticket_ids:
        try:
            response = session.get(f"{GLPI_URL}/Ticket/{ticket_id}")
            
            if response.status_code == 200:
                ticket = response.json()
                print(f"🎫 Ticket {ticket_id}:")
                print(f"   Status ID: {ticket.get('status')}")
                print(f"   Nome: {ticket.get('name', 'N/A')}")
                print(f"   Criado em: {ticket.get('date', 'N/A')}")
                print(f"   Modificado em: {ticket.get('date_mod', 'N/A')}")
                print(f"   Fechado em: {ticket.get('closedate', 'N/A')}")
                print(f"   Solucionado em: {ticket.get('solvedate', 'N/A')}")
                print(f"   Deletado (is_deleted): {ticket.get('is_deleted', 'N/A')}")
                print()
            elif response.status_code == 404:
                print(f"❌ Ticket {ticket_id}: NÃO ENCONTRADO (deletado?)\n")
            else:
                print(f"⚠️  Ticket {ticket_id}: Erro {response.status_code}\n")
                
        except Exception as e:
            print(f"❌ Erro ao consultar ticket {ticket_id}: {e}\n")
    
    # Encerra sessão
    session.get(f"{GLPI_URL}/killSession")
    print("✅ Sessão encerrada")
else:
    print(f"❌ Erro ao iniciar sessão: {init_response.status_code}")
    print(init_response.text)
