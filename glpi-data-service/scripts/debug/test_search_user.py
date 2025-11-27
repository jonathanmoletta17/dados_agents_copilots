import sys
import json
from src.config import config
from src.glpi_client.client import GLPIClient

def test_search():
    print("Testando busca de usuário 'jonathan-moletta'...")
    
    base_url = config.get_base_url('sis')
    app_token = config.get_app_token('sis')
    user_token = config.get_user_token('sis')
    
    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)
    
    try:
        results = {}
        # Teste 1: Com Range (Igual ao backend)
        try:
            data = client.make_request(
                "search/User",
                params={
                    "criteria[0][field]": 1, # name
                    "criteria[0][searchtype]": "contains",
                    "criteria[0][value]": "jonathan-moletta",
                    "range": "0-50"
                }
            )
            results['with_range'] = data
        except Exception as e:
            results['with_range_error'] = str(e)

        # Teste 2: Sem Range
        try:
            data = client.make_request(
                "search/User",
                params={
                    "criteria[0][field]": 1, # name
                    "criteria[0][searchtype]": "contains",
                    "criteria[0][value]": "jonathan-moletta"
                }
            )
            results['without_range'] = data
        except Exception as e:
            results['without_range_error'] = str(e)
            
        with open('search_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Resultados salvos em search_test_results.json")

    finally:
        client.close_session()

if __name__ == "__main__":
    test_search()
