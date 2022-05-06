from .server import Server


if __name__ == "__main__":
    server = Server(num_threads=1)
    server.run()
