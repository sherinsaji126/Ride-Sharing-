from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv("Credentials.env")



DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}"
f"@{DB_SERVER}/{DB_NAME}"
"?driver=ODBC+Driver+17+for+SQL+Server"
"&TrustServerCertificate=yes"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
