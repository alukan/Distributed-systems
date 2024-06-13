from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models import Transaction
from app.services import call_process_service, breaker
import httpx 

class TransactionRequest(BaseModel):
    courier_id: int
    amount: float

def collect_cash(transaction_request: TransactionRequest, db: Session = Depends(get_db)):
    try:
        transaction = Transaction(
            courier_id=transaction_request.courier_id,
            amount=transaction_request.amount,
            status="pending"
        )
        db.add(transaction)

        payload = {
            'amount': transaction_request.amount,
            'currency': 'USD',
            'description': f'Cash collection from courier {transaction_request.courier_id}',
            'userId': str(transaction_request.courier_id)
        }

        try:
            response = breaker.call(call_process_service, payload)
            if response.status_code == 200:
                transaction.status = 'processed'
                db.commit()
            else:
                transaction.status = 'failed'
                db.rollback()
                
        except httpx.RequestError as e:
            transaction.status = 'timeout error'
            print(e)
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

def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions

def health():
    return {"status": "healthy"}

def index():
    return "Welcome to API"
