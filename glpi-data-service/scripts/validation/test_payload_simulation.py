import requests
import json

# Configuração
API_URL = "http://localhost:8000/api/v1/glpi/sis/tickets"
HEADERS = {"Content-Type": "application/json"}

# Payload Simulado (como o App enviaria agora)
payload = {
    "serviceName": "Ar-Condicionado",
    "atendimentoPara": "Para mim",
    "nomePessoa": None,
    "localizacao": "Local (Root 70): Casa Civil 1005", # Testando limpeza + resolução válida (ID 1)
    "telefone": "51999999999",
    "urgencia": "3 - Média (Padrão)",
    "tipo": "Instalação",
    "assunto": "Teste de Correção de Campos - Dados Reais",
    "descricao": "Teste de validação com usuário e localização existentes.",
    "campoExtra": "Nenhum",
    "username": "jonathan-moletta" # Usuário real (ID 2039)
}

def test_create_ticket():
    print(f"Enviando payload para {API_URL}...")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n[SUCESSO] Ticket criado com sucesso!")
                print(f"Ticket ID: {data.get('ticket_id')}")
            else:
                print("\n[FALHA] Backend retornou sucesso=False")
        else:
            print("\n[ERRO] Falha na requisição")
            
    except Exception as e:
        print(f"\n[EXCEPTION] Erro ao conectar: {e}")

if __name__ == "__main__":
    test_create_ticket()
