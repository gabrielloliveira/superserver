import random
import socket
import time

SERVER_ADDRESS = ("superserver", 8080)
BUFFER_SIZE = 1024 * 10


class Client:
    def __init__(self):
        self.server_address = SERVER_ADDRESS

    def send_message(self, message):
        print(f"📩 Sending message: {message}")
        start_time = time.time()
        message = message.encode("utf-8")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        server.settimeout(5)
        server.sendto(message, self.server_address)
        response = server.recvfrom(BUFFER_SIZE)
        message = response[0].decode("utf-8")
        final_time = time.time() - start_time
        print(f"📨 Received response: {message} in {final_time} seconds")

    def send_message_on_tcp(self, message, port=8080):
        print(f"📩 Sending message with TCP CONNECTION: {message}")
        message = message.encode("utf-8")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        server.connect((self.server_address[0], port))
        server.send(message)
        response = server.recv(BUFFER_SIZE)
        message = response.decode("utf-8")
        print(f"📨 Received response: {message}")

    def gerate_random_message(self):
        l_c = random.randint(5, 20)
        num_1 = random.randint(0, 9)
        num_2 = random.randint(0, 9)
        matriz_1 = [[num_1] * l_c, [num_2] * l_c] * l_c

        num_1 = random.randint(0, 9)
        num_2 = random.randint(0, 9)
        matriz_2 = [[num_1] * l_c, [num_2] * l_c] * l_c

        message = f"{matriz_1} x {matriz_2}"
        return message
