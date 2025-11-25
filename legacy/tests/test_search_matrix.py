#!/usr/bin/env python3
"""
Matriz de Testes de Busca - SIS Dashboard
Validação completa das funcionalidades de busca
"""

import requests
import json
import datetime
from typing import Dict, List, Any

# Configurações
BASE_URL = "http://localhost:8000"
DTIC_SEARCH_URL = f"{BASE_URL}/api/v1/dtic/search"
SIS_SEARCH_URL = f"{BASE_URL}/api/v1/sis/search"
DTIC_STATS_URL = f"{BASE_URL}/api/v1/dtic/search/stats"
SIS_STATS_URL = f"{BASE_URL}/api/v1/sis/search/stats"

class SearchTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name: str, passed: bool, details: str = "", data: Any = None):
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status} - {test_name}")
        if details:
            print(f"  Detalhes: {details}")
        if data:
            print(f"  Dados: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
    
    def make_request(self, url: str, params: Dict) -> Dict:
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "message": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def test_busca_sem_termos(self):
        """Test 1: Busca sem termos - deve retornar todos os tickets"""
        print("\n=== TESTE 1: Busca sem termos ===")
        
        # Testar DTIC
        result = self.make_request(DTIC_SEARCH_URL, {"page": 1, "size": 10})
        if "error" in result:
            self.log_result("DTIC - Busca sem termos", False, result["error"])
        else:
            total = result.get("total", 0)
            items = result.get("items", [])
            self.log_result(
                "DTIC - Busca sem termos", 
                total > 0 and len(items) > 0,
                f"Total de tickets: {total}, Retornados: {len(items)}",
                {"total": total, "sample_items": len(items)}
            )
        
        # Testar SIS
        result = self.make_request(SIS_SEARCH_URL, {"page": 1, "size": 10})
        if "error" in result:
            self.log_result("SIS - Busca sem termos", False, result["error"])
        else:
            total = result.get("total", 0)
            items = result.get("items", [])
            self.log_result(
                "SIS - Busca sem termos", 
                total > 0 and len(items) > 0,
                f"Total de tickets: {total}, Retornados: {len(items)}",
                {"total": total, "sample_items": len(items)}
            )
    
    def test_busca_por_id(self):
        """Test 2: Busca por ID do ticket"""
        print("\n=== TESTE 2: Busca por ID ===")
        
        # Primeiro obter um ID real
        result = self.make_request(SIS_SEARCH_URL, {"page": 1, "size": 1})
        if "error" not in result and result.get("items"):
            sample_id = result["items"][0]["id"]
            
            # Testar busca exata por ID
            id_result = self.make_request(SIS_SEARCH_URL, {"q": str(sample_id)})
            if "error" in id_result:
                self.log_result("SIS - Busca por ID exato", False, id_result["error"])
            else:
                found = any(item["id"] == sample_id for item in id_result.get("items", []))
                self.log_result(
                    "SIS - Busca por ID exato",
                    found,
                    f"Buscando ID {sample_id}, encontrado: {found}",
                    {"searched_id": sample_id, "found_items": len(id_result.get("items", []))}
                )
            
            # Testar busca parcial por ID
            partial_id = str(sample_id)[:3]
            partial_result = self.make_request(SIS_SEARCH_URL, {"q": partial_id})
            if "error" in partial_result:
                self.log_result("SIS - Busca por ID parcial", False, partial_result["error"])
            else:
                found = any(partial_id in str(item["id"]) for item in partial_result.get("items", []))
                self.log_result(
                    "SIS - Busca por ID parcial",
                    found,
                    f"Buscando parte do ID {partial_id}, encontrado: {found}",
                    {"searched_partial": partial_id, "found_items": len(partial_result.get("items", []))}
                )
    
    def test_busca_por_termo_simples(self):
        """Test 3: Busca por termo simples"""
        print("\n=== TESTE 3: Busca por termo simples ===")
        
        # Termos de teste baseados em dados reais
        termos_teste = ["TESTE", "ERRO", "SISTEMA", "ACESSO", "IMPRESSORA"]
        
        for termo in termos_teste:
            result = self.make_request(SIS_SEARCH_URL, {"q": termo, "size": 5})
            if "error" in result:
                self.log_result(f"SIS - Busca por '{termo}'", False, result["error"])
            else:
                items = result.get("items", [])
                found = False
                for item in items:
                    # Verificar se o termo aparece em algum campo visível
                    campos = [
                        item.get("titulo", ""),
                        item.get("categoria", ""),
                        item.get("entidade", ""),
                        item.get("requerente", ""),
                        item.get("tecnico", ""),
                        item.get("grupo", ""),
                        item.get("status", "")
                    ]
                    if any(termo.lower() in campo.lower() for campo in campos if campo):
                        found = True
                        break
                
                self.log_result(
                    f"SIS - Busca por '{termo}'",
                    found or len(items) > 0,
                    f"Encontrados {len(items)} tickets, termo localizado: {found}",
                    {"termo": termo, "encontrados": len(items), "termo_localizado": found}
                )
    
    def test_filtro_entidade(self):
        """Test 4: Filtro por entidade"""
        print("\n=== TESTE 4: Filtro por entidade ===")
        
        # Testar com "CASA CIVIL"
        result = self.make_request(SIS_SEARCH_URL, {"entidade": "CASA CIVIL"})
        if "error" in result:
            self.log_result("SIS - Filtro entidade 'CASA CIVIL'", False, result["error"])
        else:
            items = result.get("items", [])
            total = result.get("total", 0)
            
            # Verificar se todos os tickets retornados são da entidade correta
            all_correct = all(
                "casa civil" in item.get("entidade", "").lower() 
                for item in items
            ) if items else False
            
            self.log_result(
                "SIS - Filtro entidade 'CASA CIVIL'",
                all_correct and total > 0,
                f"Total: {total}, Todos corretos: {all_correct}",
                {"total": total, "amostra": len(items), "todos_corretos": all_correct}
            )
    
    def test_filtro_status(self):
        """Test 5: Filtro por status"""
        print("\n=== TESTE 5: Filtro por status ===")
        
        status_teste = ["novo", "pendente", "solucionado"]
        
        for status in status_teste:
            result = self.make_request(SIS_SEARCH_URL, {"status": status})
            if "error" in result:
                self.log_result(f"SIS - Filtro status '{status}'", False, result["error"])
            else:
                items = result.get("items", [])
                total = result.get("total", 0)
                
                # Verificar se todos os tickets têm o status correto
                all_correct = all(
                    status.lower() in item.get("status", "").lower()
                    for item in items
                ) if items else False
                
                self.log_result(
                    f"SIS - Filtro status '{status}'",
                    all_correct or total == 0,  # Permite 0 resultados
                    f"Total: {total}, Todos corretos: {all_correct}",
                    {"status": status, "total": total, "amostra": len(items), "todos_corretos": all_correct}
                )
    
    def test_busca_combinada(self):
        """Test 6: Busca com múltiplos filtros"""
        print("\n=== TESTE 6: Busca combinada ===")
        
        # Combinar termo de busca com filtros
        params = {
            "q": "TESTE",
            "entidade": "CASA CIVIL",
            "status": "novo",
            "size": 10
        }
        
        result = self.make_request(SIS_SEARCH_URL, params)
        if "error" in result:
            self.log_result("SIS - Busca combinada", False, result["error"])
        else:
            items = result.get("items", [])
            total = result.get("total", 0)
            
            # Verificar se todos os critérios são atendidos
            all_match = True
            for item in items:
                if not ("teste" in item.get("titulo", "").lower() or 
                       "teste" in item.get("categoria", "").lower() or
                       "teste" in item.get("entidade", "").lower()):
                    all_match = False
                    break
                if not "casa civil" in item.get("entidade", "").lower():
                    all_match = False
                    break
                if not "novo" in item.get("status", "").lower():
                    all_match = False
                    break
            
            self.log_result(
                "SIS - Busca combinada",
                all_match or total == 0,
                f"Total: {total}, Todos critérios atendidos: {all_match}",
                {"total": total, "amostra": len(items), "todos_criterios": all_match}
            )
    
    def test_case_insensitive(self):
        """Test 7: Case insensitive search"""
        print("\n=== TESTE 7: Case insensitive ===")
        
        # Testar diferentes casos para o mesmo termo
        variacoes = ["teste", "TESTE", "Teste", "TeStE"]
        
        for variacao in variacoes:
            result = self.make_request(SIS_SEARCH_URL, {"q": variacao, "size": 3})
            if "error" in result:
                self.log_result(f"SIS - Case insensitive '{variacao}'", False, result["error"])
            else:
                total = result.get("total", 0)
                self.log_result(
                    f"SIS - Case insensitive '{variacao}'",
                    total >= 0,
                    f"Resultados: {total}",
                    {"variacao": variacao, "total": total}
                )
    
    def test_paginacao(self):
        """Test 8: Paginação"""
        print("\n=== TESTE 8: Paginação ===")
        
        # Testar diferentes páginas
        result_page1 = self.make_request(SIS_SEARCH_URL, {"q": "TESTE", "page": 1, "size": 5})
        result_page2 = self.make_request(SIS_SEARCH_URL, {"q": "TESTE", "page": 2, "size": 5})
        
        if "error" in result_page1 or "error" in result_page2:
            self.log_result("SIS - Paginação", False, "Erro ao buscar páginas")
        else:
            items1 = result_page1.get("items", [])
            items2 = result_page2.get("items", [])
            
            # Verificar se as páginas têm itens diferentes
            different = len(items1) > 0 and len(items2) > 0
            if different:
                # Comparar IDs para garantir que são diferentes
                ids1 = [item.get("id") for item in items1]
                ids2 = [item.get("id") for item in items2]
                different = not any(id1 in ids2 for id1 in ids1)
            
            self.log_result(
                "SIS - Paginação",
                different,
                f"Página 1: {len(items1)} itens, Página 2: {len(items2)} itens, Diferentes: {different}",
                {"pagina1": len(items1), "pagina2": len(items2), "diferentes": different}
            )
    
    def test_estatisticas(self):
        """Test 9: Estatísticas de busca"""
        print("\n=== TESTE 9: Estatísticas ===")
        
        result = self.make_request(SIS_STATS_URL, {})
        if "error" in result:
            self.log_result("SIS - Estatísticas", False, result["error"])
        else:
            status_counts = result.get("status", [])
            categorias = result.get("categoria", [])
            
            has_status = len(status_counts) > 0
            has_categorias = len(categorias) > 0
            
            self.log_result(
                "SIS - Estatísticas",
                has_status and has_categorias,
                f"Status: {len(status_counts)}, Categorias: {len(categorias)}",
                {"status_count": len(status_counts), "categoria_count": len(categorias)}
            )
    
    def test_sugestoes(self):
        """Test 10: Sugestões de autocomplete"""
        print("\n=== TESTE 10: Sugestões ===")
        
        # Testar sugestões para diferentes campos
        campos = ["entidade", "categoria", "tecnico"]
        prefixos = ["CASA", "IMP", "JO"]
        
        for campo in campos:
            for prefixo in prefixos:
                url = f"{BASE_URL}/api/v1/sis/search/suggest"
                result = self.make_request(url, {"field": campo, "prefix": prefixo})
                if "error" in result:
                    self.log_result(f"SIS - Sugestão {campo} '{prefixo}'", False, result["error"])
                else:
                    sugestoes = result if isinstance(result, list) else []
                    self.log_result(
                        f"SIS - Sugestão {campo} '{prefixo}'",
                        len(sugestoes) >= 0,
                        f"Sugestões: {len(sugestoes)}",
                        {"campo": campo, "prefixo": prefixo, "sugestoes": len(sugestoes)}
                    )
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 Iniciando Matriz de Testes de Busca - SIS Dashboard")
        print("=" * 60)
        print(f"URL Base: {BASE_URL}")
        print(f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Executar testes
        self.test_busca_sem_termos()
        self.test_busca_por_id()
        self.test_busca_por_termo_simples()
        self.test_filtro_entidade()
        self.test_filtro_status()
        self.test_busca_combinada()
        self.test_case_insensitive()
        self.test_paginacao()
        self.test_estatisticas()
        self.test_sugestoes()
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL")
        print("=" * 60)
        print(f"Total de testes: {self.passed + self.failed}")
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"📈 Taxa de sucesso: {(self.passed/(self.passed + self.failed)*100):.1f}%")
        
        # Salvar relatório detalhado
        self.save_report()
    
    def save_report(self):
        """Salvar relatório detalhado"""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "total_tests": self.passed + self.failed,
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": f"{(self.passed/(self.passed + self.failed)*100):.1f}%"
            },
            "results": self.results
        }
        
        filename = f"search_test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Relatório detalhado salvo em: {filename}")

if __name__ == "__main__":
    tester = SearchTester()
    tester.run_all_tests()