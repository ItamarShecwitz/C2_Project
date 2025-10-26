import socket
import subprocess
import sys

import ssl
import base64
import hmac
import hashlib
import os

# env
HMAC_KEY_PARAMETER = os.environ.get("HMAC", "")
CLIENT_HOST = os.environ.get("CLIENT_HOST", "127.0.0.1")

# Global Constants

MAX_BYTES_REPONSE = 65536
ENCODING = 'utf-8'
STOP_WORD = "stop"

HOST_INDEX = 1
PORT_INDEX = 2

EXPECTED_ARGS = 3  # script name + 2 args

MIN_PORT = 1
MAX_PORT = 65535

CONNECTIONS_TIMEOUT = 1.0

HMAC_KEY_FILE_NAME = "default_hmac.key"

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

    client_socket = make_socket_tls(client_socket, server_host)

    try:
        client_socket.connect((server_host, port))
    except:
        print("Error: No server found")
        exit()
    print(f"Connecting to {server_host} {port}")

    # Creating and sending a registration request to the server (The request is the client's host).
    registration_request = client_host

    if registration_request:
        client_socket.send(bytes(registration_request, encoding=ENCODING))
    else:
        client_socket.send(bytes("None", encoding=ENCODING))

    return client_socket


def get_hmac(file_name):
    # Get the hmac key from a file.

    with open(file_name, "r") as f:
        key_b64 = f.read().strip()
        hmac_key = base64.b64decode(key_b64)
        return hmac_key


def is_authorized_message(message, signature, hmac_key):
    # Check if the current message is signed with the corresponding hmac key. 

    expected_signature = hmac.new(hmac_key, message.encode(ENCODING), hashlib.sha256).hexdigest().strip()
    if hmac.compare_digest(expected_signature, signature): return True
    else: return False


def make_socket_tls(client_socket, server_host):
    # Wrap with SSL context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # because it's self-signed
    context.verify_mode = ssl.CERT_NONE
    secure_socket = context.wrap_socket(client_socket, server_hostname=server_host)
    return secure_socket


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
        socket_object.sendall(bytes("Empty message", encoding=ENCODING))
        return None


def get_response(socket_object, hmac_key):
    # Wait, and recieve the message from the server.
    message = socket_object.recv(MAX_BYTES_REPONSE).decode(ENCODING)
    signature = socket_object.recv(MAX_BYTES_REPONSE).decode(ENCODING)
    
    if not is_authorized_message(message, signature, hmac_key):
        return None
    return message


def send_response(socket_object, result, hmac_key):
    # Sent the stdout and stderr of the command back to ther server.
    
    response = (result.stdout + result.stderr).strip() if result.stdout or result.stderr else " "
    socket_object.send(bytes(response, encoding=ENCODING))

    signature = hmac.new(hmac_key, response.encode(ENCODING), hashlib.sha256).hexdigest()
    socket_object.send(bytes(signature, encoding=ENCODING))


def stop_connection(socket_object):
    # Close the connection of a session.

    socket_object.close()
    print("Disconnecting from server")

def main():

    server_host, port = get_arguments()
    hmac_key = HMAC_KEY_PARAMETER if HMAC_KEY_PARAMETER != "" else get_hmac(HMAC_KEY_FILE_NAME)

    client_socket = create_session(CLIENT_HOST, server_host, port)
    client_socket.settimeout(CONNECTIONS_TIMEOUT)
    with client_socket:
        try:
            # Running until "stop" is sent from the server.
            while True:
                try:

                    message = get_response(client_socket, hmac_key)

                    if not message:
                        send_response(client_socket, None, hmac_key)
                        continue

                    # If the message is stop, stop the session.
                    if message == STOP_WORD: break
                    
                    result = execute_message(client_socket, message)

                    send_response(client_socket, result, hmac_key)
                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            pass
    
    stop_connection(client_socket)

if __name__ == "__main__":
    main()