from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import Base, engine
from app.services import register_service
from app.controllers import collect_cash, get_transactions, health, index, TransactionRequest, get_db


app = FastAPI()


@app.post("/collect_cash")
def collect_cash_route(transaction_request: TransactionRequest, db: Session = Depends(get_db)):
    return collect_cash(transaction_request, db)

@app.get("/transactions")
def get_transactions_route(db: Session = Depends(get_db)):
    return get_transactions(db)

@app.get("/health")
def health_route():
    return health()

@app.get("/")
def index_route():
    return index()


Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    register_service()
