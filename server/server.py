import socket

SERVER_HOST = "127.0.0.1"
PORT = 2222

MAX_BYTES_REPONSE = 1024
ENCODING = 'utf-8'
STOP_WORD = "stop"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Binding the server's host.
    s.bind((SERVER_HOST, PORT))

    # Establish new connection.
    s.listen()
    connection, address = s.accept()
    client_host = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)

    with connection:

        # Running until "stop" is sent.
        while True:

            # Sending the message to the client.
            message = input()

            if message:
                connection.send(bytes(message, encoding=ENCODING))

                # If the message is stop, stop the session.
                if message == STOP_WORD:
                    break

                # Get the response from the client (stdout and stderr), and print it.
                response = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)
                print(response)

print("Done")