import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import os

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return "Welcome to API"


DATABASE_URL = os.getenv("DATABASE_URL")
PROCESS_URL = os.getenv("PROCESS_URL")


max_retries = 10
for attempt in range(max_retries):
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()

        class Transaction(Base):
            __tablename__ = "transactions"
            id = Column(Integer, primary_key=True, index=True)
            courier_id = Column(Integer, nullable=False)
            amount = Column(Float, nullable=False)
            status = Column(String(50), nullable=False)

        Base.metadata.create_all(bind=engine)
        print("Database connection established")
        break
    except Exception as e:
        print(f"Database connection failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(10)
        else:
            raise Exception("Database connection could not be established after multiple attempts")


class TransactionRequest(BaseModel):
    courier_id: int
    amount: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/collect_cash")
def collect_cash(transaction_request: TransactionRequest, db: Session = Depends(get_db)):
    try:
        transaction = Transaction(
            courier_id=transaction_request.courier_id,
            amount=transaction_request.amount,
            status="pending"
        )
        db.add(transaction)

        try:
            response = requests.post(f'{PROCESS_URL}/v1/wallet/transaction', json={
                'amount': transaction_request.amount,
                'currency': 'USD',
                'description': f'Cash collection from courier {transaction_request.courier_id}',
                'userId': str(transaction_request.courier_id)
            })
            if response.status_code == 200:
                transaction.status = 'processed'
                db.commit()
            else:
                transaction.status = 'failed'
                db.rollback()
        except Exception as e:
            transaction.status = 'error'
            print(e)
            db.rollback()

        db.commit()
        return {"transaction_id": transaction.id, "status": transaction.status}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions
