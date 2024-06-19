from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager

DATABASE_URL_1 = os.getenv("DATABASE_URL_1")
DATABASE_URL_2 = os.getenv("DATABASE_URL_2")

engine_1 = create_engine(DATABASE_URL_1)
engine_2 = create_engine(DATABASE_URL_2)

SessionLocal_1 = sessionmaker(autocommit=False, autoflush=False, bind=engine_1)
SessionLocal_2 = sessionmaker(autocommit=False, autoflush=False, bind=engine_2)

Base = declarative_base()

@contextmanager
def get_db(courier_id: int):
    if courier_id % 2 == 0:
        db = SessionLocal_1()
    else:
        db = SessionLocal_2()
    try:
        yield db
    finally:
        db.close()
