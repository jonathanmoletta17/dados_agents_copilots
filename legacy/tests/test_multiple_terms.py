#!/usr/bin/env python3
"""
Teste de Busca com Múltiplos Termos - Lógica AND
Validar se a busca com múltiplos termos funciona corretamente
"""

import requests
import json
import datetime
from typing import Dict, List, Any

# Configurações
BASE_URL = "http://localhost:8000"
SIS_SEARCH_URL = f"{BASE_URL}/api/v1/sis/search"

def test_multiple_terms():
    """Testar busca com múltiplos termos"""
    print("🔍 TESTE DE MÚLTIPLOS TERMOS - Lógica AND")
    print("=" * 60)
    print(f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Testes com combinações de termos
    test_cases = [
        {
            "name": "Termos relacionados",
            "terms": ["TESTE", "SISTEMA"],
            "expected_logic": "AND"
        },
        {
            "name": "Termo + Categoria",
            "terms": ["ERRO", "IMPRESSORA"],
            "expected_logic": "AND"
        },
        {
            "name": "Termos diversos",
            "terms": ["ACESSO", "USUÁRIO"],
            "expected_logic": "AND"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print("-" * 40)
        
        terms = test_case['terms']
        
        # Buscar cada termo individualmente
        individual_results = {}
        for term in terms:
            response = requests.get(SIS_SEARCH_URL, params={"q": term, "size": 100})
            if response.status_code == 200:
                data = response.json()
                individual_results[term] = {
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
            else:
                individual_results[term] = {"total": 0, "items": []}
        
        # Buscar com múltiplos termos (juntos)
        combined_query = " ".join(terms)
        response = requests.get(SIS_SEARCH_URL, params={"q": combined_query, "size": 100})
        
        if response.status_code == 200:
            combined_data = response.json()
            combined_total = combined_data.get("total", 0)
            combined_items = combined_data.get("items", [])
            
            print(f"Termos individuais:")
            for term in terms:
                total = individual_results[term]["total"]
                print(f"  '{term}': {total} tickets")
            
            print(f"\nCombinação '{combined_query}': {combined_total} tickets")
            
            # Análise da lógica
            print(f"\n📊 ANÁLISE:")
            
            # Verificar se os resultados combinados são uma subconjunto dos individuais
            min_individual = min(individual_results[term]["total"] for term in terms)
            
            if combined_total <= min_individual:
                print(f"✅ Lógica AND confirmada: {combined_total} ≤ {min_individual}")
                
                # Verificar se os tickets combinados realmente contêm todos os termos
                if combined_items:
                    sample_items = combined_items[:3]  # Analisar primeiros 3
                    print(f"\n📝 Amostra de tickets encontrados:")
                    
                    for i, item in enumerate(sample_items, 1):
                        titulo = item.get("titulo", "")
                        categoria = item.get("categoria", "")
                        entidade = item.get("entidade", "")
                        
                        # Verificar quais termos aparecem
                        found_terms = []
                        for term in terms:
                            term_lower = term.lower()
                            if (term_lower in titulo.lower() or 
                                term_lower in categoria.lower() or 
                                term_lower in entidade.lower()):
                                found_terms.append(term)
                        
                        print(f"  Ticket {i}: '{titulo[:50]}...'")
                        print(f"    Termos encontrados: {', '.join(found_terms)}")
                        
                        # Verificar se todos os termos foram encontrados
                        all_terms_found = len(found_terms) == len(terms)
                        print(f"    Todos termos encontrados: {'✅' if all_terms_found else '❌'}")
                        
            else:
                print(f"❌ Resultado inesperado: {combined_total} > {min_individual}")
                print("A busca pode estar usando lógica OR ou outro algoritmo")
            
            print(f"\n" + "="*40)
        
        else:
            print(f"❌ Erro na busca combinada: HTTP {response.status_code}")
    
    # Teste adicional: verificar se a ordem dos termos importa
    print(f"\n🔀 TESTE DE ORDEM DOS TERMOS")
    print("-" * 40)
    
    term1 = "TESTE SISTEMA"
    term2 = "SISTEMA TESTE"
    
    response1 = requests.get(SIS_SEARCH_URL, params={"q": term1, "size": 10})
    response2 = requests.get(SIS_SEARCH_URL, params={"q": term2, "size": 10})
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        total1 = data1.get("total", 0)
        total2 = data2.get("total", 0)
        
        print(f"'{term1}': {total1} tickets")
        print(f"'{term2}': {total2} tickets")
        print(f"Resultados idênticos: {'✅' if total1 == total2 else '❌'}")
        
        if total1 == total2 and total1 > 0:
            print("✅ A ordem dos termos não afeta os resultados (comportamento esperado)")
        else:
            print("ℹ️  A ordem dos termos pode afetar os resultados")
    
    print(f"\n✅ Teste de múltiplos termos concluído!")

if __name__ == "__main__":
    test_multiple_terms()