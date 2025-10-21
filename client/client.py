import socket

HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.connect((HOST, PORT))
    registration_request = HOST
    s.sendall(bytes(registration_request, encoding='utf-8'))

    while True:
        message = s.recv(1024).decode('utf-8')
        if message == "stop":
            break
        if message:
            print(f"Execute this: \"{message}\"")
        else:
            print(f"Error with recieving command")

print("Done")