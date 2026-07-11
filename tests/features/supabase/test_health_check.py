import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import AsyncClient, ASGITransport

# Import the FastAPI instance from your main entry point
from main import app
from src.core.supabase_connection import get_db

@pytest.fixture
def anyio_backend():
    """Configures the asynchronous execution backend matrix for pytest."""
    return "asyncio"


@pytest.fixture(autouse=True)
def override_supabase_dependency():
    async def fake_get_db():
        return object()

    app.dependency_overrides[get_db] = fake_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
@patch("src.features.supabase.health.endpoint.verify_supabase_connectivity", new_callable=AsyncMock)
async def test_health_check_success(mock_verify):
    """
    Verifies that when Supabase responds normally, the /health endpoint
    returns a 200 OK status along with structured health parameters.
    """
    # 1. Arrange: Configure the mock to simulate a successful connection with a latency of 15.4ms
    mock_verify.return_value = (True, 15.4)

    # 2. Act: Execute an internal HTTP call against the FastAPI instance using AsyncClient
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/supabase/health")

    # 3. Assert: Validate that outbound payload match specifications perfectly
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert data["latency_ms"] == 15.4
    
    # Ensure the handler actually called the underlying connection verifier
    mock_verify.assert_called_once()


@pytest.mark.anyio
@patch("src.features.supabase.health.endpoint.verify_supabase_connectivity", new_callable=AsyncMock)
async def test_health_check_database_offline(mock_verify):
    """
    Verifies that if Supabase is offline or unreachable, the CQRS handler
    correctly intercepts the error and returns a 503 Service Unavailable error.
    """
    # 1. Arrange: Configure the mock to simulate a database query timeout/failure
    mock_verify.return_value = (False, None)

    # 2. Act: Execute the health check endpoint request
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/supabase/health")

    # 3. Assert: Validate that failure codes match production infrastructure specifications
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    
    data = response.json()
    # FastAPI nests details inside a detail key object for exceptions
    assert data["detail"]["status"] == "unhealthy"
    assert data["detail"]["database_connected"] is False
    assert data["detail"]["error"] is not None


@pytest.mark.anyio
@patch("src.features.supabase.health.endpoint.verify_supabase_connectivity", new_callable=AsyncMock)
async def test_health_check_exception_handling(mock_verify):
    """
    Verifies that if the connectivity checker throws an unhandled system exception,
    the CQRS execution handler intercepts it gracefully without crashing the server.
    """
    # 1. Arrange: Force an unhandled operational exception inside the dependency service
    mock_verify.side_effect = Exception("Connection refused by remote host protocol engine.")

    # 2. Act: Execute request
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/supabase/health")

    # 3. Assert: Ensure the server intercepts the raw exception and bubbles a 503 error
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()
    assert "Connection refused" in data["detail"]["error"]