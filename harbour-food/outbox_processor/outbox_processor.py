import time
import json
import requests
from sqlalchemy import update
from db import get_db
from models import Outbox
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
NUMBER_OF_DBS = int(os.getenv("NUMBER_OF_DBS", 2))

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

def process_outbox(session):
    try:
        entries = session.query(Outbox).filter(Outbox.processed_at == None).all()
        for entry in entries:
            payload = entry.payload
            message = payload['message']
            if send_telegram_message(message):
                stmt = (
                    update(Outbox)
                    .where(Outbox.id == entry.id)
                    .values(processed_at=time.strftime('%Y-%m-%d %H:%M:%S'))
                )
                session.execute(stmt)
                session.commit()
    except Exception as e:
        print(f"Error processing outbox: {e}")
        session.rollback()

if __name__ == "__main__":
    while True:
        for i in range(NUMBER_OF_DBS):
            with get_db(i) as session:
                process_outbox(session)
        time.sleep(60)