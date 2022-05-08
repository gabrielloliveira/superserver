import socket
import threading

from server import HOST, PORT, BUFFER_SIZE
from server.base import BaseServer
from server.helpers import calculate_product, matrices_from_message


class PartnerServer(BaseServer):
    def __init__(self, threads: int, host: str = HOST, port: int = PORT):
        super().__init__(threads=threads, host=host, port=port)

    @property
    def info(self):
        """Info partner server."""
        return {
            "port": self.port,
            "performance_rate": 0,
            "max_threads": self.max_threads,
            "thread_used": self.threads,
        }

    def run(self):
        """Run the server."""
        print("🚀 Starting server on mode partner...")
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.max_threads}...")
        self.listen()

    def create_socket(self):
        """Create a TCP socket."""
        self.port = self.available_port()
        print(f"🚀 Port {self.port} is available...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        return sock

    def available_port(self):
        """Get available port."""
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

    def listen(self):
        """Listen for connections."""
        # TODO: Register the server in the parent server queue
        print("🚀 Waiting for connections on TYPE MODE TCP...")
        self.sock.listen()
        while True:
            conn, client_address = self.sock.accept()
            print("🚀 Received connection...", client_address)
            message = conn.recv(BUFFER_SIZE)
            message = message.decode("utf-8")
            try:
                self.handle_request(message, conn)
            except Exception as e:
                conn.send(str(e).encode())

    def handle_request(self, message, connection):
        """Handle a request."""
        if self.threads < self.max_threads:
            return self.thread_request(message, connection)
        raise Exception("Too many threads running...")

    def send_response_thread(self, message, connection, from_thread=False):
        """Send a response to the client."""
        print(f"📩 Received {message} ...")
        print("🚀 Sending response...")
        try:
            matrices = matrices_from_message(message)
            product = calculate_product(matrices)
        except Exception:
            product = f"The matrices is not valid."

        response = str(product).encode("utf-8")
        connection.send(response)
        connection.close()
        if from_thread:
            self.threads -= 1

    def thread_request(self, message, connection):
        """Handle request in a thread."""
        t = threading.Thread(target=self.send_response_thread, args=(message, connection), kwargs={"from_thread": True})
        t.start()
        self.threads += 1
