import requests
import json
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000/api/v1/glpi/sis/tickets"
HEADERS = {"Content-Type": "application/json"}

# Lista de todos os serviços/formulários disponíveis
SERVICES = [
    "Ar-Condicionado",
    "Carregadores",
    "Copa",
    "Elétrica",
    "Elevadores",
    "Hidráulica",
    "Jardinagem",
    "Limpeza",
    "Marcenaria",
    "Mensageria",
    "Pedreiro",
    "Pintura",
    "Projeto",
    "Técnico de Redes",
    "Vidraçaria"
]

# Categorias/Tipos comuns para teste
COMMON_TYPES = {
    "Ar-Condicionado": "Instalação",
    "Carregadores": "Reparo",
    "Copa": "Limpeza",
    "Elétrica": "Instalação",
    "Elevadores": "Manutenção",
    "Hidráulica": "Vazamento",
    "Jardinagem": "Poda",
    "Limpeza": "Limpeza Geral",
    "Marcenaria": "Reparo",
    "Mensageria": "Configuração",
    "Pedreiro": "Reparo",
    "Pintura": "Pintura",
    "Projeto": "Novo Projeto",
    "Técnico de Redes": "Instalação",
    "Vidraçaria": "Troca de Vidro"
}

def create_test_ticket(service_name):
    """Cria um ticket de teste para o serviço especificado"""
    
    payload = {
        "serviceName": service_name,
        "atendimentoPara": "Para mim",
        "nomePessoa": None,
        "localizacao": "Casa Civil 1005",  # Usando localização válida identificada
        "telefone": "51999887766",
        "urgencia": "3 - Média (Padrão)",
        "tipo": COMMON_TYPES.get(service_name, "Diversos"),
        "assunto": f"[TESTE VALIDAÇÃO] {service_name}",
        "descricao": f"Ticket de teste para validação do formulário de {service_name}. Criado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "campoExtra": None,
        "username": "jonathan-moletta"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        
        result = {
            "service": service_name,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "payload": payload
        }
        
        if response.status_code == 200:
            data = response.json()
            result["ticket_id"] = data.get("ticket_id")
            result["response"] = data
        else:
            result["error"] = response.text
            
        return result
        
    except Exception as e:
        return {
            "service": service_name,
            "status_code": None,
            "success": False,
            "error": str(e),
            "payload": payload
        }

def validate_all_forms():
    """Valida todos os formulários disponíveis"""
    print("="*80)
    print(f"VALIDAÇÃO DE FORMULÁRIOS DO MOBILE APP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"\nServiços para validar: {len(SERVICES)}")
    print("\nIniciando testes...\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, service in enumerate(SERVICES, 1):
        print(f"[{i}/{len(SERVICES)}] Testando formulário: {service}...")
        
        result = create_test_ticket(service)
        results.append(result)
        
        if result["success"]:
            print(f"  ✓ SUCESSO - Ticket ID: {result.get('ticket_id', 'N/A')}")
            success_count += 1
        else:
            print(f"  ✗ FALHA - Status: {result['status_code']}, Erro: {result.get('error', 'N/A')}")
            failed_count += 1
        
        print()
    
    # Resumo
    print("="*80)
    print("RESULTADOS DA VALIDAÇÃO")
    print("="*80)
    print(f"Total de formulários testados: {len(SERVICES)}")
    print(f"✓ Sucessos: {success_count}")
    print(f"✗ Falhas: {failed_count}")
    print(f"Taxa de sucesso: {(success_count/len(SERVICES)*100):.1f}%")
    
    # Salvar resultados detalhados
    with open('validation_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_services": len(SERVICES),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print("\nResultados detalhados salvos em: validation_results.json")
    
    # Lista de tickets criados para auditoria
    if success_count > 0:
        print("\n" + "="*80)
        print("TICKETS CRIADOS (para auditoria manual no GLPI)")
        print("="*80)
        for result in results:
            if result["success"]:
                print(f"  - {result['service']}: Ticket #{result.get('ticket_id', 'N/A')}")
    
    return results

if __name__ == "__main__":
    validate_all_forms()
