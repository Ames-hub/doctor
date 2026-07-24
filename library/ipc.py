import logging
import asyncio
import json
import os

SOCKET_PATH = "/run/doctor/doctor.sock"

async def _handle_client(reader, writer, scan_callback):
    try:
        data = await reader.read(1024)
        command = data.decode().strip()

        if command == "scannow":
            logging.info("Received 'scannow' request over IPC socket.")
            result = await scan_callback()
            response = json.dumps(result)
        else:
            response = json.dumps({"error": f"Unknown command '{command}'"})

        writer.write(response.encode())
        await writer.drain()
    except Exception as err:
        logging.error("Error handling IPC client connection", exc_info=err)
    finally:
        writer.close()
        await writer.wait_closed()

async def run_server(scan_callback):
    """
    Starts a Unix domain socket server that listens for CLI commands
    (e.g. 'scannow') and dispatches them to the running daemon.
    """
    socket_dir = os.path.dirname(SOCKET_PATH)
    os.makedirs(socket_dir, exist_ok=True)

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = await asyncio.start_unix_server(
        lambda r, w: _handle_client(r, w, scan_callback),
        path=SOCKET_PATH
    )

    # Daemon runs as root; non-root users need to reach the socket to run --scannow.
    os.chmod(SOCKET_PATH, 0o666)

    logging.info(f"IPC socket server listening at {SOCKET_PATH}")

    async with server:
        await server.serve_forever()


async def send_scannow_request():
    """
    Client-side: connects to the running daemon's socket, sends a
    'scannow' command, and returns the parsed JSON response.
    Raises ConnectionRefusedError / FileNotFoundError if the daemon isn't running.
    """
    reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
    try:
        writer.write(b"scannow")
        await writer.drain()
        writer.write_eof()

        data = await reader.read(65536)
        return json.loads(data.decode())
    finally:
        writer.close()
        await writer.wait_closed()