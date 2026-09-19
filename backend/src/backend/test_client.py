import socket
import json

HOST = "127.0.0.1"
PORT = 5005

def test_client() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        while True:
            data, _addr = sock.recvfrom(4096)
            print("CLIENT", json.loads(data))
            if not data: break

test_client()