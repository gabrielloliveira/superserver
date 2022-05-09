import argparse
import random

from server.partner import PartnerServer
from .client import Client

if __name__ == "__main__":
    client = Client()
    menssage_random = client.gerate_random_message()
    client.send_message(menssage_random)
