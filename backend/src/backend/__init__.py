import os 

UDP_IP = os.getenv("UDP_IP")
UDP_PORT = os.getenv("UDP_PORT")

def main() -> None:
    print("Hello from backend!", UDP_IP, UDP_PORT)
