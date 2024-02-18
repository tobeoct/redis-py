from .protocol import Protocol;
from .commands import Commands;
from .persistence import db;
import socket;
import threading;

start = False
class Network:
    def __init__(self):
        self.protocolHandler = Protocol(Commands(db))
    def handle_client_connection(self,client_socket):
        while True:
            command = client_socket.recv(1024).decode()  # Read data from the client
            if not command:
                break  # Break the loop if the client has disconnected
            result =self.protocolHandler.handle(command)  # Process the command
            client_socket.send(result.encode())  # Send back the result
        client_socket.close()  # Close the connection

    def start_server(self,host='127.0.0.1', port=6379):
        start=True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new socket
        server.bind((host, port))  # Bind the socket to our host and port
        server.listen(5)  # Start listening for connections
        print(f'Server started on {host}:{port}')
        while start:
            client_sock, address = server.accept()  # Accept a new connection
            print(f'Accepted connection from {address[0]}:{address[1]}')
            client_handler = threading.Thread(
                target=self.handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()  # Start the client handler thread
    def stop_server(self):
        start = False