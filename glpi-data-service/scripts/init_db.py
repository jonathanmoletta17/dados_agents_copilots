import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.postgres_manager import get_db_manager
from src.config import config

def init_db():
    print(f"🚀 Initializing databases...")
    print(f"🔌 URL: {config.DATABASE_URL}")
    
    for context in ['dtic', 'sis']:
        print(f"📦 Creating tables for context: {context}")
        try:
            db = get_db_manager(context)
            db.create_tables()
            print(f"✅ Tables created for {context}")
        except Exception as e:
            print(f"❌ Error initializing {context}: {e}")

if __name__ == "__main__":
    init_db()
