from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(override=True)
db_url = os.environ.get('DATABASE_URL')
print("DB URL:", repr(db_url))

try:
    engine = create_engine(db_url)
    conn = engine.connect()
    print("Connected to:", engine.url)
    conn.close()
    print("Success")
except Exception as e:
    print("Error:", type(e).__name__, "-", str(e))
