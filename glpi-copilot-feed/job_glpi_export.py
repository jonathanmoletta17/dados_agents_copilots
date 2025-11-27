import os
import sys
import logging
from datetime import datetime
from src.export_csv import generate_all_csvs
from src.sharepoint_upload import upload_csvs_to_sharepoint
from src.db_load import create_tables

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("job_execution.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run() -> None:
    """
    Executa o fluxo completo de exportação de dados do GLPI da DTIC
    para CSVs e upload para SharePoint.
    """
    start_time = datetime.now()
    logger.info("=== Iniciando Job de Exportação GLPI para Copilot ===")
    
    output_dir = os.path.join(os.getcwd(), "output")
    
    try:
        # Etapa 0: Criar tabelas no banco se não existirem
        logger.info(">>> Etapa 0/3: Verificando/criando tabelas no banco...")
        create_tables()
        logger.info("Tabelas verificadas/criadas com sucesso.")
        
        # Etapa 1 & 2: Extração e Geração de CSVs
        logger.info(">>> Etapa 1/3: Gerando arquivos CSV...")
        generate_all_csvs(output_dir)
        logger.info("Arquivos CSV gerados com sucesso.")
        
        # Etapa 2: Upload para SharePoint (Opcional)
        if os.getenv("ENABLE_SHAREPOINT_UPLOAD", "false").lower() == "true":
            logger.info(">>> Etapa 2/3: Enviando para SharePoint...")
            upload_csvs_to_sharepoint(output_dir)
            logger.info("Upload concluído com sucesso.")
        else:
            logger.info(">>> Etapa 2/3: Upload para SharePoint desativado (ENABLE_SHAREPOINT_UPLOAD=false).")
            logger.info(f"Arquivos CSV disponíveis em: {output_dir}")
        
    except Exception as e:
        logger.error(f"FALHA CRÍTICA NO JOB: {e}", exc_info=True)
        sys.exit(1)
        
    duration = datetime.now() - start_time
    logger.info(f"=== Job Finalizado com Sucesso (Duração: {duration}) ===")

if __name__ == "__main__":
    run()
