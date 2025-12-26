import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

with open("settings.json") as f:
    settings = json.load(f)["db"]

db_password = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{settings['user']}:{db_password}@"
    f"{settings['host']}:{settings['port']}/{settings['database']}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
