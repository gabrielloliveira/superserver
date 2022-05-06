from random import randint

from .server import Server


if __name__ == "__main__":
    server = Server(num_threads=randint(1, 4))
    server.run()
