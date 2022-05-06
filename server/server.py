import socket
import threading

HOST = "127.0.0.1"
PORT = 8080
QUEUE_AVAILABLE_SERVERS = []
QUEUE_UNAVAILABLE_SERVERS = []

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, num_threads: int, port: int = PORT):
        self.host = HOST
        self.port = port
        self.num_threads = num_threads
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.threads = 0

    def run(self):
        """Run the server."""
        self.listen()

    def listen(self):
        """Listen for connections."""
        print(f"🚀 Starting server on port {self.port}...")
        while True:
            print("🚀 Waiting for connections...")
            message, client_address = self.sock.recvfrom(BUFFER_SIZE)
            print("🚀 Received connection...", client_address)
            self.handle_request(message, client_address)

    def handle_request(self, message, client_address):
        """Handle a request."""
        if self.threads < self.num_threads:
            self.thread_request(message, client_address)
        else:
            self.subprocess_request(message, client_address)

    def send_response(self, message, client_address):
        """Send a response to the client."""
        response = "Hello from Server".encode("utf-8")
        self.sock.sendto(response, client_address)

    def thread_request(self, message, client_address):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response, args=(message, client_address))
        t.start()
        self.threads += 1

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        # TODO: Send request to available subprocess or create a new subprocess
        pass
