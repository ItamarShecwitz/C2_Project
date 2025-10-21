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

        # Running until "stop" is sent.
        while True:

            # Sending the message to the client.
            message = input()
            
            if message:
                connection.send(bytes(message, encoding='utf-8'))

                # If the message is stop, stop the session.
                if message == "stop":
                    break

                # Get the response from the client (stdout and stderr), and print it.
                response = connection.recv(1024).decode('utf-8')
                print(response)

print("Done")