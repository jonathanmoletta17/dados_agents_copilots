import os
import json
import subprocess

def run(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
        raise RuntimeError(err.decode(errors="ignore"))
    return out.decode("utf-8", errors="ignore")

def main():
    base = os.path.dirname(__file__)
    schema = os.path.join(base, "create_schema.py")
    loader = os.path.join(base, "load_csv_tickets_flat.py")
    query = os.path.join(base, "query_tickets_json.py")
    run(f"python \"{schema}\"")
    run(f"python \"{loader}\"")
    payload = run(f"python \"{query}\" --page 1 --page_size 1000")
    data = json.loads(payload)
    assert data.get("status") == "ok"
    items = data["data"]["dados"]
    assert len(items) > 0
    jmap = {it["ID"]: it for it in items}
    if "11162" in jmap:
        it = jmap["11162"]
        assert it["Status"] == "Fechado"
        assert it["Categoria"] == "AJUDA E SUPORTE"
        assert it["Entidade"] == "CASA CIVIL"
        assert it["Requerente"] == "Paulo Ricardo Duarte Speck"
        assert it["Técnico"] == "Alessandro Carbonera Vieira"
        assert it["Grupo"] == "Sem Grupo"
    print(json.dumps({"ok": True, "total_page": len(items)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
