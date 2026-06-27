from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
from models_orm import Base
import logging
# PostgreSQL connection settings (ЗАМЕНИ НА СВОИ!)
DB_NAME = "practice"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger = logging.getLogger()
# ORM
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
# def create_database_if_not_exists():
#     """Подключаемся к служебной БД postgres и создаём нашу БД, если её нет."""
#     service_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
#     engine = create_engine(service_url, isolation_level="AUTOCOMMIT")

#     with engine.connect() as conn:
#         exists = conn.execute(
#             text("SELECT 1 FROM pg_database WHERE datname = :name"),
#             {"name": DB_NAME}
#         ).scalar()

#         if not exists:
#             conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
#             logger.info(f"Database '{DB_NAME}' created.")
#         else:
#             logger.info(f"Database '{DB_NAME}' already exists.")

#     engine.dispose()


# def init_db():
#     create_database_if_not_exists()

#     # Теперь подключаемся к нашей БД и создаём таблицы по моделям
#     DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     engine = create_engine(DATABASE_URL)
    
#     Base.metadata.create_all(engine)  # создаёт только отсутствующие таблицы
#     logger.info("All tables created successfully")

#     Session = sessionmaker(bind=engine)
#     return Session()


# session = init_db()

# Native SQL
def get_native_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def get_native_cursor():
    conn = get_native_conn()
    return conn, conn.cursor(cursor_factory=RealDictCursor)
