"""
Dashboard Gerencial GLPI – Casa Civil RS
=======================================

Objetivo: fornecer visão operacional clara e acessível ao diretor e equipe gerencial,
substituindo métricas técnicas por indicadores práticos e visuais.

Autor: Analista de Dados – Casa Civil
"""
import os
import sys
import pandas as pd
import datetime as dt
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from file_manager import FileManager

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
XLSX_DIR = os.path.join(BASE_DIR, "dados", "tickets_completos")
XLSX_BASE = os.path.join(XLSX_DIR, "todos_tickets_base_atual.xlsx")
XLSX_PATH = os.path.join(XLSX_DIR, "todos_tickets_atual.xlsx")

class DashboardGerencial:
    def __init__(self):
        self.df = None
        self.periodo_inicio = None
        self.periodo_fim = None
        self.load_data()

    def load_data(self):
        path = XLSX_BASE if os.path.exists(XLSX_BASE) else XLSX_PATH
        self.df = pd.read_excel(path)
        # converte datas
        for c in ["Data Criação", "Data Modificação"]:
            if c in self.df.columns:
                self.df[c] = pd.to_datetime(self.df[c], errors="coerce", dayfirst=True)
        # define período
        self.periodo_inicio = self.df["Data Criação"].min()
        self.periodo_fim = self.df["Data Criação"].max()

    def print_header(self, titulo):
        print("\n" + "=" * 70)
        print(titulo)
        print("=" * 70)

    def top_tecnicos_mais_demandados(self, top=10):
        """Lista técnicos mais solicitados (requerente → técnico)"""
        self.print_header("Técnicos Mais Demandados")
        if "Técnico" not in self.df.columns:
            print("[AVISO] Coluna Técnico não encontrada")
            return
        cont = Counter(self.df["Técnico"].dropna())
        for nome, qtd in cont.most_common(top):
            pct = (qtd / len(self.df)) * 100
            print(f"   • {nome:<35} {qtd:>5} chamados ({pct:>4.1f}%)")

    def locais_mais_atendidos_periodo(self, dias=30, top=10):
        """Locais (entidades) mais atendidos nos últimos dias"""
        self.print_header(f"Locais Mais Atendidos – Últimos {dias} dias")
        if "Entidade" not in self.df.columns:
            print("[AVISO] Coluna Entidade não encontrada")
            return
        corte = self.periodo_fim - pd.Timedelta(days=dias)
        df_recente = self.df[self.df["Data Criação"] >= corte]
        cont = Counter(df_recente["Entidade"].dropna())
        total = len(df_recente)
        for nome, qtd in cont.most_common(top):
            pct = (qtd / total) * 100
            print(f"   • {nome:<35} {qtd:>5} chamados ({pct:>4.1f}%)")

    def tipos_solicitacoes_mais_frequentes(self, top=10):
        """Tipos de solicitações mais frequentes (por categoria)"""
        self.print_header("Tipos de Solicitações Mais Frequentes")
        if "Categoria" not in self.df.columns:
            print("[AVISO] Coluna Categoria não encontrada")
            return
        cont = Counter(self.df["Categoria"].dropna())
        for nome, qtd in cont.most_common(top):
            pct = (qtd / len(self.df)) * 100
            print(f"   • {nome:<45} {qtd:>5} chamados ({pct:>4.1f}%)")

    def relacao_requerente_tecnico(self, tecnico_filtro="Edson", top=10):
        """Requerentes que mais solicitam a um técnico específico"""
        self.print_header(f"Principais Requerentes do Técnico '{tecnico_filtro}'")
        if "Técnico" not in self.df.columns or "Requerente" not in self.df.columns:
            print("[AVISO] Colunas Técnico/Requerente não encontradas")
            return
        df_tec = self.df[self.df["Técnico"].str.contains(tecnico_filtro, case=False, na=False)]
        if df_tec.empty:
            print(f"   • Nenhum chamado encontrado para '{tecnico_filtro}'")
            return
        cont = Counter(df_tec["Requerente"].dropna())
        total = len(df_tec)
        for nome, qtd in cont.most_common(top):
            pct = (qtd / total) * 100
            print(f"   • {nome:<35} {qtd:>5} chamados ({pct:>4.1f}%)")

    def chamados_por_dia_semana(self):
        """Distribuição por dia da semana (útil para planejar escalas)"""
        self.print_header("Chamados por Dia da Semana")
        if "Data Criação" not in self.df.columns:
            print("[AVISO] Data Criação não encontrada")
            return
        dias = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
        self.df["dia_semana"] = self.df["Data Criação"].dt.weekday
        cont = Counter(self.df["dia_semana"])
        for d, nome in dias.items():
            qtd = cont.get(d, 0)
            pct = (qtd / len(self.df)) * 100
            print(f"   • {nome:<10} {qtd:>5} chamados ({pct:>4.1f}%)")

    def situacoes_atipicas(self):
        """Situações que merecem atenção gerencial"""
        self.print_header("Situações Atípicas – Requer Atenção")
        # 1. Chamados antigos abertos
        if "Status" in self.df.columns and "Data Criação" in self.df.columns:
            abertos = self.df[self.df["Status"].str.contains("Aberto|Aberto - Em andamento", case=False, na=False)]
            if not abertos.empty:
                antigos = abertos[abertos["Data Criação"] < (self.periodo_fim - pd.Timedelta(days=30))]
                if not antigos.empty:
                    print(f"   • {len(antigos)} chamados abertos há mais de 30 dias")
        # 2. Categorias genéricas
        if "Categoria" in self.df.columns:
            genericas = self.df[self.df["Categoria"].str.contains("sem categoria|outros|não classificado", case=False, na=False)]
            if not genericas.empty:
                print(f"   • {len(genericas)} chamados com categorização genérica")
        # 3. Grupos sem atribuição
        if "Grupo" in self.df.columns:
            sem_grupo = self.df[self.df["Grupo"] == "Sem Grupo"]
            if not sem_grupo.empty:
                print(f"   • {len(sem_grupo)} chamados sem grupo técnico definido")

    def tempo_medio_resolucao_simples(self):
        """Tempo médio entre abertura e última modificação (proxy de resolução)"""
        self.print_header("Tempo Médio de Resolução (simplificado)")
        if "Data Criação" not in self.df.columns or "Data Modificação" not in self.df.columns:
            print("[AVISO] Datas não disponíveis")
            return
        df_ok = self.df.dropna(subset=["Data Criação", "Data Modificação"])
        df_ok = df_ok[df_ok["Data Modificação"] >= df_ok["Data Criação"]]  # remove inconsistências
        df_ok["delta_h"] = (df_ok["Data Modificação"] - df_ok["Data Criação"]).dt.total_seconds() / 3600
        mediana = df_ok["delta_h"].median()
        media = df_ok["delta_h"].mean()
        print(f"   • Mediana: {mediana:.1f} horas")
        print(f"   • Média:   {media:.1f} horas")

    def exportar_tabela_simples(self):
        """Gera XLSX resumido para visualização/planilha"""
        pasta = os.path.join(BASE_DIR, "dados", "metricas_xlsx")
        os.makedirs(pasta, exist_ok=True)
        # Top entidades últimos 30 dias
        corte = self.periodo_fim - pd.Timedelta(days=30)
        df_recente = self.df[self.df["Data Criação"] >= corte]
        top_ent = df_recente["Entidade"].value_counts().head(10).reset_index()
        top_ent.columns = ["Entidade", "Chamados_30d"]
        FileManager.salvar_com_backup(top_ent, FileManager.gerar_nome_fixo(pasta, "top_entidades_30d"), "top entidades 30d")
        # Top técnicos últimos 30 dias
        top_tec = df_recente["Técnico"].value_counts().head(10).reset_index()
        top_tec.columns = ["Técnico", "Chamados_30d"]
        FileManager.salvar_com_backup(top_tec, FileManager.gerar_nome_fixo(pasta, "top_tecnicos_30d"), "top técnicos 30d")

    def executar_dashboard(self):
        print("\n" + "=" * 70)
        print("DASHBOARD GERENCIAL – CASA CIVIL RS")
        print("Período:", self.periodo_inicio.strftime("%d/%m/%Y"), "a", self.periodo_fim.strftime("%d/%m/%Y"))
        print("Total de chamados:", len(self.df))
        print("=" * 70)
        self.top_tecnicos_mais_demandados()
        self.locais_mais_atendidos_periodo()
        self.tipos_solicitacoes_mais_frequentes()
        self.relacao_requerente_tecnico(tecnico_filtro="Edson")  # exemplo
        self.chamados_por_dia_semana()
        self.situacoes_atipicas()
        self.tempo_medio_resolucao_simples()
        self.exportar_tabela_simples()
        print("\n[OK] Dashboard concluído – arquivos XLSX salvos em dados/metricas_xlsx/")

def main():
    dash = DashboardGerencial()
    dash.executar_dashboard()

if __name__ == "__main__":
    main()