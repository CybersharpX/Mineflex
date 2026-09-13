# Troubleshooting Guide

---

## Common Issues & Resolutions

### 1. Connection Refused / Connection Timed Out
* **Symptom**: `ConnectionError: Failed to connect to localhost:25565`.
* **Resolution**: Ensure the Minecraft server is actively running and accepting connections on the target host and port.

### 2. Kicked During Login / Invalid UUID
* **Symptom**: `ProtocolError: Kicked during login: Invalid username or session`.
* **Resolution**: If the server has `online-mode=true`, connecting with `auth="offline"` will be rejected by the server. Connect to an offline test server or supply valid Microsoft authentication credentials.

### 3. Block Out of Reach
* **Symptom**: `DiggingError: Block at Vec3(...) is out of reach (6.2 > 5.0)`.
* **Resolution**: Minecraft enforces reach limits (~4.5 - 5.0 blocks). Move the bot closer to the block using movement controls before digging.

### 4. Broken Event Listeners
* **Behavior**: If an event listener raises an unhandled exception, Mineflex isolates the failure and logs the traceback without crashing other listeners or the main asyncio event loop. Inspect logger `mineflex.events` for detailed tracebacks.
