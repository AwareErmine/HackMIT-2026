import socket
import json

IP_ADDR  ="127.0.0.1"
PORT = 5005

def server() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # TODO: add client that listens for audio data to send?
    obj = {"hello": "world"}
    print("SERVER: SENDING MESSAGE")
    sock.sendto(json.dumps(obj).encode('utf-8'), (IP_ADDR, PORT))

    sock.close()

