import sys
import json
from src.config import config
from src.glpi_client.client import GLPIClient

def inspect_data():
    print("Inspecionando dados no GLPI (SIS)...")
    
    base_url = config.get_base_url('sis')
    app_token = config.get_app_token('sis')
    user_token = config.get_user_token('sis')
    
    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)
    
    results = {}
    try:
        # 1. Verificar Usuário 2039
        try:
            user = client.make_request("User/2039")
            results['user_2039'] = user
        except Exception as e:
            results['user_2039_error'] = str(e)

        # 2. Listar Localizações (primeiras 5)
        try:
            data = client.make_request("Location", params={"range": "0-5"})
            results['valid_locations'] = data
        except Exception as e:
            results['locations_error'] = str(e)
            
        with open('inspection_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Resultados salvos em inspection_results.json")

    finally:
        client.close_session()

if __name__ == "__main__":
    inspect_data()
