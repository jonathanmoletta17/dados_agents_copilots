from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
from src.config import config
from src.glpi_client.client import GLPIClient

router = APIRouter()

class FormSubmission(BaseModel):
    serviceName: str = Field(...)
    atendimentoPara: str = Field(...)
    nomePessoa: Optional[str] = None
    localizacao: Optional[str] = None
    telefone: str = Field(...)
    urgencia: Optional[str] = None
    tipo: str = Field(...)
    assunto: str = Field(...)
    descricao: str = Field(...)
    campoExtra: Optional[str] = None

def map_urgency(label: Optional[str]) -> int:
    if not label:
        return 3
    l = label.strip().lower()
    # Se houver dígito inicial, usar o número diretamente (1..5/6)
    try:
        # Extrai primeiro dígito encontrado
        for ch in l:
            if ch.isdigit():
                val = int(ch)
                if 1 <= val <= 6:
                    return val
                break
    except Exception:
        pass
    # Fallback por palavra-chave
    if 'baixa' in l:
        return 2
    if 'alta' in l:
        return 4
    return 3

def get_search_field_id(client: GLPIClient, itemtype: str, target_field: str) -> int:
    """Obtém o ID do campo de busca ('name' ou 'completename')."""
    try:
        data = client.make_request(endpoint=f"searchOptions/{itemtype}")
        for entry in data:
            name = entry.get('name', '').lower()
            if name == target_field.lower():
                return int(entry.get('id'))
    except Exception:
        pass
    # Fallback comum para 'name'
    return 2

def resolve_category_id(client: GLPIClient, tipo_label: str) -> Optional[int]:
    # Preferir 'completename' para categorias hierárquicas
    field_id = get_search_field_id(client, 'ITILCategory', 'completename')
    try:
        data = client.make_request(
            endpoint="search/ITILCategory",
            params={
                "criteria[0][field]": field_id,
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": tipo_label,
                "range": "0-50"
            }
        )
        items = data.get('items') or data.get('data') or []
        for item in items:
            cid = item.get('id') or item.get('2')
            if cid:
                return int(cid)
    except Exception:
        pass
    # Fallback: listar categorias e tentar match no 'completename' ou 'name'
    try:
        cats = client.make_request("ITILCategory", params={"range": "0-999"})
        for c in cats or []:
            full = c.get('completename') or ''
            name = c.get('name') or ''
            if tipo_label.lower() in full.lower() or tipo_label.lower() in name.lower():
                cid = c.get('id')
                if cid:
                    return int(cid)
    except Exception:
        pass
    return None

def resolve_location_id(client: GLPIClient, loc_label: Optional[str]) -> Optional[int]:
    if not loc_label:
        return None
    field_id = get_search_field_id(client, 'Location', 'name')
    try:
        data = client.make_request(
            endpoint="search/Location",
            params={
                "criteria[0][field]": field_id,
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": loc_label,
                "range": "0-50"
            }
        )
        items = data.get('items') or data.get('data') or []
        for item in items:
            lid = item.get('id') or item.get('2')
            if lid:
                return int(lid)
    except Exception:
        pass
    # Fallback: listar localizações e tentar match
    try:
        locs = client.make_request("Location", params={"range": "0-999"})
        for l in locs or []:
            nm = l.get('name') or ''
            if loc_label.lower() in nm.lower():
                lid = l.get('id')
                if lid:
                    return int(lid)
    except Exception:
        pass
    return None

def resolve_user_id(client: GLPIClient, name_label: Optional[str]) -> Optional[int]:
    if not name_label:
        return None
    # Tentar em 'realname' e 'name'
    for field in ('realname', 'name'):
        field_id = get_search_field_id(client, 'User', field)
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
            items = data.get('items') or data.get('data') or []
            for item in items:
                uid = item.get('id') or item.get('2')
                if uid:
                    return int(uid)
        except Exception:
            continue
    return None

@router.post("/glpi/{context}/tickets")
def create_glpi_ticket(context: str, submission: FormSubmission) -> Dict:
    ctx = context.lower()
    if ctx not in ("sis", "dtic"):
        raise HTTPException(400, "Contexto inválido. Use 'sis' ou 'dtic'.")

    base_url = config.get_base_url(ctx)
    app_token = config.get_app_token(ctx)
    user_token = config.get_user_token(ctx)
    if not all([base_url, app_token, user_token]):
        raise HTTPException(500, "Configurações GLPI ausentes para o contexto.")

    client = GLPIClient(base_url=base_url, app_token=app_token, user_token=user_token)

    # Monta content com bloco de informações do formulário
    content_lines = []
    content_lines.append(submission.descricao.strip())
    content_lines.append(f"Telefone: {submission.telefone}")
    content_lines.append(f"Atendimento: {submission.atendimentoPara}")
    if submission.nomePessoa:
        content_lines.append(f"Nome pessoa: {submission.nomePessoa}")
    if submission.localizacao:
        content_lines.append(f"Localização: {submission.localizacao}")
    if submission.campoExtra:
        content_lines.append(f"Extra: {submission.campoExtra}")
    content = "\n".join(content_lines)

    # Resolvers
    urgency_num = map_urgency(submission.urgencia)
    # Dicionário básico de categorias por serviço (fallback)
    base_cat_by_service = {
        'Ar-Condicionado': 1,
        'Elétrica': 22,
        'Elevadores': 17,
        'Carregadores': 55,
        'Mensageria': 128
    }
    cat_id = resolve_category_id(client, submission.tipo)
    loc_id = resolve_location_id(client, submission.localizacao)
    requester_id = None
    if submission.atendimentoPara and submission.atendimentoPara.strip() == 'Para outra Pessoa':
        requester_id = resolve_user_id(client, submission.nomePessoa)

    # Fallbacks (em homologação, permitir prosseguir mesmo sem IDs resolvidos)
    ticket_input = {
        "name": submission.assunto.strip(),
        "content": content,
        "type": 2,
        "urgency": urgency_num,
        "requesttypes_id": 7
    }
    if cat_id is not None:
        ticket_input["itilcategories_id"] = cat_id
    elif submission.serviceName in base_cat_by_service:
        ticket_input["itilcategories_id"] = base_cat_by_service[submission.serviceName]
    if loc_id is not None:
        ticket_input["locations_id"] = loc_id
    if requester_id is not None:
        ticket_input["_users_id_requester"] = requester_id

    try:
        result = client.create_ticket(ticket_input)
        client.close_session()
        # GLPI geralmente retorna {"id": <id>, ...} com status 201
        ticket_id = result.get("id") or result.get("ticket_id")
        return {"success": True, "ticket_id": ticket_id, "glpi_response": result}
    except Exception as e:
        client.close_session()
        raise HTTPException(500, f"Falha ao criar ticket: {e}")
