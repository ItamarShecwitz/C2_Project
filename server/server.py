import socket
import logging

SERVER_HOST = "127.0.0.1"
PORT = 2222

MAX_BYTES_REPONSE = 65536
ENCODING = 'utf-8'
STOP_WORD = "stop"


def create_tcp_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def bind_and_listen(socket_object, server_host, port):
    # Binding the server's host.
    socket_object.bind((server_host, port))

    # Establish new connection.
    socket_object.listen()


def create_session_server(socket_object):
    connection, address = socket_object.accept()
    client_host = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)
    return (connection, address, client_host)

def send_new_message(connection):
    # Sending the message to the client.
    message = input()

    if message:
        connection.send(bytes(message, encoding=ENCODING))

    return message


def get_output(connection):
    # Get the response from the client (stdout and stderr), and print it.
    response = connection.recv(MAX_BYTES_REPONSE).decode(ENCODING)
    print(response)


def main():

    #  Create logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s - Session: %(address)s (%(session)s) - %(message)s', level=logging.INFO)



    with create_tcp_socket() as s:

        bind_and_listen(s, SERVER_HOST, PORT)

        connection, address, client_host = create_session_server(s)
        
        with connection:

            # Running until "stop" is sent.
            while True:
                logger.info("Now getting commands...", extra={'address': client_host, 'session': address[1]})
                message = send_new_message(connection)

                # If the message is stop, stop the session.
                if message == STOP_WORD:
                    break
                elif message:
                    get_output(connection)

    print("Done")



if __name__ == "__main__":
    main()