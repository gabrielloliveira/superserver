import argparse

from .server import Server

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parâmetros necessários.")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        action="store",
        help="Número de threads para o servidor.",
        default=1,
        required=True,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Porta que o servidor irá escutar.",
        action="store",
        required=False,
    )
    parser.add_argument(
        "--partner",
        help="Inidica se o servidor é parceiro.",
        action="store_true",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    server = Server(num_threads=args.threads, is_subprocess=args.partner, port=args.port)
    server.run()
