from random import randint

from .server import Server
from ast import literal_eval
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parâmetros necessários.")
    parser.add_argument("threads", type=int, metavar="t", help="Número de threads para o servidor.")
    parser.add_argument("subprocess", metavar="s", type=str, help="É um subprocesso ?")

    args = parser.parse_args()
    print(args)
    print(args.threads)
    print()

    server = Server(num_threads=args.threads, is_subprocess=literal_eval(args.subprocess))
    server.run()
