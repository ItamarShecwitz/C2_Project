import socket
import logging

SERVER_HOST = "127.0.0.1"
PORT = 2222

MAX_BYTES_REPONSE = 65536
ENCODING = 'utf-8'
STOP_WORD = "stop"

class Session():
    
    id_counter = 1

    def __init__(self, socket_object):
        connection, _ = socket_object.accept()

        self.id = Session.id_counter
        Session.id_counter += 1

        self.connection = connection
        self.client_host = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)


    def send_new_message(self):
        # Sending the message to the client.
        message = input()

        if message:
            self.connection.send(bytes(message, encoding=ENCODING))

        return message


    def get_output(self):
        # Get the response from the client (stdout and stderr), and print it.
        return self.connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)


def create_tcp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def bind_and_listen(socket_object, server_host, port):
    # Binding the server's host.
    socket_object.bind((server_host, port))

    # Establish new connection.
    socket_object.listen()

  

def print_logging(logger, log, session):
    logger.info(log, extra={'address': session.client_host, 'session_id': session.id})


def main():

    #  Create logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='server.log', format='%(asctime)s - %(address)s (%(session_id)s) - %(message)s', level=logging.INFO)



    with create_tcp_socket() as server_socket:

        bind_and_listen(server_socket, SERVER_HOST, PORT)

        session1 = Session(server_socket)

        with session1.connection:

            # Running until "stop" is sent.
            while True:
                message = session1.send_new_message()

                # If the message is stop, stop the session.
                if message == STOP_WORD:
                    break
                elif message:
                    print(session1.get_output())
                    

    print("Done")



if __name__ == "__main__":
    main()