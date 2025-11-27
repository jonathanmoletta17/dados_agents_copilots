import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def get_connection():
    """
    Cria e retorna uma conexão com o PostgreSQL `glpi_data`
    usando variáveis de ambiente.
    """
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "glpi_data")

    if not user or not password:
        raise ValueError(
            "Credenciais do banco não configuradas. "
            "Defina PGUSER e PGPASSWORD no arquivo .env"
        )

    # Construct SQLAlchemy connection string
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Create engine
    engine = create_engine(db_url)
    return engine

def load_dtic_tickets(conn=None) -> pd.DataFrame:
    """
    Lê dtic.tickets com as colunas especificadas,
    adiciona colunas derivadas (ano, mes, ano_mes),
    e retorna um DataFrame pandas.
    """
    if conn is None:
        conn = get_connection()

    # Query selecting only non-sensitive fields and dimensions
    query = """
        SELECT
            id,
            glpi_id,
            status,
            prioridade,
            tipo,
            categoria,
            entidade,
            grupo,
            grupo_nivel,
            requerente,
            tecnico,
            localizacao,
            criado_em,
            solucionado_em,
            fechado_em,
            tempo_para_resolver,
            tempo_acao_total
        FROM
            dtic.tickets
        WHERE
            is_deleted = false
    """

    # Read data into DataFrame
    df = pd.read_sql(query, conn)

    # Ensure datetime columns are properly typed
    date_cols = ['criado_em', 'solucionado_em', 'fechado_em']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Create derived columns
    if 'criado_em' in df.columns:
        df['ano'] = df['criado_em'].dt.year
        df['mes'] = df['criado_em'].dt.month
        df['ano_mes'] = df['criado_em'].dt.strftime('%Y-%m')

    return df

if __name__ == "__main__":
    # Simple test block
    try:
        print("Connecting to database...")
        df = load_dtic_tickets()
        print(f"Successfully loaded {len(df)} tickets.")
        print("Columns:", df.columns.tolist())
        print(df.head(3))
    except Exception as e:
        print(f"Error: {e}")
