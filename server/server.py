import os
import random
import socket
import threading
from ast import literal_eval
from functools import reduce

import numpy as np

HOST = "127.0.0.1"
PORT = 8080

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, num_threads: int, is_subprocess: bool = False):
        self.host = HOST
        self.is_subprocess = is_subprocess
        self.select_type_serve()
        self.num_threads = num_threads
        self.threads = 0
        self.QUEUE_AVAILABLE_SERVERS = []
        self.QUEUE_UNAVAILABLE_SERVERS = []

    def select_type_serve(self):
        """Select type of serve."""
        if not self.is_subprocess:
            self.port = PORT
            self.sock = self.create_socket_upd()
        else:
            self.port = self.get_port()
            self.sock = self.create_socket_tcp()

    def create_socket_upd(self):
        """Create a socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        return sock

    def create_socket_tcp(self):
        """Create a socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        return sock

    def close(self):
        """Close the server."""
        self.sock.close()

    def run(self):
        """Run the server."""
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.num_threads}...")
        if not self.is_subprocess:
            while True:
                self.listen_udp()
        else:
            self.listen_tcp()

    def listen_udp(self):
        """Listen for connections."""
        print("🚀 Waiting for connections...")
        message, client_address = self.sock.recvfrom(BUFFER_SIZE)
        print("🚀 Received connection...", client_address)
        self.handle_request(message, client_address)

    def listen_tcp(self):
        """Listen for connections."""
        pass

    def get_port(self):
        """Get a port."""
        port = random.randint(8000, 65535)
        if self.test_port(random.randint(8000, 65535)):
            return port
        else:
            return self.get_port()

    def test_port(self, port):
        """Test if port is available."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        return s.connect_ex((self.host, self.port)) == 0

    def handle_request(self, message, client_address):
        """Handle a request."""
        if self.threads < self.num_threads:
            self.thread_request(message, client_address)
        else:
            if not self.is_subprocess:
                self.subprocess_request(message, client_address)

    @staticmethod
    def matrices(message):
        """Get matrices from message."""
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        matrices = message.lower().split("x")
        matrices = [literal_eval(m.strip()) for m in matrices]
        return matrices

    @staticmethod
    def calculate_product(matrices):
        """Calculate product of matrices."""
        return reduce(np.dot, matrices)

    def send_response_thread(self, message, client_address, from_thread=False):
        """Send a response to the client."""
        # TODO: Calculate product from matrix

        matrices = self.matrices(message)
        product = self.calculate_product(matrices)

        response = str(product).encode("utf-8")
        self.sock.sendto(response, client_address)
        if from_thread:
            self.threads -= 1

    def thread_request(self, message, client_address):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response_thread, args=(message, client_address), kwargs={"from_thread": True})
        t.start()
        self.threads += 1

    def create_subprocess(self):
        """Create a subprocess."""
        os.system("python3 -m server True")

    def info_subprocess(self):
        """Listen for info."""

        process = {
            "subprocess": info["port"],
            "performance_rate": 0,
            "status": "available",
            "thread_total": info["threads"],
            "thread_used": 0,
        }

        self.QUEUE_AVAILABLE_SERVERS.append(process)
        self.QUEUE_AVAILABLE_SERVERS = sorted(self.QUEUE_AVAILABLE_SERVERS, key=lambda row: row["performance_rate"], reverse=1)

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        # TODO: Send request to available subprocess or create a new subprocess
        if self.QUEUE_AVAILABLE_SERVERS == []:
            process = self.create_subprocess()
            return self.subprocess_request()

        process = self.use(self.QUEUE_AVAILABLE_SERVERS[0])
        if process.status == "unavailable":
            self.QUEUE_AVAILABLE_SERVERS.remove(process)
            self.QUEUE_UNAVAILABLE_SERVERS.append(process)
            return self.subprocess_request(message, client_address)
            """ 
            Chamada Recursiva para evitar alteração na lista de processos disponíveis enquanto aconteça interação pelo for
            """

        t = threading.Thread(target=self.send_reponse_process, args=(process, message, client_address), kwargs={})
        t.start()

        raise NotImplementedError("Subprocess not implemented yet.")
