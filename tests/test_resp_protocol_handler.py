import pytest
from redis_py.processor import Processor
from redis_py.resp.handler import RespProtocol

@pytest.mark.happy
@pytest.mark.parametrize(
    "message, expected_response",
    [
        ("+PING\r\n", "+PONG\r\n"),
        ("*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n", "+hello world\r\n"),
        ("*3\r\n$3\r\nset\r\n$3\r\nkey\r\n$3\r\nkey\r\n","+OK\r\n"),
        ("*2\r\n$3\r\nget\r\n$3\r\nkey\r\n","+key\r\n")
    ]
)
def test_ping_request(message, expected_response):
    """ Simple strings are encoded as a plus (+) character, followed by a string.
        The string mustn't contain a CR (\r) or LF (\n) character and is terminated by CRLF (i.e., \r\n).
        format=> +<data>\r\n
    """

    response = RespProtocol(Processor).handle_request(message)

    assert response == expected_response
