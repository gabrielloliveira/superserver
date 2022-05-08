from ast import literal_eval
from functools import reduce

import numpy as np


def matrices_from_message(message: str):
    """Get matrices from message."""
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    list_matrices = message.lower().split("x")
    list_matrices = [literal_eval(m.strip()) for m in list_matrices]
    return list_matrices


def calculate_product(list_matrices: list):
    """Calculate product of matrices."""
    return reduce(np.dot, list_matrices)
