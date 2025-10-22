import socket
import logging

SERVER_HOST = "127.0.0.1"
PORT = 2222

MAX_BYTES_REPONSE = 65536
ENCODING = "utf-8"
STOP_WORD = "stop"
PROMPT = "> "

class Session():
    
    id_counter = 1

    def __init__(self, logger, socket_object):
        connection, _ = socket_object.accept()

        self.id = Session.id_counter
        Session.id_counter += 1

        self.connection = connection
        self.client_host = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)

        print_log(logger, f"Client connected: {self.client_host} (Session ID: {self.id})", self)


    def send_new_message(self, logger):
        # Sending the message to the client.
        message = input(PROMPT)

        if message:
            self.connection.send(bytes(message, encoding=ENCODING))
            print_log(logger, f"Sent: {message}", self, False)

        return message


    def get_output(self, logger):
        # Get the response from the client (stdout and stderr), and print it.
        response = self.connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)
        print_log(logger, f"Recived: {response}", self)
        return response
    
    def stop_connection(self, logger):
        self.connection.close()
        print_log(logger, f"Client disconnected: {self.client_host} (Session ID: {self.id})", self)



def create_tcp_socket(logger):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print_log(logger, "Server Started")
    return server_socket


def bind_and_listen(logger, socket_object, server_host, port):
    # Binding the server's host.
    socket_object.bind((server_host, port))

    # Listen to client.
    print_log(logger, "Waiting for connections...")
    socket_object.listen()

  

def print_log(logger, log, session=None, printable=True):
    if printable: print(log) 
    if session:
        logger.info(log, extra={"address": session.client_host, "session_id": session.id})
    else:
        logger.info(log, extra={"address": SERVER_HOST, "session_id": "server"})


def main():

    #  Create logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="server.log", format="%(asctime)s - %(address)s [%(session_id)s] - %(message)s", level=logging.INFO)

    

    with create_tcp_socket(logger) as server_socket:

        bind_and_listen(logger, server_socket, SERVER_HOST, PORT)

        session1 = Session(logger, server_socket)

        with session1.connection:

            # Running until "stop" is sent.
            while True:
                message = session1.send_new_message(logger)

                # If the message is stop, stop the session.
                if message == STOP_WORD:
                    break
                elif message:
                    session1.get_output(logger)
                    
            session1.stop_connection(logger)

    print("Done")



if __name__ == "__main__":
    main()