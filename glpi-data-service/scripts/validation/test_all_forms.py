import requests
import json
import time
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000/api/v1/glpi/sis/tickets"
HEADERS = {"Content-Type": "application/json"}

# Dados de Teste Padrão
TEST_DATA = {
    "username": "jonathan-moletta",
    "atendimentoPara": "Para mim",
    "nomePessoa": None,
    "localizacao": "Casa Civil 1005",
    "telefone": "51999887766",
    "urgencia": "3 - Média (Padrão)"
}

# Lista completa de formulários com dados específicos para cada um
FORMULARIOS = [
    {
        "serviceName": "Ar-Condicionado",
        "tipo": "Instalação",
        "assunto": "[TESTE] Instalação de ar-condicionado na sala 105",
        "descricao": "Solicitação de instalação de ar-condicionado split 12000 BTUs na sala 105 do 1º andar."
    },
    {
        "serviceName": "Carregadores",
        "tipo": "Reparo",
        "assunto": "[TESTE] Carregador de veículo elétrico não funciona",
        "descricao": "Carregador do estacionamento G1 não está funcionando. Precisa manutenção urgente."
    },
    {
        "serviceName": "Copa",
        "tipo": "Limpeza",
        "assunto": "[TESTE] Limpeza da copa do 3º andar",
        "descricao": "Solicito limpeza completa da copa do 3º andar incluindo geladeira e microondas."
    },
    {
        "serviceName": "Elétrica",
        "tipo": "Instalação",
        "assunto": "[TESTE] Instalação de tomadas na sala de reunião",
        "descricao": "Necessário instalar 4 tomadas 110V na parede sul da sala de reunião 302."
    },
    {
        "serviceName": "Elevadores",
        "tipo": "Manutenção",
        "assunto": "[TESTE] Elevador 2 fazendo barulho estranho",
        "descricao": "O elevador 2 está fazendo um barulho de rangido ao subir entre o 1º e 2º andar."
    },
    {
        "serviceName": "Hidráulica",
        "tipo": "Vazamento",
        "assunto": "[TESTE] Torneira do banheiro feminino vazando",
        "descricao": "Torneira da pia do banheiro feminino do 2º andar está vazando constantemente."
    },
    {
        "serviceName": "Jardinagem",
        "tipo": "Poda",
        "assunto": "[TESTE] Poda de árvores na área externa",
        "descricao": "Necessário realizar poda das árvores na área externa próxima ao estacionamento."
    },
    {
        "serviceName": "Limpeza",
        "tipo": "Limpeza Geral",
        "assunto": "[TESTE] Limpeza geral da sala 210",
        "descricao": "Solicitação de limpeza geral da sala 210 incluindo carpete e vidraças."
    },
    {
        "serviceName": "Marcenaria",
        "tipo": "Reparo",
        "assunto": "[TESTE] Porta da sala 115 não fecha",
        "descricao": "A porta da sala 115 está empenada e não fecha corretamente. Precisa ajuste."
    },
    {
        "serviceName": "Mensageria",
        "tipo": "Configuração",
        "assunto": "[TESTE] Configuração de email corporativo",
        "descricao": "Necessário configurar conta de email corporativo no Outlook para novo colaborador."
    },
    {
        "serviceName": "Pedreiro",
        "tipo": "Reparo",
        "assunto": "[TESTE] Reparo de rachadura na parede",
        "descricao": "Existe uma rachadura vertical na parede da sala 308 que precisa ser reparada."
    },
    {
        "serviceName": "Pintura",
        "tipo": "Pintura",
        "assunto": "[TESTE] Pintura da sala de espera",
        "descricao": "Solicitação de pintura completa da sala de espera do térreo, cor branca."
    },
    {
        "serviceName": "Projeto",
        "tipo": "Novo Projeto",
        "assunto": "[TESTE] Projeto de reforma do auditório",
        "descricao": "Iniciar planejamento do projeto de reforma completa do auditório principal."
    },
    {
        "serviceName": "Técnico de Redes",
        "tipo": "Instalação",
        "assunto": "[TESTE] Instalação de ponto de rede na sala 405",
        "descricao": "Necessário instalar 2 pontos de rede cat6 na sala 405 próximo às mesas."
    },
    {
        "serviceName": "Vidraçaria",
        "tipo": "Troca de Vidro",
        "assunto": "[TESTE] Troca de vidro quebrado da janela",
        "descricao": "Vidro da janela da sala 201 está quebrado e precisa ser trocado urgentemente."
    }
]

def criar_ticket(formulario_data):
    """Cria um ticket de teste combinando dados padrão com dados específicos"""
    payload = {
        **TEST_DATA,
        **formulario_data,
        "campoExtra": None
    }
    
    try:
        print(f"\n{'='*80}")
        print(f"TESTANDO: {formulario_data['serviceName']}")
        print(f"{'='*80}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        
        resultado = {
            "formulario": formulario_data['serviceName'],
            "status_code": response.status_code,
            "sucesso": response.status_code == 200,
            "timestamp": datetime.now().isoformat()
        }
        
        if response.status_code == 200:
            data = response.json()
            resultado["ticket_id"] = data.get("ticket_id")
            resultado["response"] = data
            print(f"\n✅ SUCESSO! Ticket criado: #{resultado['ticket_id']}")
        else:
            resultado["erro"] = response.text
            print(f"\n❌ FALHA! Status: {response.status_code}")
            print(f"Erro: {response.text}")
            
        return resultado
        
    except Exception as e:
        print(f"\n❌ EXCEÇÃO! {str(e)}")
        return {
            "formulario": formulario_data['serviceName'],
            "status_code": None,
            "sucesso": False,
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("\n" + "="*80)
    print("VALIDAÇÃO DE FORMULÁRIOS - MOBILE APP")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    resultados = []
    tickets_criados = []
    
    for i, formulario in enumerate(FORMULARIOS, 1):
        print(f"\n[{i}/{len(FORMULARIOS)}] Processando: {formulario['serviceName']}...")
        
        resultado = criar_ticket(formulario)
        resultados.append(resultado)
        
        if resultado["sucesso"]:
            tickets_criados.append({
                "nome": formulario['serviceName'],
                "id": resultado.get('ticket_id')
            })
        
        # Delay entre requisições para não sobrecarregar
        if i < len(FORMULARIOS):
            print("\nAguardando 2 segundos antes do próximo...")
            time.sleep(2)
    
    # Resumo Final
    print("\n" + "="*80)
    print("RESUMO FINAL")
    print("="*80)
    
    sucessos = sum(1 for r in resultados if r["sucesso"])
    falhas = len(resultados) - sucessos
    
    print(f"\nTotal de formulários testados: {len(FORMULARIOS)}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📊 Taxa de sucesso: {(sucessos/len(FORMULARIOS)*100):.1f}%")
    
    if tickets_criados:
        print("\n" + "="*80)
        print("TICKETS CRIADOS (Verificar no GLPI)")
        print("="*80)
        for ticket in tickets_criados:
            print(f"  • {ticket['nome']:.<30} Ticket #{ticket['id']}")
    
    # Salvar resultados
    with open('form_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "resumo": {
                "total": len(FORMULARIOS),
                "sucessos": sucessos,
                "falhas": falhas,
                "taxa_sucesso": round(sucessos/len(FORMULARIOS)*100, 1)
            },
            "tickets_criados": tickets_criados,
            "resultados_detalhados": resultados
        }, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Resultados salvos em: form_validation_results.json")
    print("="*80 + "\n")
    
    return resultados

if __name__ == "__main__":
    main()
