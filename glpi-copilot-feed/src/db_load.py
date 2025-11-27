import pandas as pd
from sqlalchemy import text, inspect
from src.db_extract import get_connection
import logging

logger = logging.getLogger(__name__)

def create_tables():
    """
    Creates necessary tables in the 'dtic' schema if they don't exist.
    """
    engine = get_connection()
    
    # SQL definitions for new tables
    # Using simple types for now, can be refined.
    # We use 'IF NOT EXISTS' to avoid errors.
    
    # Ticket Tasks
    sql_tasks = """
    CREATE TABLE IF NOT EXISTS dtic.tickettasks (
        id BIGINT PRIMARY KEY,
        tickets_id BIGINT,
        tasks_id BIGINT,
        is_private INTEGER,
        date TIMESTAMP,
        users_id BIGINT,
        users_id_tech BIGINT,
        content TEXT,
        actiontime INTEGER,
        state INTEGER,
        users_id_editor BIGINT,
        date_mod TIMESTAMP,
        date_creation TIMESTAMP,
        taskcategories_id BIGINT,
        begin TIMESTAMP,
        end_ TIMESTAMP,
        uuid VARCHAR(255),
        links TEXT,
        timeline_position INTEGER
    );
    """
    
    # Problems
    sql_problems = """
    CREATE TABLE IF NOT EXISTS dtic.problems (
        id BIGINT PRIMARY KEY,
        name VARCHAR(255),
        date TIMESTAMP,
        closedate TIMESTAMP,
        solvedate TIMESTAMP,
        date_mod TIMESTAMP,
        users_id_recipient BIGINT,
        users_id_lastupdater BIGINT,
        status INTEGER,
        priority INTEGER,
        impact INTEGER,
        urgency INTEGER,
        content TEXT
    );
    """
    
    # Changes
    sql_changes = """
    CREATE TABLE IF NOT EXISTS dtic.changes (
        id BIGINT PRIMARY KEY,
        name VARCHAR(255),
        date TIMESTAMP,
        closedate TIMESTAMP,
        solvedate TIMESTAMP,
        date_mod TIMESTAMP,
        users_id_recipient BIGINT,
        users_id_lastupdater BIGINT,
        status INTEGER,
        priority INTEGER,
        impact INTEGER,
        urgency INTEGER,
        content TEXT
    );
    """
    
    # Followups (if we decide to store them fully later, for now just structure)
    # But wait, we are not fetching full followups yet, only counting.
    # I will create the table definition just in case, but might not use it yet.
    # Actually, let's stick to what we have data for.
    
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS dtic;"))
        conn.execute(text(sql_tasks))
        conn.execute(text(sql_problems))
        conn.execute(text(sql_changes))
        conn.commit()
        logger.info("Tables checked/created in 'dtic' schema.")

def load_data_to_db(df: pd.DataFrame, table_name: str, if_exists='replace'):
    """
    Loads a DataFrame into a PostgreSQL table.
    """
    if df.empty:
        logger.warning(f"DataFrame for {table_name} is empty. Skipping load.")
        return

    engine = get_connection()
    
    try:
        # Ensure schema is specified
        schema = 'dtic'
        
        # Clean column names to match DB if necessary (lowercase)
        df.columns = [c.lower() for c in df.columns]
        
        # Handle 'end' reserved keyword in tasks if present (renamed to end_ in SQL)
        if 'end' in df.columns:
            df.rename(columns={'end': 'end_'}, inplace=True)

        # Convert dict/list columns to JSON string to avoid psycopg2 errors
        import json
        import html
        for col in df.columns:
            # Check for dict/list
            if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
            
            # Check for string columns to unescape HTML entities
            elif df[col].dtype == 'object':
                # Apply html.unescape to string columns, handling None/NaN
                df[col] = df[col].apply(lambda x: html.unescape(str(x)) if isinstance(x, str) else x)

        logger.info(f"Loading {len(df)} rows into {schema}.{table_name}...")
        
        # Using chunksize for better performance on large datasets
        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=1000,
            method='multi'
        )
        logger.info(f"Successfully loaded data into {schema}.{table_name}.")
        
    except Exception as e:
        logger.error(f"Failed to load data into {table_name}: {e}")
        raise
