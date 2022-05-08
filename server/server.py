import socket
import subprocess
import threading

from server.helpers import calculate_product, matrices_from_message

HOST = "127.0.0.1"
PORT = 8080

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, threads: int, partner: bool = False, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.partner = partner
        self.sock = self.create_sock()
        self.num_threads = threads
        self.threads = 0
        self.queue_available_servers = []
        self.queue_unavailable_servers = []

    def close(self):
        """Close the server."""
        self.sock.close()

    def run(self):
        """Run the server."""
        if self.partner:
            print("🚀 Starting server on mode partner...")
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.num_threads}...")
        listen_type_connection = self.listen_udp
        if self.partner:
            listen_type_connection = self.listen_tcp
        listen_type_connection()

    def create_sock(self):
        """Create a socket."""
        if self.partner:
            return self.create_socket_tcp()
        return self.create_socket_udp()

    def create_socket_udp(self):
        """Create a UDP socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        return sock

    def create_socket_tcp(self):
        """Create a TCP socket."""
        self.port = self.available_port()
        print(f"🚀 Port {self.port} is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        return sock

    def available_port(self):
        """Get available port."""
        try:
            s = socket.socket()
            s.bind((self.host, self.port))
            s.close()
            return self.port
        except OSError:
            pass
        initial = 8000
        final = 65535
        for port in range(initial, final):
            try:
                s = socket.socket()
                s.bind((self.host, port))
                s.close()
                return port
            except OSError:
                pass
        raise OSError("All ports from {} to {} are in use. Please close a port.".format(initial, final))

    def listen_udp(self):
        """Listen for connections."""
        while True:
            print("🚀 Waiting for connections...")
            message, client_address = self.sock.recvfrom(BUFFER_SIZE)
            print("🚀 Received connection...", client_address)
            self.handle_request(message, client_address)

    def listen_tcp(self):
        """Listen for connections."""
        if self.partner:
            # TODO: Register the server in the parent server queue
            pass
        print("🚀 Waiting for connections on TYPE MODE TCP...")
        self.sock.listen()
        conn, client_address = self.sock.accept()
        with conn:
            print("🚀 Received connection...", client_address)
            while True:
                message = conn.recv(BUFFER_SIZE)
                if not message:
                    break
                self.handle_request(message, client_address)

    def handle_request(self, message, client_address):
        """Handle a request."""
        if self.threads < self.num_threads:
            self.thread_request(message, client_address)
        elif not self.partner:
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
        if self.partner:
            self.sock.sendall(response)
        else:
            self.sock.sendto(response, client_address)
        if from_thread:
            self.threads -= 1

    def thread_request(self, message, client_address):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response_thread, args=(message, client_address), kwargs={"from_thread": True})
        t.start()
        self.threads += 1

    @staticmethod
    def info_partner(port, threads):
        """Listen for info."""
        info = {
            "port": port,
            "performance_rate": 0,
            "num_thread": threads,
            "thread_used": 0,
        }
        return info

    def insert_partner_in_queue(self, port, threads):
        """Insert partner in queue."""
        # TODO: Order by performance rate
        info = self.info_partner(port, threads)
        self.queue_available_servers.append(info)

    @staticmethod
    def create_subprocess():
        """Create a subprocess."""
        subprocess.run(["python", "-m", "server", "--partner"])

    def available_partner(self):
        """Get available partner."""
        if not self.queue_available_servers:
            self.create_subprocess()

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
