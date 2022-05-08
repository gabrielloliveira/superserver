import socket
import subprocess
import threading

from server import BUFFER_SIZE
from server.base import BaseServer
from server.helpers import calculate_product, matrices_from_message


class Server(BaseServer):
    def __init__(self, **kwargs):
        """Initialize the server."""
        super().__init__(**kwargs)
        self.queue_available_servers = []
        self.queue_unavailable_servers = []

    def run(self):
        """Run the server."""
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.max_threads}...")
        self.listen()

    def create_socket(self):
        """Create a UDP socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        return sock

    def listen(self):
        """Listen for connections."""
        while True:
            print("🚀 Waiting for connections...")
            message, client_address = self.sock.recvfrom(BUFFER_SIZE)
            print("🚀 Received connection...", client_address)
            self.handle_request(message, client_address)

    def handle_request(self, message, client_address):
        """Handle a request."""
        if self.threads < self.max_threads:
            self.thread_request(message, client_address)
        else:
            self.subprocess_request(message, client_address)

    def send_response_thread(self, message, client_address, from_thread=False):
        """Send a response to the client."""

        print(f"📩 Received {message} ...")
        print("🚀 Sending response...")

        try:
            matrices = matrices_from_message(message)
            product = calculate_product(matrices)
        except ValueError as e:
            product = f"The matrices is not valid."

        response = str(product).encode("utf-8")
        self.sock.sendto(response, client_address)
        if from_thread:
            self.threads -= 1

    def thread_request(self, message, client_address):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response_thread, args=(message, client_address), kwargs={"from_thread": True})
        t.start()
        self.threads += 1

    def insert_partner_in_queue(self, port, threads):
        """Insert partner in queue."""
        raise NotImplementedError

    @staticmethod
    def create_partner():
        """Create a subprocess."""
        subprocess.run(["python", "-m", "server", "--partner"])

    def available_partner(self):
        """Get available partner."""
        if not self.queue_available_servers:
            self.create_partner()

        # Wait for partner ready and register itself
        len_available_partner = 0
        while len_available_partner == 0:
            len_available_partner = len(self.queue_available_servers)
        return self.queue_available_servers.pop(0)

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        available_server = self.available_partner()
        self.queue_unavailable_servers.append(available_server)

        response = self.request_to_partner(available_server, message)
        self.sock.sendto(response, client_address)

    def request_to_partner(self, available_server, message):
        """Send request to partner."""
        port = available_server["port"]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, port))
        s.send(message)
        response = s.recv(BUFFER_SIZE)
        s.close()
        return response
