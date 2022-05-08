from server import HOST, PORT


class BaseServer:
    def __init__(self, host=HOST, port=PORT, threads=0):
        self.host = host
        self.port = port
        self.max_threads = threads
        self.threads = 0
        self.sock = self.create_socket()

    def create_socket(self):
        raise NotImplementedError

    def close(self):
        self.sock.close()

    def listen(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
