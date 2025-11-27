import sys
from src.config import config
from src.glpi_client.client import GLPIClient

# Copiando as funções do backend para teste isolado
def get_search_field_id(client: GLPIClient, itemtype: str, target_field: str) -> int:
    """Obtém o ID do campo de busca ('name' ou 'completename')."""
    try:
        data = client.make_request(endpoint=f"searchOptions/{itemtype}")
        for entry in data:
            # entry pode ser dict ou list, dependendo da versão GLPI, mas geralmente é list of dicts ou dict of dicts
            # No GLPI API, searchOptions retorna um objeto onde as chaves são os IDs ou uma lista.
            # Vamos imprimir data para ver estrutura se falhar.
            
            # Ajuste: A resposta de searchOptions costuma ser um Dict onde Key=ID e Value=Metadata
            # OU uma lista. O código original itera sobre 'data'. Se data for dict, itera chaves.
            # Se for lista, itera itens.
            
            # Vamos assumir que o código original estava tentando iterar lista.
            # Mas se data for dict (o que é comum no GLPI 9.5+), entry será a chave (ID).
            pass 
            
        # Vamos usar a implementação exata do glpi_submit.py para ver se ela está quebrada
        for entry in data:
            name = entry.get('name', '').lower()
            if name == target_field.lower():
                return int(entry.get('id'))
    except Exception as e:
        print(f"Erro em get_search_field_id: {e}")
    
    # Fallbacks manuais
    if target_field.lower() == 'name':
        return 1
    if target_field.lower() == 'realname':
        return 9
    return 1

def resolve_user_id(client: GLPIClient, name_label: str):
    print(f"Tentando resolver: {name_label}")
    for field in ('realname', 'name'):
        print(f"  Buscando em campo: {field}")
        field_id = get_search_field_id(client, 'User', field)
        print(f"    ID do campo '{field}': {field_id}")
        
        try:
            data = client.make_request(
                endpoint="search/User",
                params={
                    "criteria[0][field]": field_id,
                    "criteria[0][searchtype]": "contains",
                    "criteria[0][value]": name_label,
                    "range": "0-50"
                }
            )
            # print(f"    Resposta crua: {data}")
            items = data.get('items') or data.get('data') or []
            print(f"    Itens encontrados: {len(items)}")
            for item in items:
                uid = item.get('id') or item.get('2')
                if uid:
                    print(f"    -> Encontrado ID: {uid}")
                    return int(uid)
        except Exception as e:
            print(f"    Erro na busca: {e}")
            continue
    return None

def debug():
    base_url = config.get_base_url('sis')
    app_token = config.get_app_token('sis')
    user_token = config.get_user_token('sis')
    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)

    try:
        # Teste com o login exato
        uid = resolve_user_id(client, "jonathan-moletta")
        print(f"Resultado Final: {uid}")
        
        # Debug extra: ver o que searchOptions retorna
        print("\n--- Debug SearchOptions/User ---")
        opts = client.make_request("searchOptions/User")
        # Imprimir primeiros 3 itens para ver estrutura
        if isinstance(opts, list):
            print("É lista")
            print(opts[:3])
        elif isinstance(opts, dict):
            print("É dict")
            import itertools
            print(dict(itertools.islice(opts.items(), 3)))
            
    finally:
        client.close_session()

if __name__ == "__main__":
    debug()
