from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import Base, engine_1, engine_2, get_db
from services import register_service
from controllers import collect_cash, get_transactions, health, index, TransactionRequest
from contextlib import AsyncExitStack

app = FastAPI()

async def get_db_for_transaction(transaction_request: TransactionRequest):
    async with AsyncExitStack() as stack:
        db = stack.enter_context(get_db(transaction_request.courier_id))
        yield db

async def get_db_for_courier(courier_id: int):
    async with AsyncExitStack() as stack:
        db = stack.enter_context(get_db(courier_id))
        yield db

@app.post("/collect_cash")
async def collect_cash_route(transaction_request: TransactionRequest, db: Session = Depends(get_db_for_transaction)):
    return collect_cash(transaction_request, db)

@app.get("/transactions")
async def get_transactions_route(courier_id: int, db: Session = Depends(get_db_for_courier)):
    return get_transactions(db)

@app.get("/health")
async def health_route():
    return health()

@app.get("/")
async def index_route():
    return index()

try:
    Base.metadata.create_all(bind=engine_1)
    Base.metadata.create_all(bind=engine_2)
except:
    pass

@app.on_event("startup")
async def startup_event():
    register_service()
