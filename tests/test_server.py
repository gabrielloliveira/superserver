import socket
from unittest import mock

import numpy as np
import pytest

from server.server import Server


def test_create_super_server():
    """
    Test creating a super server
    """
    server = Server(num_threads=1)
    server.close()

    assert server.host == "127.0.0.1"
    assert server.port == 8080
    assert server.is_subprocess is False
    assert server.num_threads == 1
    assert server.threads == 0
    assert server.sock is not None
    assert server.sock.family == socket.AF_INET
    assert server.sock.type == socket.SOCK_DGRAM


@mock.patch("socket.socket.recvfrom", return_value=(b"test", ("123", 123)), autospec=True)
@mock.patch("server.server.Server.handle_request", return_value=None, autospec=True)
def test_listen(mock_handle_request, mock_recvfrom):
    """
    Test listen
    """
    server = Server(num_threads=1)
    server.listen()
    server.close()
    assert mock_recvfrom.called
    assert mock_handle_request.called


@mock.patch("socket.socket.recvfrom", return_value=(b"test", ("123", 123)), autospec=True)
@mock.patch("server.server.Server.send_response", return_value=None, autospec=True)
def test_server_send_response(mock_send_response, mock_recvfrom):
    """
    Test send response
    """
    server = Server(num_threads=1)
    server.listen()
    server.close()
    assert mock_recvfrom.called
    assert len(mock_send_response.call_args.args) == 3
    assert mock_send_response.call_args.args[1] is b"test"
    assert mock_send_response.call_args.args[2] == ("123", 123)
    assert mock_send_response.call_args.kwargs["from_thread"] is True


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
    server = Server(num_threads=1)
    matrices = server.matrices(message)
    server.close()
    assert isinstance(matrices, list)
    assert len(matrices) == 2
    assert matrices[0] == expected_matrix
    assert matrices[1] == expected_matrix


def test_calculate_product():
    """
    Test matrices
    """
    matrices = [[[2, 3], [3, 4]], [[5, 6], [6, 7]], [[2, 3], [3, 4]]]
    expected_result_mult = [[155, 216], [216, 301]]

    server = Server(num_threads=1)
    result_mult = server.calculate_product(matrices)
    server.close()
    assert len(result_mult) == 2
    np.testing.assert_array_equal(result_mult, expected_result_mult)
