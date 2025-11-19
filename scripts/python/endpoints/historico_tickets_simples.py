"""
HISTÓRICO DE TICKETS GLPI - Versão Simplificada
==============================================

Gera históricos de tickets usando dados locais quando API não está disponível.
Versão de fallback para quando o SDK não está disponível.

Autor: Analista de Dados - Casa Civil
Data: 2025-11-16
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def gerar_historico_fake():
    """Gera dados de histórico fake para testes quando API não está disponível"""
    
    historico_data = [
        {
            'ticket_id': 10800,
            'data_alteracao': '2025-11-16 16:43:13',
            'usuario': 'Admin GLPI',
            'campo_modificado': 'Status',
            'valor_antigo': 'Novo',
            'valor_novo': 'Em Andamento',
            'tipo_alteracao': 'Atualização',
            'itemtype_link': 'Ticket',
            'linked_action': 0
        },
        {
            'ticket_id': 10800,
            'data_alteracao': '2025-11-16 16:45:22',
            'usuario': 'Técnico Silva',
            'campo_modificado': 'Técnico',
            'valor_antigo': '',
            'valor_novo': 'Técnico Silva',
            'tipo_alteracao': 'Atribuição',
            'itemtype_link': 'User',
            'linked_action': 15
        }
    ]
    
    return historico_data

def salvar_historico(historico_data, output_dir):
    """Salva histórico em formato XLSX"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Criar DataFrame
    df = pd.DataFrame(historico_data)
    
    # Gerar nome único
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"historico_ticket_fake_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # Salvar como XLSX
    df.to_excel(filepath, index=False)
    
    print(f"[OK] Histórico fake salvo: {filename}")
    return filepath

def main():
    """Função principal"""
    print("=" * 60)
    print("[HISTÓRICO] GERADOR DE HISTÓRICO SIMPLIFICADO")
    print("=" * 60)
    
    # Diretório de saída
    output_dir = "../dados/historicos"
    
    print("[INFO] Gerando histórico fake (API não disponível)...")
    
    try:
        # Gerar dados fake
        historico = gerar_historico_fake()
        
        # Salvar histórico
        arquivo_salvo = salvar_historico(historico, output_dir)
        
        print(f"[SUCESSO] Histórico gerado com sucesso!")
        print(f"[ARQUIVO] {arquivo_salvo}")
        print(f"[DADOS] {len(historico)} registros")
        
        # Gerar mais arquivos para simular múltiplos tickets
        for i in range(6):
            historico_extra = gerar_historico_fake()
            # Modificar ID do ticket
            for item in historico_extra:
                item['ticket_id'] = 10799 + i
            salvar_historico(historico_extra, output_dir)
        
        print(f"[SUCESSO] Total de 7 arquivos de histórico gerados!")
        
    except Exception as e:
        print(f"[ERRO] Falha ao gerar histórico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()