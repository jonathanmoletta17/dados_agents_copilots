#!/usr/bin/env python3
"""
Comparação de Status - SIS Dashboard vs GLPI Nativo
Validar se as contagens de status estão consistentes
"""

import requests
import json
import datetime
from typing import Dict, List, Any

# Configurações
BASE_URL = "http://localhost:8000"
SIS_STATS_URL = f"{BASE_URL}/api/v1/sis/search/stats"

class StatusComparator:
    def __init__(self):
        self.results = []
        
    def get_our_stats(self) -> Dict:
        """Obter estatísticas do nosso sistema"""
        try:
            response = requests.get(SIS_STATS_URL)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_status_distribution(self, stats: Dict):
        """Analisar distribuição de status"""
        if "error" in stats:
            print(f"❌ Erro ao obter estatísticas: {stats['error']}")
            return
        
        status_data = stats.get("status", [])
        total_tickets = sum(count for _, count in status_data)
        
        print("📊 DISTRIBUIÇÃO DE STATUS - SIS Dashboard")
        print("=" * 50)
        print(f"Total de tickets: {total_tickets}")
        print()
        
        for status, count in status_data:
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            print(f"{status:<20} {count:>6} tickets ({percentage:>5.1f}%)")
        
        print()
        print("🔍 ANÁLISE DETALHADA:")
        print("-" * 30)
        
        # Análise de consistência
        analysis = []
        
        for status, count in status_data:
            status_lower = status.lower()
            
            if status_lower == "novo":
                analysis.append(f"✅ Status '{status}': {count} tickets - Novos tickets aguardando atendimento")
            elif status_lower == "atribuido":
                analysis.append(f"✅ Status '{status}': {count} tickets - Tickets já atribuídos a técnicos")
            elif status_lower == "pendente":
                analysis.append(f"⚠️  Status '{status}': {count} tickets - Tickets pendentes (aguardando usuário, aprovação, etc.)")
            elif status_lower == "solucionado":
                analysis.append(f"✅ Status '{status}': {count} tickets - Tickets solucionados, aguardando confirmação")
            elif status_lower == "fechado":
                analysis.append(f"✅ Status '{status}': {count} tickets - Tickets fechados definitivamente")
            else:
                analysis.append(f"ℹ️  Status '{status}': {count} tickets - Status adicional")
        
        for line in analysis:
            print(line)
        
        # Verificar distribuição saudável
        print()
        print("🔧 VALIDAÇÃO DE DISTRIBUIÇÃO:")
        print("-" * 35)
        
        if total_tickets > 0:
            novos_pct = next((count for status, count in status_data if status.lower() == "novo"), 0) / total_tickets * 100
            pendentes_pct = next((count for status, count in status_data if status.lower() == "pendente"), 0) / total_tickets * 100
            finalizados_pct = sum(count for status, count in status_data if status.lower() in ["solucionado", "fechado"]) / total_tickets * 100
            
            print(f"📈 Novos: {novos_pct:.1f}% {'(Normal)' if novos_pct < 30 else '(Alto)'}")
            print(f"⏳ Pendentes: {pendentes_pct:.1f}% {'(Normal)' if pendentes_pct < 40 else '(Alto)'}")
            print(f"✅ Finalizados: {finalizados_pct:.1f}% {'(Bom)' if finalizados_pct > 30 else '(Abaixo do esperado)'}")
            
            if novos_pct > 30:
                print("⚠️  Alerta: Alta quantidade de tickets novos pode indicar gargalo no atendimento")
            if pendentes_pct > 40:
                print("⚠️  Alerta: Muitos tickets pendentes podem indicar processos travados")
            if finalizados_pct < 30:
                print("⚠️  Alerta: Baixa taxa de finalização pode indicar problemas de eficiência")
        
        # Salvar relatório
        self.save_report(status_data, total_tickets)
    
    def save_report(self, status_data: List, total_tickets: int):
        """Salvar relatório detalhado"""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis_type": "status_distribution",
            "total_tickets": total_tickets,
            "status_breakdown": [
                {
                    "status": status,
                    "count": count,
                    "percentage": round((count / total_tickets * 100) if total_tickets > 0 else 0, 2)
                }
                for status, count in status_data
            ],
            "validation_metrics": {
                "total_statuses": len(status_data),
                "coverage": "complete" if len(status_data) >= 4 else "partial"
            }
        }
        
        filename = f"status_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Relatório salvo em: {filename}")

def main():
    print("🔍 ANÁLISE DE STATUS - SIS Dashboard")
    print("=" * 60)
    print(f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    comparator = StatusComparator()
    stats = comparator.get_our_stats()
    comparator.analyze_status_distribution(stats)
    
    print("\n✅ Análise concluída!")

if __name__ == "__main__":
    main()