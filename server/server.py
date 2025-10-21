import socket

SERVER_HOST = "127.0.0.1"
PORT = 2222

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Binding the server's host.
    s.bind((SERVER_HOST, PORT))

    # Establish new connection.
    s.listen()
    connection, address = s.accept()
    client_host = connection.recv(1024).decode('utf-8')

    with connection:
        while True:
            message = input()
            connection.send(bytes(message, encoding='utf-8'))
            if message == "stop":
                break
            response = connection.recv(1024).decode('utf-8')
            print(f"Response: {response}")

print("Done")