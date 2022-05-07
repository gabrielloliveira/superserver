import socket
import threading

HOST = "127.0.0.1"
PORT = 8080
QUEUE_AVAILABLE_SERVERS = []
QUEUE_UNAVAILABLE_SERVERS = []

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, num_threads: int, port: int = PORT, is_subprocess: bool = False):
        self.host = HOST
        self.port = port
        self.num_threads = num_threads
        self.sock = self.create_socket()
        self.threads = 0
        self.is_subprocess = is_subprocess

    def create_socket(self):
        """Create a socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        return sock

    def run(self):
        """Run the server."""
        self.listen()

    def listen(self):
        """Listen for connections."""
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.num_threads}...")
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

    def send_response(self, message, client_address, from_thread=False):
        """Send a response to the client."""
        # TODO: Calculate product from matrix
        response = "Hello from Server".encode("utf-8")
        self.sock.sendto(response, client_address)
        if from_thread:
            self.threads -= 1

    def thread_request(self, message, client_address):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response, args=(message, client_address), kwargs={"from_thread": True})
        t.start()
        self.threads += 1

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        # TODO: Send request to available subprocess or create a new subprocess
        raise NotImplementedError("Subprocess not implemented yet.")
