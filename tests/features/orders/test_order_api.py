from fastapi.testclient import TestClient

from main import create_app

def test_order_health_check() -> None:
    
    client = TestClient(create_app())

    response = client.get("/orders/health")

    assert response.status_code == 200


def test_order_get_orders() -> None:
    client = TestClient(create_app())

    response = client.get("/orders/get")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0