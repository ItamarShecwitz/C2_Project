import socket

HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    connection, address = s.accept()
    with connection:
        while True:
            message = connection.recv(1024).decode('utf-8')
            if message == "stop":
                break
            if message:
                print(f"Got message from {address[0]} on port {address[1]}\nMessage: \"{message}\"")
            else:
                print(f"Error with recieving the data from {address}")
print("Done")