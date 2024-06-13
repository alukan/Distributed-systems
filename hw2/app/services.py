import httpx
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker

PROCESS_URL = os.getenv("PROCESS_URL")

breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(httpx.RequestError)
)
def call_process_service(payload):
    print('Calling process service')
    response = httpx.post(
        f'{PROCESS_URL}/v1/wallet/transaction',
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response

def register_service():
    load_balancer_url = "http://load_balancer:8000/register"
    service_name = os.getenv('SERVICE_NAME')
    instance_url = f"http://{service_name}:8000"

    external_url = f"http://localhost:{os.getenv('SERVICE_PORT')}"

    while True:
        try:
            response = httpx.post(load_balancer_url, json={"url": instance_url, "external_url": external_url})
            if response.status_code == 200:
                print("Service registered successfully")
                break
        except httpx.RequestError as e:
            print(f"Failed to register service: {e}")
        time.sleep(5)
