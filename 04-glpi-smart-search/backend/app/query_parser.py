from typing import Dict, Any, Tuple, List
import datetime as dt

def parse(q: str, filters: Dict[str, Any]) -> Tuple[str, List[Any], str, List[Any]]:
    tokens = q.strip()
    match = tokens if tokens else None
    where = []
    params = []
    inc_del = str(filters.get("include_deleted", "")).lower() in {"1","true","t","yes","y"}
    if not inc_del:
        where.append("status != ?")
        params.append("excluido")
    for k in ["status","prioridade","categoria","entidade","tecnico","grupo","requerente"]:
        v = filters.get(k)
        if v:
            where.append(f"{k} LIKE ?")
            params.append(v.lower()+"%")
    if filters.get("dt_ini"):
        try:
            d = dt.datetime.strptime(filters["dt_ini"], "%d/%m/%Y")
            where.append("data_criacao >= ?")
            params.append(d.strftime("%Y-%m-%d 00:00:00"))
        except Exception:
            pass
    if filters.get("dt_fim"):
        try:
            d = dt.datetime.strptime(filters["dt_fim"], "%d/%m/%Y")
            where.append("data_criacao <= ?")
            params.append(d.strftime("%Y-%m-%d 23:59:59"))
        except Exception:
            pass
    where_sql = " AND ".join(where)
    return match, params, where_sql, []