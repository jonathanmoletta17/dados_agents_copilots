import os
import sys
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from file_manager import FileManager

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
XLSX_DIR = os.path.join(BASE_DIR, "..", "dados", "tickets_completos")
XLSX_BASE = os.path.join(XLSX_DIR, "todos_tickets_base_atual.xlsx")
XLSX_PATH = os.path.join(XLSX_DIR, "todos_tickets_atual.xlsx")

def _infer_tipo(col, series, total):
    name = col
    s = series
    try:
        if name.lower() in ["data criação", "data modificação", "data solução", "data fechamento"]:
            pd.to_datetime(s, errors="coerce", dayfirst=True)
            return "data/hora"
    except Exception:
        pass
    if name.lower() in ["status", "categoria", "entidade", "grupo", "técnico", "requerente"]:
        return "categórico"
    try:
        pd.to_numeric(s, errors="raise")
        return "numérico"
    except Exception:
        pass
    try:
        nunique = s.nunique(dropna=True)
        ratio = nunique / max(total, 1)
        return "categórico" if ratio < 0.02 else "texto"
    except Exception:
        return "texto"

def main():
    path = XLSX_BASE if os.path.exists(XLSX_BASE) else XLSX_PATH
    df = pd.read_excel(path)
    total = len(df)
    perfil_rows = []
    for col in df.columns:
        nulos = float(df[col].isna().mean() * 100)
        tipo = _infer_tipo(col, df[col], total)
        perfil_rows.append({"coluna": col, "tipo_inferido": tipo, "percentual_nulos": round(nulos, 2)})
    pasta_out = os.path.join(BASE_DIR, "..", "dados", "metricas_xlsx")
    FileManager.salvar_com_backup(pd.DataFrame(perfil_rows), FileManager.gerar_nome_fixo(pasta_out, "columns_profile"), "perfil de colunas")
    resumo = []
    resumo.append({"metrica": "linhas", "valor": total})
    resumo.append({"metrica": "colunas", "valor": len(df.columns)})
    for dc in ["Data Criação", "Data Modificação"]:
        if dc in df.columns:
            try:
                dts = pd.to_datetime(df[dc], errors="coerce", dayfirst=True)
                dmin = dts.min()
                dmax = dts.max()
                vmin = dmin.strftime("%Y-%m-%d %H:%M") if pd.notna(dmin) else ""
                vmax = dmax.strftime("%Y-%m-%d %H:%M") if pd.notna(dmax) else ""
                resumo.append({"metrica": f"{dc} min", "valor": vmin})
                resumo.append({"metrica": f"{dc} max", "valor": vmax})
            except Exception:
                pass
    FileManager.salvar_com_backup(pd.DataFrame(resumo), FileManager.gerar_nome_fixo(pasta_out, "dataset_resumo"), "resumo do dataset")
    print("[OK] Perfil e resumo gerados")

if __name__ == "__main__":
    main()