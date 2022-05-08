import socket
import subprocess
import threading
import time
from ast import literal_eval

from server import BUFFER_SIZE, SERVER_ADDRESS_TCP
from server.base import BaseServer
from server.helpers import calculate_product, matrices_from_message


class Server(BaseServer):
    def __init__(self, **kwargs):
        """Initialize the server."""
        super().__init__(**kwargs)
        self.sock_partner = self.create_socket_for_partner()
        self.queue_available_servers = []
        self.queue_unavailable_server = []

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

    @staticmethod
    def create_socket_for_partner():
        """Create a TCP socket for the partner."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(SERVER_ADDRESS_TCP)
        sock.listen(1)
        return sock

    def listen(self):
        """Listen for connections."""

        t = threading.Thread(target=self.listener_to_register_partner)
        t.start()

        while True:
            print("🚀 Waiting for connections...")
            message, client_address = self.sock.recvfrom(BUFFER_SIZE)
            print("🚀 Received connection...", client_address)
            self.handle_request(message, client_address)

    def listener_to_register_partner(self):
        """Listen for partner."""
        while True:
            conn, client_address = self.sock_partner.accept()
            print("✅ Received partner solicitation...", client_address)
            message = conn.recv(BUFFER_SIZE)
            message = message.decode("utf-8")
            try:
                self.register_partner(message)
            except Exception as e:
                conn.send(str(e).encode())

    def register_partner(self, message):
        """Listen for TCP connection."""
        print(f"✅ Registered {message} ...")
        message = literal_eval(message)
        self.queue_available_servers.append(message)
        print(f"✅ Queue available servers: {self.queue_available_servers} ...")

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
        subprocess.Popen(["python", "-m", "server", "--partner"])

    def available_partner(self):
        """Get available partner."""
        if not self.queue_available_servers:
            self.create_partner()
            print("🤝 Created a new partner...")

        # Wait for partner ready and register itself
        print("👀 Waiting for available partner...")
        len_available_partner = 0
        while len_available_partner == 0:
            len_available_partner = len(self.queue_available_servers)
        print("🤝 Partner available...")
        return self.queue_available_servers.pop(0)

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        available_server = self.available_partner()

        print(f"📪 Sending {message} to available partner on PORT {available_server['port']} ...")

        t = threading.Thread(target=self.send_subprocess_response, args=(available_server, message, client_address))
        t.start()

    def send_subprocess_response(self, available_server, message, client_address):
        self.queue_unavailable_server.append(available_server)

        start_time = time.time()
        response = self.request_to_partner(available_server, message)
        total_time = time.time() - start_time

        print(f"📩 Sending response to client ...")
        self.sock.sendto(response, client_address)
        self.queue_unavailable_server.remove(available_server)
        performance = self.calculate_performance(message, total_time)
        print(f"📊 Performance of partner {available_server['port']}: {performance} ...")
        self.update_queue_available_servers(available_server, performance)

    def request_to_partner(self, available_server, message):
        """Send request to partner."""
        print(f"📩 Sending message with TCP CONNECTION to partner at port {available_server['port']}")
        if isinstance(message, str):
            message = message.encode("utf-8")
        server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        server.connect((self.host, available_server["port"]))
        server.send(message)
        response = server.recv(BUFFER_SIZE)
        print(f"📨 Received from partner response: {response.decode('utf-8')}")
        return response

    @staticmethod
    def calculate_performance(message, total_time):
        matrices = matrices_from_message(message)
        size_processing = len(matrices[0]) * len(matrices[1][0])
        return total_time / size_processing

    def update_queue_available_servers(self, available_server, performance):
        """Update queue available servers."""
        available_server["performance_rate"] = performance
        self.queue_available_servers.append(available_server)
        print(f"🔁️ Updating queue available servers: {self.queue_available_servers}")
        sorted(self.queue_available_servers, key=lambda row: row["performance_rate"], reverse=True)
        print(f"✅️ Updated queue available servers: {self.queue_available_servers}")
