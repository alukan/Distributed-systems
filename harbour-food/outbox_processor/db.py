import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


NUMBER_OF_DBS = int(os.getenv("NUMBER_OF_DBS", 2))
DATABASE_URL_TEMPLATE = "mysql+mysqlconnector://user{user}:password{password}@mysql_db_{index}:3306/courier_db_{index}"

engines = []
SessionLocals = []
Base = declarative_base()

for i in range(1, NUMBER_OF_DBS + 1):
    db_url = DATABASE_URL_TEMPLATE.format(user=i, password=i, index=i)
    engine = create_engine(db_url)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    engines.append(engine)
    SessionLocals.append(session_local)

@contextmanager
def get_db(index: int):
    db = SessionLocals[index]()
    try:
        yield db
    finally:
        db.close()