import socket

HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.connect((HOST, PORT))
    while True:
        message = input()
        s.sendall(bytes(message, encoding='utf-8'))
        if message == "stop":
            break

print("Done")