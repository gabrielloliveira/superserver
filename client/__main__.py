import argparse
import random

from server.partner import PartnerServer
from .client import Client


def execute():
    client = Client()
    menssage_random = client.gerate_random_message()

    while True:
        try:
            client.send_message(menssage_random)
        except:
            execute()


if __name__ == "__main__":
    execute()
