import socket


SERVER_ADDRESS = ("127.0.0.1", 8080)
BUFFER_SIZE = 1024 * 10


class Client:
    def __init__(self):
        self.server_address = SERVER_ADDRESS

    def send_message(self, message):
        print(f"📩 Sending message: {message}")
        message = message.encode("utf-8")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        server.sendto(message, self.server_address)
        response = server.recvfrom(BUFFER_SIZE)
        message = response[0].decode("utf-8")
        print(f"📨 Received response: {message}")

    def send_message_on_tcp(self, message, port=8080):
        print(f"📩 Sending message with TCP CONNECTION: {message}")
        message = message.encode("utf-8")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        server.connect((self.server_address[0], port))
        server.send(message)
        response = server.recv(BUFFER_SIZE)
        message = response.decode("utf-8")
        print(f"📨 Received response: {message}")
