import socket
import threading

HOST = "127.0.0.1"
PORT = 45678
BUFFER_SIZE = 1024


def try_activate_existing() -> bool:
    """Try to send a show command to an existing instance.

    Returns True if an existing instance was found and activated.
    Returns False if no existing instance was found.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(1.0)
            client.connect((HOST, PORT))
            client.sendall(b"show")
            return True
    except (ConnectionRefusedError, OSError):
        return False


def start_server(on_show: callable) -> socket.socket | None:
    """Start a server that listens for show commands from other instances.

    Returns the server socket if successful, None if another instance is already running.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(1)
    except OSError:
        server.close()
        return None

    def listen() -> None:
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(BUFFER_SIZE)
                if data == b"show":
                    on_show()
                conn.close()
            except OSError:
                break

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    return server
