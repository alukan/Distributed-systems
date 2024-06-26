FROM python:3.9-slim

WORKDIR /outbox_processor

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "outbox_processor.py"]
