import socket

QUEUE_AVAILABLE_SERVERS = []
QUEUE_UNAVAILABLE_SERVERS = []

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, num_threads: int, port: int = 8080):
        self.host = "127.0.0.1"
        self.port = port
        self.num_threads = num_threads

    def run(self):
        """Run the server."""
        print(f"🚀 Starting server on port {self.port}...")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        server.bind((self.host, self.port))
        while True:
            print("🚀 Waiting for connections...")
            bytes_address_pair = server.recvfrom(BUFFER_SIZE)

            print("🚀 Received connection...", bytes_address_pair)
            message = bytes_address_pair[0]

            address = bytes_address_pair[1]

            client_message = "Message from Client:{}".format(message)
            client_ip = "Client IP Address:{}".format(address)

            print(client_message)
            print(client_ip)

            response = "Hello from Server".encode("utf-8")
            server.sendto(response, address)
