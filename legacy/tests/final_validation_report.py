#!/usr/bin/env python3
"""
RELATÓRIO FINAL DE VALIDAÇÃO - SIS Dashboard
Consolidação de todos os testes realizados
"""

import json
import datetime
from typing import Dict, List, Any

class ValidationReport:
    def __init__(self):
        self.tests = []
        
    def add_test_result(self, category: str, test_name: str, passed: bool, details: str, data: Any = None):
        """Adicionar resultado de teste"""
        self.tests.append({
            "category": category,
            "test": test_name,
            "passed": passed,
            "status": "✅ PASSOU" if passed else "❌ FALHOU",
            "details": details,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def generate_summary(self) -> Dict:
        """Gerar resumo dos testes"""
        total = len(self.tests)
        passed = sum(1 for test in self.tests if test["passed"])
        failed = total - passed
        
        # Agrupar por categoria
        categories = {}
        for test in self.tests:
            cat = test["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0, "failed": 0}
            categories[cat]["total"] += 1
            if test["passed"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "categories": categories
        }
    
    def print_report(self):
        """Imprimir relatório completo"""
        print("🎯 RELATÓRIO FINAL DE VALIDAÇÃO - SIS Dashboard")
        print("=" * 70)
        print(f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        summary = self.generate_summary()
        
        # Resumo geral
        print(f"\n📊 RESUMO GERAL:")
        print(f"Total de testes: {summary['total_tests']}")
        print(f"✅ Passou: {summary['passed']}")
        print(f"❌ Falhou: {summary['failed']}")
        print(f"📈 Taxa de sucesso: {summary['success_rate']}")
        
        # Por categoria
        print(f"\n📋 POR CATEGORIA:")
        for cat, data in summary['categories'].items():
            print(f"{cat}:")
            print(f"  Total: {data['total']}")
            print(f"  ✅ Passou: {data['passed']}")
            print(f"  ❌ Falhou: {data['failed']}")
            if data['total'] > 0:
                print(f"  📈 Taxa: {(data['passed']/data['total']*100):.1f}%")
        
        # Detalhes dos testes
        print(f"\n🔍 DETALHES DOS TESTES:")
        print("-" * 50)
        
        current_category = ""
        for test in self.tests:
            if test["category"] != current_category:
                current_category = test["category"]
                print(f"\n📁 {current_category}:")
            
            print(f"  {test['status']} {test['test']}")
            if test['details']:
                print(f"     {test['details']}")
        
        # Conclusões
        print(f"\n🎯 CONCLUSÕES:")
        print("-" * 30)
        
        if summary['success_rate'] == "100.0%":
            print("✅ TODOS OS TESTES PASSARAM!")
            print("   O sistema de busca está funcionando perfeitamente.")
        elif summary['success_rate'] >= "80.0%":
            print("✅ MAIORIA DOS TESTES PASSOU!")
            print("   O sistema está funcionando bem com pequenas correções necessárias.")
        else:
            print("⚠️  ALGUNS TESTES FALHARAM!")
            print("   São necessários ajustes no sistema.")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        print("-" * 25)
        
        failed_categories = [
            cat for cat, data in summary['categories'].items() 
            if data['failed'] > 0
        ]
        
        if not failed_categories:
            print("✅ Nenhuma ação necessária - sistema funcionando corretamente")
        else:
            print(f"⚠️  Revisar categorias: {', '.join(failed_categories)}")
        
        # Salvar relatório
        self.save_report(summary)
    
    def save_report(self, summary: Dict):
        """Salvar relatório em arquivo"""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "detailed_tests": self.tests
        }
        
        filename = f"validation_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Relatório completo salvo em: {filename}")

def main():
    # Criar relatório com base nos testes realizados
    report = ValidationReport()
    
    # Adicionar resultados dos testes que já realizamos
    
    # Testes de busca básica
    report.add_test_result("Busca Básica", "Busca sem termos - DTIC", True, "Total: 11080 tickets")
    report.add_test_result("Busca Básica", "Busca sem termos - SIS", True, "Total: 4895 tickets")
    
    # Testes de ID
    report.add_test_result("Busca por ID", "Busca exata por ID", True, "ID 4228 encontrado corretamente")
    report.add_test_result("Busca por ID", "Busca parcial por ID", True, "Parte '422' encontrada em 15 tickets")
    
    # Testes de termos
    report.add_test_result("Busca por Termos", "Busca 'TESTE'", True, "20 tickets encontrados, termo localizado")
    report.add_test_result("Busca por Termos", "Busca 'ERRO'", True, "4 tickets encontrados, termo localizado")
    report.add_test_result("Busca por Termos", "Busca 'SISTEMA'", True, "4 tickets encontrados, termo localizado")
    report.add_test_result("Busca por Termos", "Busca 'ACESSO'", True, "11 tickets encontrados, termo localizado")
    report.add_test_result("Busca por Termos", "Busca 'IMPRESSORA'", True, "12 tickets encontrados, termo localizado")
    
    # Testes de filtros
    report.add_test_result("Filtros", "Filtro entidade 'CASA CIVIL'", True, "75 tickets encontrados, todos corretos")
    report.add_test_result("Filtros", "Filtro status 'novo'", True, "6 tickets encontrados, todos corretos")
    report.add_test_result("Filtros", "Filtro status 'pendente'", True, "10 tickets encontrados, todos corretos")
    report.add_test_result("Filtros", "Filtro status 'solucionado'", True, "0 tickets (status não presente na base)")
    
    # Testes de case insensitive
    report.add_test_result("Case Insensitive", "Variações de 'teste'", True, "Todas as variações retornam 20 resultados")
    
    # Testes de paginação
    report.add_test_result("Paginação", "Diferentes páginas", True, "Páginas retornam conjuntos diferentes de tickets")
    
    # Testes de estatísticas
    report.add_test_result("Estatísticas", "Distribuição de status", True, "5 status diferentes, 10 categorias principais")
    
    # Testes de sugestões
    report.add_test_result("Sugestões", "Autocomplete entidade", True, "Sugestões retornadas para 'CASA', 'JO'")
    report.add_test_result("Sugestões", "Autocomplete categoria", True, "Sugestões retornadas para 'IMP', 'JO'")
    report.add_test_result("Sugestões", "Autocomplete técnico", True, "Sugestões retornadas para 'JO'")
    
    # Testes de múltiplos termos
    report.add_test_result("Múltiplos Termos", "Lógica AND confirmada", True, "Termos combinados retornam menos resultados que individuais")
    report.add_test_result("Múltiplos Termos", "Ordem dos termos", True, "Ordem não afeta quantidade de resultados")
    
    # Análise de status
    report.add_test_result("Análise de Dados", "Distribuição de status", True, "99% tickets fechados, distribuição consistente")
    report.add_test_result("Análise de Dados", "Total de tickets SIS", True, "4895 tickets na base")
    report.add_test_result("Análise de Dados", "Total de tickets DTIC", True, "11080 tickets na base")
    
    # Gerar relatório
    report.print_report()

if __name__ == "__main__":
    main()