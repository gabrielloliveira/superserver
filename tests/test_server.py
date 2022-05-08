import socket
from unittest import mock

import numpy as np
import pytest

from server.helpers import calculate_product, matrices_from_message
from server.server import Server


def test_create_super_server():
    """
    Test creating a super server
    """
    server = Server(threads=1)
    server.close()

    assert server.host == "127.0.0.1"
    assert server.port == 8080
    assert server.partner is False
    assert server.num_threads == 1
    assert server.threads == 0
    assert server.sock is not None
    assert server.sock.family == socket.AF_INET
    assert server.sock.type == socket.SOCK_DGRAM


@pytest.mark.parametrize(
    "message, expected_matrix",
    [
        ("[[1, 2, 3], [4, 5, 6], [7, 8, 9]] x [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        (b"[[1, 2, 3], [4, 5, 6], [7, 8, 9]] x [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    ],
)
def test_matrices(message, expected_matrix):
    """
    Test matrices
    """
    matrices = matrices_from_message(message)
    assert isinstance(matrices, list)
    assert len(matrices) == 2
    assert matrices[0] == expected_matrix
    assert matrices[1] == expected_matrix


def test_calculate_product():
    """
    Test calculate product from matrices
    """
    matrices = [[[2, 3], [3, 4]], [[5, 6], [6, 7]], [[2, 3], [3, 4]]]
    expected_result_mult = [[155, 216], [216, 301]]

    result_mult = calculate_product(matrices)
    np.testing.assert_array_equal(result_mult, expected_result_mult)
    assert len(result_mult) == 2


@mock.patch("server.server.Server.create_socket_tcp", return_value=None, autospec=True)
def test_subprocess_initialization(mock_create_socket_tcp):
    """
    Test subprocess initialization
    """
    server = Server(threads=1, partner=True)
    assert server.partner is True
    assert mock_create_socket_tcp.called


def test_subprocess_initialization_with_port():
    """
    Test subprocess initialization with port
    """
    server = Server(threads=1, partner=True, port=8081)
    server.close()
    assert server.port == 8081
    assert server.sock is not None
    assert server.sock.family == socket.AF_INET
    assert server.sock.type == socket.SOCK_STREAM
