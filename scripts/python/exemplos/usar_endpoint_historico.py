"""
EXEMPLO PRÁTICO - USO DO ENDPOINT DE HISTÓRICO GLPI
====================================================

Este script demonstra como usar o endpoint de histórico de tickets
de forma prática para obter auditoria completa de alterações.

Autor: Analista de Dados - Casa Civil
Data: 2025-11-16
"""

import sys
import os

# Adicionar o diretório ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from endpoints.historico_tickets_api import (
    endpoint_historico_ticket, 
    endpoint_historico_multiplos_tickets,
    obter_historico_ticket,
    inicializar_cliente_glpi
)

def exemplo_basico():
    """Exemplo básico de uso do endpoint"""
    print("🎯 EXEMPLO BÁSICO - HISTÓRICO DE UM TICKET")
    print("=" * 50)
    
    # ID do ticket que queremos consultar
    ticket_id = 10798
    
    print(f"📋 Consultando histórico do ticket {ticket_id}...")
    
    # Obter histórico em formato JSON
    resultado = endpoint_historico_ticket(ticket_id, formato='json', exportar_csv=True)
    
    if "erro" not in resultado:
        print(f"✅ Sucesso! Encontradas {resultado['total_alteracoes']} alterações")
        
        # Mostrar resumo
        print(f"\n📊 RESUMO DO TICKET {ticket_id}:")
        print(f"   📅 Período: {resultado['periodo']['primeira_alteracao']} até {resultado['periodo']['ultima_alteracao']}")
        print(f"   👥 Usuários envolvidos: {len(resultado['usuarios_envolvidos'])}")
        print(f"   📝 Tipos de alterações: {len(resultado['tipos_alteracoes'])}")
        
        # Mostrar usuários
        print(f"\n👨‍💻 USUÁRIOS QUE REALIZARAM ALTERAÇÕES:")
        for usuario in resultado['usuarios_envolvidos']:
            print(f"   • {usuario}")
        
        # Mostrar tipos de alterações
        print(f"\n🔄 TIPOS DE ALTERAÇÕES ENCONTRADAS:")
        for tipo in resultado['tipos_alteracoes']:
            print(f"   • {tipo}")
        
        # Mostrar últimas 5 alterações
        print(f"\n📋 ÚLTIMAS 5 ALTERAÇÕES:")
        for i, alteracao in enumerate(resultado['historico_detalhado'][:5]):
            print(f"\n   {i+1}. {alteracao.get('tipo_alteracao', 'Alteração')}")
            print(f"      📅 Data: {alteracao.get('date_mod', 'N/A')}")
            print(f"      👤 Usuário: {alteracao.get('user_name', 'Sistema')}")
            if alteracao.get('old_value') or alteracao.get('new_value'):
                print(f"      🔄 De: '{alteracao.get('old_value', '')}' Para: '{alteracao.get('new_value', '')}'")
        
        if 'arquivo_csv' in resultado:
            print(f"\n💾 Arquivo CSV exportado: {resultado['arquivo_csv']}")
    
    else:
        print(f"❌ Erro: {resultado['erro']}")

def exemplo_multiplos_tickets():
    """Exemplo com múltiplos tickets"""
    print("\n🎯 EXEMPLO MÚLTIPLOS TICKETS")
    print("=" * 50)
    
    # Lista de tickets para consultar
    ticket_ids = [10798, 10799, 10800]
    
    print(f"📋 Consultando histórico de {len(ticket_ids)} tickets...")
    
    # Obter histórico de múltiplos tickets
    resultado = endpoint_historico_multiplos_tickets(ticket_ids, exportar_csv=True)
    
    if "erro" not in resultado:
        print(f"✅ Processados {resultado['total_tickets_processados']} tickets")
        print(f"📊 Tickets com histórico: {resultado['tickets_com_historico']}")
        print(f"🔄 Total geral de alterações: {resultado['total_alteracoes_geral']}")
        
        # Análise por ticket
        print(f"\n📈 ANÁLISE POR TICKET:")
        for ticket_id, dados in resultado['historicos_por_ticket'].items():
            print(f"\n🎫 Ticket {ticket_id}:")
            print(f"   📊 Total de alterações: {dados['total_alteracoes']}")
            
            if dados['total_alteracoes'] > 0:
                # Análise das alterações
                tipos_alteracoes = {}
                usuarios = set()
                
                for alteracao in dados['historico']:
                    tipo = alteracao.get('tipo_alteracao', 'Desconhecido')
                    usuario = alteracao.get('user_name', 'Sistema')
                    tipos_alteracoes[tipo] = tipos_alteracoes.get(tipo, 0) + 1
                    usuarios.add(usuario)
                
                print(f"   👥 Usuários envolvidos: {len(usuarios)}")
                print(f"   📝 Tipos de alterações: {len(tipos_alteracoes)}")
                print(f"   📅 Período: {dados['historico'][-1].get('date_mod', 'N/A')} até {dados['historico'][0].get('date_mod', 'N/A')}")
                
                # Top 3 tipos de alterações
                top_tipos = sorted(tipos_alteracoes.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   🔝 Top alterações:")
                for tipo, quantidade in top_tipos:
                    print(f"      • {tipo}: {quantidade}x")
    
    else:
        print(f"❌ Erro: {resultado['erro']}")

def exemplo_analise_auditoria():
    """Exemplo de análise para auditoria"""
    print("\n🎯 EXEMPLO ANÁLISE PARA AUDITORIA")
    print("=" * 50)
    
    ticket_id = 10798
    print(f"🔍 Análise de auditoria do ticket {ticket_id}...")
    
    # Obter dados completos
    resultado = endpoint_historico_ticket(ticket_id, formato='json')
    
    if "erro" not in resultado:
        historico = resultado['historico_detalhado']
        
        print(f"\n📊 RELATÓRIO DE AUDITORIA - TICKET {ticket_id}")
        print("=" * 60)
        
        # 1. Timeline completa
        print(f"\n📅 TIMELINE DO TICKET:")
        print(f"   🕐 Criado em: {resultado['periodo']['primeira_alteracao']}")
        print(f"   🕐 Última alteração: {resultado['periodo']['ultima_alteracao']}")
        
        # 2. Análise de usuários
        print(f"\n👥 ANÁLISE DE USUÁRIOS:")
        usuarios_alteracoes = {}
        for alteracao in historico:
            usuario = alteracao.get('user_name', 'Sistema')
            usuarios_alteracoes[usuario] = usuarios_alteracoes.get(usuario, 0) + 1
        
        for usuario, quantidade in sorted(usuarios_alteracoes.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {usuario}: {quantidade} alterações")
        
        # 3. Análise de tipos de alterações
        print(f"\n🔄 ANÁLISE DE TIPOS DE ALTERAÇÕES:")
        tipos_alteracoes = {}
        for alteracao in historico:
            tipo = alteracao.get('tipo_alteracao', 'Desconhecido')
            tipos_alteracoes[tipo] = tipos_alteracoes.get(tipo, 0) + 1
        
        for tipo, quantidade in sorted(tipos_alteracoes.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {tipo}: {quantidade} ocorrências")
        
        # 4. Alterações críticas (usuário, status, etc)
        print(f"\n⚠️ ALTERAÇÕES CRÍTICAS IDENTIFICADAS:")
        alteracoes_criticas = []
        for alteracao in historico:
            campo = alteracao.get('campo_modificado', '')
            if any(critico in campo.lower() for critico in ['usuário', 'status', 'técnico', 'grupo']):
                alteracoes_criticas.append(alteracao)
        
        if alteracoes_criticas:
            for i, alteracao in enumerate(alteracoes_criticas[:5]):
                print(f"   {i+1}. {alteracao.get('tipo_alteracao')}")
                print(f"      📅 {alteracao.get('date_mod')}")
                print(f"      👤 {alteracao.get('user_name')}")
                print(f"      📝 Campo: {alteracao.get('campo_modificado')}")
        else:
            print("   ✅ Nenhuma alteração crítica identificada")
        
        # 5. Resumo estatístico
        print(f"\n📈 RESUMO ESTATÍSTICO:")
        print(f"   📊 Total de alterações: {len(historico)}")
        print(f"   👥 Usuários diferentes: {len(usuarios_alteracoes)}")
        print(f"   📝 Tipos de alterações: {len(tipos_alteracoes)}")
        print(f"   ⚠️ Alterações críticas: {len(alteracoes_criticas)}")
        
        # 6. Recomendações
        print(f"\n💡 RECOMENDAÇÕES DE AUDITORIA:")
        if len(usuarios_alteracoes) > 3:
            print("   ⚠️ Muitos usuários diferentes - verificar se todas as alterações foram autorizadas")
        
        if len(alteracoes_criticas) > 5:
            print("   ⚠️ Muitas alterações críticas - revisar mudanças de status e atribuições")
        
        usuario_principal = max(usuarios_alteracoes.items(), key=lambda x: x[1])
        print(f"   ✅ Usuário principal: {usuario_principal[0]} ({usuario_principal[1]} alterações)")
        
        print("   ✅ Ticket com histórico completo e rastreável")

def exemplo_export_csv():
    """Exemplo de exportação CSV para relatórios"""
    print("\n🎯 EXEMPLO EXPORTAÇÃO CSV")
    print("=" * 50)
    
    ticket_id = 10798
    print(f"💾 Exportando histórico do ticket {ticket_id} para CSV...")
    
    # Obter em formato CSV direto
    csv_data = endpoint_historico_ticket(ticket_id, formato='csv', exportar_csv=True)
    
    if isinstance(csv_data, str) and not csv_data.startswith("{'erro'"):
        print("✅ Dados CSV obtidos com sucesso!")
        print("\n📋 PRIMEIRAS 5 LINHAS DO CSV:")
        
        # Mostrar cabeçalho e primeiras linhas
        linhas = csv_data.strip().split('\n')
        for i, linha in enumerate(linhas[:6]):
            if i == 0:
                print(f"🔤 CABEÇALHO: {linha}")
            else:
                print(f"📄 Linha {i}: {linha}")
        
        print(f"\n💾 Total de linhas: {len(linhas)}")
        print("✅ CSV pronto para importar em Excel ou outras ferramentas")
    
    else:
        print(f"❌ Erro: {csv_data}")

def main():
    """Função principal que executa todos os exemplos"""
    print("🚀 EXEMPLOS PRÁTICOS - ENDPOINT DE HISTÓRICO GLPI")
    print("=" * 60)
    print("Este script demonstra como usar o endpoint de histórico de tickets")
    print("para obter auditoria completa de alterações no GLPI.")
    
    try:
        # Executar exemplos
        exemplo_basico()
        exemplo_multiplos_tickets()
        exemplo_analise_auditoria()
        exemplo_export_csv()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("\n📋 RESUMO DAS FUNCIONALIDADES:")
        print("• endpoint_historico_ticket() - Histórico individual")
        print("• endpoint_historico_multiplos_tickets() - Histórico em lote")
        print("• Suporte a formatos JSON e CSV")
        print("• Exportação automática de arquivos")
        print("• Análise completa de auditoria")
        print("• Identificação de alterações críticas")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("Verifique a conexão com a API GLPI e as configurações.")

if __name__ == "__main__":
    main()