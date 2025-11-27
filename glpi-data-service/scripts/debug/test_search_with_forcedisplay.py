import sys
import json
from src.config import config
from src.glpi_client.client import GLPIClient

def test_search():
    print("Testando busca com forcedisplay...")
    
    base_url = config.get_base_url('sis')
    app_token = config.get_app_token('sis')
    user_token = config.get_user_token('sis')
    
    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)
    
    try:
        results = {}
        try:
            data = client.make_request(
                "search/User",
                params={
                    "criteria[0][field]": 1, 
                    "criteria[0][searchtype]": "contains",
                    "criteria[0][value]": "jonathan-moletta",
                    "range": "0-50",
                    "forcedisplay[0]": 2 # Force ID
                }
            )
            results['with_forcedisplay'] = data
        except Exception as e:
            results['error'] = str(e)
            
        with open('search_forcedisplay_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Resultados salvos em search_forcedisplay_results.json")

    finally:
        client.close_session()

if __name__ == "__main__":
    test_search()
