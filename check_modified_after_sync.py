import requests
from datetime import datetime

# Configurações
GLPI_URL = "http://10.72.30.39/sis/apirest.php"
APP_TOKEN = "mRCtg3CLRX4lBbp0gJ3mUZgJAaG6azWZQGQJVq2f"
USER_TOKEN = "Rs1pLfsSMnqa5LQ5roph0Ne7xSiZafQdfbXeL3CN"

session = requests.Session()
session.headers.update({'App-Token': APP_TOKEN, 'Content-Type': 'application/json'})

# Init
init_resp = session.get(f"{GLPI_URL}/initSession", 
                        headers={'Authorization': f'user_token {USER_TOKEN}'})
if init_resp.status_code != 200:
    print(f"❌ Erro ao iniciar sessão: {init_resp.status_code}")
    exit(1)

session_token = init_resp.json()['session_token']
session.headers.update({'Session-Token': session_token})

print("✅ Sessão iniciada\n")

# Última sincronização: 2025-11-25T11:02:13.400507
last_sync = datetime.fromisoformat("2025-11-25T11:02:13.400507")
print(f"🕒 Última sincronização: {last_sync}\n")

# Buscar tickets modificados após last_sync
params = {
    'range': '0-99',
    'sort': 'date_mod',
    'order': 'DESC'
}

response = session.get(f"{GLPI_URL}/Ticket", params=params)
tickets = response.json()

modified_after_sync = []

for ticket in tickets:
    date_mod_str = ticket.get('date_mod')
    if date_mod_str:
        ticket_mod_date = datetime.strptime(date_mod_str, '%Y-%m-%d %H:%M:%S')
        
        if ticket_mod_date > last_sync:
            modified_after_sync.append({
                'id': ticket['id'],
                'name': ticket['name'],
                'status': ticket['status'],
                'is_deleted': ticket.get('is_deleted', 0),
                'date_mod': ticket_mod_date,
                'diff_seconds': (ticket_mod_date - last_sync).total_seconds()
            })

print(f"📊 Tickets modificados APÓS última sync ({len(modified_after_sync)} encontrados):\n")

for t in modified_after_sync[:20]:  # Primeiros 20
    print(f"  🎫 ID {t['id']}: {t['name'][:50]}")
    print(f"     Status: {t['status']}, Deleted: {t['is_deleted']}")
    print(f"     Modificado: {t['date_mod']}")
    print(f"     Diferença: +{t['diff_seconds']:.1f}s após last_sync\n")

# Encerra
session.get(f"{GLPI_URL}/killSession")
print("✅ Sessão encerrada")
