import socket
import subprocess
import threading

from server.helpers import calculate_product, matrices_from_message

HOST = "127.0.0.1"
PORT = 8080

BUFFER_SIZE = 1024 * 10


class Server:
    def __init__(self, num_threads: int, is_subprocess: bool = False, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.is_subprocess = is_subprocess
        self.sock = self.create_sock()
        self.num_threads = num_threads
        self.threads = 0
        self.queue_available_servers = []
        self.queue_unavailable_servers = []

    def close(self):
        """Close the server."""
        self.sock.close()

    def run(self):
        """Run the server."""
        if self.is_subprocess:
            print("🚀 Starting server on mode subprocess...")
        print(f"🚀 Starting server on port {self.port}...")
        print(f"🚀 Number of threads = {self.num_threads}...")
        listen_type_connection = self.listen_udp
        if self.is_subprocess:
            listen_type_connection = self.listen_tcp
        while True:
            listen_type_connection()

    def create_sock(self):
        """Create a socket."""
        if self.is_subprocess:
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
        print("🚀 Waiting for connections...")
        message, client_address = self.sock.recvfrom(BUFFER_SIZE)
        print("🚀 Received connection...", client_address)
        self.handle_request(message, client_address)

    def listen_tcp(self):
        """Listen for connections."""
        pass

    def handle_request(self, message, client_address):
        """Handle a request."""
        if self.threads < self.num_threads:
            self.thread_request(message, client_address)
        else:
            self.subprocess_request(message, client_address)

    def send_response_thread(self, message, client_address, from_thread=False):
        """Send a response to the client."""

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

    def create_subprocess(self):
        """Create a subprocess."""
        available_port = self.available_port()
        threads = 1
        subprocess.run(["python", "-m", "server", "-t", str(threads), "-p", str(available_port), "--partner"])
        self.insert_partner_in_queue(available_port, threads)

    def available_partner(self):
        """Get available partner."""
        if not self.queue_available_servers:
            self.create_subprocess()
        return self.queue_available_servers.pop(0)

    def subprocess_request(self, message, client_address):
        """Handle request in a subprocess."""
        # TODO: Send request to available subprocess or create a new subprocess
        available_server = self.available_partner()
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
