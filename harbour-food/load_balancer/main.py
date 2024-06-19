from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import threading
import asyncio
from typing import List

app = FastAPI()

class Service(BaseModel):
    url: str
    external_url: str

services = []
lock = threading.Lock()

@app.get("/")
def read_root():
    return {"message": "Redirect Load Balancer"}

@app.post("/register")
def register_service(service: Service):
    with lock:
        if service.url not in [s.url for s in services]:
            services.append(service)
    return {"message": "Service registered successfully"}

@app.get("/services")
def get_services():
    with lock:
        return {"services": services}

@app.get("/redirect{full_path:path}")
def redirect_request(full_path: str, request: Request):
    with lock:
        if not services:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No available services")

        service = services.pop(0)
        services.append(service)
    
    full_url = f"{service.external_url}{full_path}"
    print(f"Redirecting to: {full_url}")
    return RedirectResponse(url=full_url, status_code=307)

async def health_check():
    global services
    while True:
        healthy_services = []
        async with httpx.AsyncClient() as client:
            tasks = [client.get(f"{service.url}/health", timeout=2) for service in services]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for service, result in zip(services, results):
                if isinstance(result, httpx.Response) and result.status_code == 200:
                    healthy_services.append(service)
        with lock:
            services = healthy_services
        await asyncio.sleep(10)

def start_health_check_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(health_check())

threading.Thread(target=start_health_check_loop, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
