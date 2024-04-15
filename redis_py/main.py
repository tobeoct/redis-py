import socket
import threading

from redis_py.processor import Processor
from redis_py.resp.handler import RespProtocol


def handle_client_connection(client_socket):
    """
    Deserializes a message from a resp protocol to a format that can be understood
    by the system

    Args:
        resp_string: message

    Returns:
        A tuple of 3 (prefix,length,data)
    """
    while True:
        command = client_socket.recv(1024).decode()  # Read data from the client
        if not command:
            break  # Break the loop if the client has disconnected
        print("Command:", repr(command))
        result =RespProtocol(Processor).handle_request(command)
        client_socket.send(result.encode())  # Send back the result
    client_socket.close()  # Close the connection


def start_server(host="127.0.0.1", port=6379):
    """
    Deserializes a message from a resp protocol to a format that can be understood
    by the system

    Args:
        resp_string: message

    Returns:
        A tuple of 3 (prefix,length,data)
    """
    start = True
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
    server.bind((host, port))  # Bind the socket to our host and port
    server.listen(5)  # Start listening for connections
    print(f"Server started on {host}:{port}")
    while start:
        client_sock, address = server.accept()  # Accept a new connection
        print(f"Accepted connection from {address[0]}:{address[1]}")
        client_handler = threading.Thread(
            target=handle_client_connection, args=(client_sock,)
        )
        client_handler.start()  # Start the client handler thread
