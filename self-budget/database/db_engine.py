from sqlalchemy import create_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "budget.db"

engine = create_engine(f"sqlite+pysqlite:///{DB_PATH}", echo=True)