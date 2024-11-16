import pytest
import websockets
import asyncio
from httpx import AsyncClient
from app.main import app
from fastapi.testclient import TestClient
from app.ocpp_server import ocpp_server


@pytest.mark.asyncio
async def test_ocpp_websocket():
    """
    Tests the OCPP WebSocket endpoint for basic connectivity and message handling.
    """
    uri = "ws://localhost:8000/ocpp/1234"

    async with websockets.connect(uri) as websocket:
        # Send a BootNotification test message
        boot_notification_message = {
            "messageTypeId": 2,
            "uniqueId": "1234",
            "action": "BootNotification",
            "payload": {
                "chargePointVendor": "TestVendor",
                "chargePointModel": "TestModel"
            }
        }

        await websocket.send(str(boot_notification_message))  # Convert dict to string for WebSocket sending

        # Receive the response
        response = await websocket.recv()

        # Parse the response and check its validity
        assert "Message received" in response

        # Send another custom message to validate additional behavior
        custom_message = {
            "messageTypeId": 2,
            "uniqueId": "5678",
            "action": "StatusNotification",
            "payload": {
                "connectorId": 1,
                "status": "Available"
            }
        }
        await websocket.send(str(custom_message))

        response = await websocket.recv()

        # Assert the response matches expected behavior
        assert "Message received" in response


@pytest.mark.asyncio
async def test_ocpp_integration():
    """
    Tests the OCPP WebSocket endpoint within the FastAPI app using an AsyncClient.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        uri = "ws://localhost:8000/ocpp/5678"

        # Test WebSocket connection
        async with websockets.connect(uri) as websocket:
            test_message = "Integration Test Message"
            await websocket.send(test_message)
            response = await websocket.recv()

            # Ensure the OCPP server handles the message correctly
            assert response == f"Message received: {test_message}"
