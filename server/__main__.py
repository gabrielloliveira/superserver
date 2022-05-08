import argparse
import random

from server.partner import PartnerServer
from .server import Server

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parâmetros necessários.")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        action="store",
        help="Número de threads para o servidor.",
        required=False,
        default=0,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Porta que o servidor irá escutar.",
        action="store",
        type=int,
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

    data = args.__dict__.copy()

    if not data["port"]:
        del data["port"]

    partner = data["partner"]
    del data["partner"]

    if partner:
        data["threads"] = random.randint(1, 4)
        server = PartnerServer(**data)
    else:
        server = Server(**data)
    server.run()
