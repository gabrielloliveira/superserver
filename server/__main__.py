import argparse

from .server import Server

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parâmetros necessários.")
    parser.add_argument("--threads", type=int, action="store", help="Número de threads para o servidor.", default=1, required=True)
    parser.add_argument("--subproccess", action="store", help="É um subprocesso ?", required=False, default=False)
    args = parser.parse_args()

    server = Server(num_threads=args.threads, is_subprocess=args.subprocess)
    server.run()
