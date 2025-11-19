# Script de Limpeza e Organização Final do Projeto GLPI
# Este script remove arquivos desnecessários e organiza o projeto

import os
import shutil
import glob

def limpar_arquivos_desnecessarios():
    """Remove arquivos de backup e duplicatas desnecessárias"""
    
    print("=== LIMPEZA DE ARQUIVOS DESNECESSÁRIOS ===\n")
    
    # Arquivos a remover (padrões)
    padroes_remover = [
        "**/*_anterior.csv",
        "**/todos_tickets_limpos.csv",
        "**/todos_tickets_limpos_v2.csv", 
        "**/todos_tickets_limpos_cirurgico.*",
        "**/todos_tickets_limpos_inteligente.*",
        "**/limpar_tickets_completos.py",
        "**/limpar_tickets_refinado.py",
        "**/limpar_tickets_cirurgico.py",
        "**/limpar_tickets_final.py",
        "**/limpar_tickets_inteligente.py",
        "**/analisar_limpeza_tickets.py",
        "**/limpar_tickets_*.py"  # Remove todos os scripts antigos exceto o preciso
    ]
    
    arquivos_removidos = []
    
    for padrao in padroes_remover:
        arquivos = glob.glob(padrao, recursive=True)
        for arquivo in arquivos:
            try:
                if os.path.isfile(arquivo):
                    os.remove(arquivo)
                    arquivos_removidos.append(arquivo)
                    print(f"✅ Removido: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
    
    print(f"\nTotal de arquivos removidos: {len(arquivos_removidos)}")
    
    return arquivos_removidos

def organizar_scripts_python():
    """Organiza os scripts Python nos diretórios corretos"""
    
    print("\n=== ORGANIZAÇÃO DE SCRIPTS PYTHON ===\n")
    
    # Mover scripts de limpeza para análise de dados
    script_limpeza = "scripts/dados/tickets_completos/limpar_tickets_preciso.py"
    destino_limpeza = "02-analise-dados-glpi/scripts/"
    
    if os.path.exists(script_limpeza):
        try:
            shutil.copy2(script_limpeza, destino_limpeza)
            print(f"✅ Script de limpeza copiado para: {destino_limpeza}")
        except Exception as e:
            print(f"❌ Erro ao copiar script de limpeza: {e}")
    
    # Copiar scripts de ETL importantes
    etl_scripts = [
        "scripts/python/extrair_todos_tickets.py",
        "scripts/python/extrair_metricas_tickets_otimizado.py",
        "scripts/python/continuous_scheduler.py",
        "scripts/python/scheduler.py"
    ]
    
    destino_etl = "03-integracao-glpi/etl/"
    
    for script in etl_scripts:
        if os.path.exists(script):
            try:
                shutil.copy2(script, destino_etl)
                print(f"✅ Script ETL copiado: {os.path.basename(script)}")
            except Exception as e:
                print(f"❌ Erro ao copiar {script}: {e}")

def criar_readmes_organizados():
    """Cria READMEs para cada projeto organizado"""
    
    print("\n=== CRIAÇÃO DE ARQUIVOS README ===\n")
    
    # README para API Atlas
    readme_api = """# GLPI API Atlas

Mapeamento completo da API REST do GLPI com documentação OpenAPI, SDK Python e exemplos.

## Estrutura
- `docs/` - Documentação OpenAPI e markdown
- `sdk/` - Client SDK Python
- `examples/` - Exemplos de uso
- `collections/` - Coleções Postman/Insomnia

## Uso Rápido
```python
from glpi_client import GLPIClient

client = GLPIClient(url="https://glpi.example.com", app_token="seu_token")
client.init_session(user_token="seu_user_token")

tickets = client.tickets.list()
```
"""

    with open("01-glpi-api-atlas/README.md", "w", encoding="utf-8") as f:
        f.write(readme_api)
    print("✅ README criado para API Atlas")
    
    # README para Análise de Dados
    readme_analise = """# Análise de Dados GLPI

Projeto de análise e limpeza de dados de tickets do GLPI.

## Estrutura
- `data/raw/` - Dados brutos (CSVs originais)
- `data/processed/` - Dados limpos (XLSX/CSV processados)
- `data/reports/` - Relatórios gerados
- `scripts/` - Scripts de limpeza e análise

## Uso
```bash
# Limpar dados de tickets
python scripts/limpar_tickets_preciso.py

# Arquivo principal: todos_tickets_limpos_preciso.xlsx
```
"""

    with open("02-analise-dados-glpi/README.md", "w", encoding="utf-8") as f:
        f.write(readme_analise)
    print("✅ README criado para Análise de Dados")
    
    # README para Integração
    readme_integracao = """# Integração GLPI

Projeto de integração com banco de dados SQLite e sincronização.

## Estrutura
- `database/` - Banco SQLite e schemas
- `etl/` - Scripts de ETL
- `sync/` - Scripts de sincronização

## Uso
```bash
# Executar ETL
python etl/extrair_todos_tickets.py

# Banco de dados: database/glpi.sqlite
```
"""

    with open("03-integracao-glpi/README.md", "w", encoding="utf-8") as f:
        f.write(readme_integracao)
    print("✅ README criado para Integração")

def main():
    """Executa toda a organização"""
    
    print("🚀 INICIANDO ORGANIZAÇÃO FINAL DO PROJETO GLPI")
    print("=" * 60)
    
    # 1. Limpar arquivos desnecessários
    arquivos_removidos = limpar_arquivos_desnecessarios()
    
    # 2. Organizar scripts
    organizar_scripts_python()
    
    # 3. Criar READMEs
    criar_readmes_organizados()
    
    print("\n" + "=" * 60)
    print("✅ ORGANIZAÇÃO CONCLUÍDA!")
    print(f"📊 Arquivos removidos: {len(arquivos_removidos)}")
    print("\n📁 Estrutura organizada:")
    print("  📋 01-glpi-api-atlas/ - Mapeamento da API")
    print("  📊 02-analise-dados-glpi/ - Análise de dados")  
    print("  🔄 03-integracao-glpi/ - Integração e banco")
    print("\n✨ O projeto agora está organizado e limpo!")

if __name__ == "__main__":
    main()