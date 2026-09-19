import platform
import socket
import time

print("=== HackMIT! ===")
print("Python backend starting")
print("Machine:", platform.machine())
print("Hostname:", socket.gethostname())

while True:
    print("yay backend alive")
    time.sleep(2)
