from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime

# Sample charger details
charger_details = {
    "vendor": "RealChargerVendor",
    "model": "RealModelX",
    "serial_number": "123456789",
    "firmware_version": "v1.0.3"
}

async def ocpp_server(websocket: WebSocket):
    """
    Handles OCPP WebSocket communication with a client.
    """
    await websocket.accept()
    print("[SERVER] Client connected")

    try:
        while True:
            # Receive incoming OCPP message
            message = await websocket.receive_text()
            print(f"[SERVER] Received: {message}")

            # Parse the incoming message as JSON
            try:
                ocpp_message = json.loads(message)
                action = ocpp_message.get("action")
                payload = ocpp_message.get("payload", {})

                # Handle specific OCPP actions
                if action == "BootNotification":
                    print("[SERVER] Handling BootNotification")
                    response = {
                        "action": "BootNotificationResponse",
                        "payload": {
                            "currentTime": datetime.utcnow().isoformat(),
                            "interval": 300,
                            "status": "Accepted",
                        },
                    }
                elif action == "MeterValues":
                    print("[SERVER] Handling MeterValues")
                    response = {
                        "action": "MeterValuesResponse",
                        "payload": {
                            "status": "Accepted"
                        },
                    }
                elif action == "StatusNotification":
                    print("[SERVER] Handling StatusNotification")
                    response = {
                        "action": "StatusNotificationResponse",
                        "payload": {
                            "status": "Accepted"
                        },
                    }
                else:
                    print("[SERVER] Unknown action received")
                    response = {
                        "action": "Error",
                        "payload": {
                            "errorCode": "NotSupported",
                            "errorDescription": f"Action '{action}' is not supported."
                        },
                    }

                # Send the response back to the client
                await websocket.send_text(json.dumps(response))
                print(f"[SERVER] Sent: {response}")

            except json.JSONDecodeError:
                print("[SERVER] Invalid JSON received")
                await websocket.send_text(
                    json.dumps({"error": "Invalid JSON format"})
                )

    except WebSocketDisconnect:
        print("[SERVER] Client disconnected")
