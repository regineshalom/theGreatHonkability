from sqlalchemy import create_engine, text
from pathlib import Path

def init_db():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "budget.db"

    engine = create_engine(f"sqlite+pysqlite:///{DB_PATH}", echo=True) ## equivalent to create_engine("sqlite:///budget.db"), sqlalchemy chooses the correct sqlite driver in most cases, if ever migrate, the syntax is engine = create_engine()"postgresql+psycopg://user:password@localhost/budget") where dialect+driver://...

    ## for future deployment
    # @event.listens_for(engine, "connect")
    # def enable_foreign_keys(dbapi_connection, connection_record):
    #     cursor = dbapi_connection.cursor()
    #     cursor.execute("PRAGMA foreign_keys=ON")
    #     cursor.close()

    ## Creation of the table and insertion of initial data
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS category (
                cat_name TEXT,
                sub_cat TEXT,
                cat_budget INTEGER not null,
                cat_id INTEGER PRIMARY KEY,
                UNIQUE(cat_name, sub_cat)
            )
        """))
        conn.execute(text("""
            insert or ignore into category (cat_name, sub_cat, cat_budget) values (:cat_name, :sub_cat, :cat_budget)
            """),
                     [
                        {"cat_name": "food", "sub_cat": "lunch", "cat_budget": 31000},
                        {"cat_name": "food", "sub_cat": "dinner", "cat_budget": 31000},
                        {"cat_name": "food", "sub_cat": "coffee", "cat_budget": 9300},
                        {"cat_name": "public transportation", "sub_cat": None, "cat_budget": 10000},
                        {"cat_name": "tardiness", "sub_cat": None, "cat_budget": 10000},
                        {"cat_name": "whimsies", "sub_cat": "clothes", "cat_budget": 10000},
                        {"cat_name": "whimsies", "sub_cat": "misc", "cat_budget": 10000}
                     ])

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS expenses (
                exp_id INTEGER PRIMARY KEY,
                exp_name TEXT not null,
                exp_amount NUMERIC(10, 2) not null,
                exp_datetime timestamp not null default (datetime('now', 'localtime')),
                cat_id INTEGER not null,
                telegram_chat_id INTEGER not null,
                telegram_message_id INTEGER not null,
                FOREIGN KEY (cat_id) REFERENCES category (cat_id),
                UNIQUE (telegram_chat_id, telegram_message_id)
            )
        """))

init_db()