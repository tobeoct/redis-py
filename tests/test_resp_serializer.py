import pytest
from redis_py.resp.models import  RespCommands, RespDataTypes, RespError, RespResponseMessages
from redis_py.resp.serializer import RespProtocolSerializer

##Bulk Strings:$<length>\r\n<data>\r\n
##Empty String: $0\r\n\r\n
##NULL: $-1\r\n
##Arrays: *<number-of-elements>\r\n<element-1>...<element-n>
##Empty Array: *0\r\n
##NULL Array: *-1\r\n
##The \r\n (CRLF) is the protocol's terminator, which always separates its parts.

# For Simple Strings, the first byte of the reply is "+"
# For Errors, the first byte of the reply is "-"
# For Integers, the first byte of the reply is ":"
# For Bulk Strings, the first byte of the reply is "$"
# For Arrays, the first byte of the reply is "*"

# Happy Tests:
# Sad Tests: Passing an invalid object as request, passing null as request, Request is not an array of bulk strings


# Array Tests

# Arrays can contain mixed data types. For instance, the following encoding is of a list of four integers and a bulk string
# When Redis replies with a null array, the client should return a null object rather than an empty array.


##Deserialization tests
##starting with testing simple strings for PING



##TESTS FOR STRING STRUCTURE##
@pytest.mark.sad
@pytest.mark.parametrize(
    "message, expected_data",
    [
        (f"+PING", RespResponseMessages.NO_TERMINATOR),
        ("", RespResponseMessages.NO_DATA)
    ]
)
def test_deserialization_of_invalid_command_structure(message, expected_data):
    """Does not match the general command structure <data_type><something in between><terminator>"""
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(expected_data)

@pytest.mark.sad
@pytest.mark.parametrize("message",
    [
        (f"RPING\r\n"),
        (f"%PING\r\n")
    ]
)
def test_deserialization_of_unrecognized_data_type_command(message):
    """First byte is not a recognized data_type"""
    data,data_type, length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(RespResponseMessages.INVALID_DATA_TYPE)



##TESTS FOR SIMPLE STRINGS##
@pytest.mark.happy
@pytest.mark.parametrize(
    "message, expected_data",
    [
        (f"+PING\r\n", RespCommands.PING.value),
        (f"+PING\r\n", RespCommands.PING.value),
        (f"+PONG\r\n", RespCommands.PONG.value)
    ]
)
def test_deserialization_of_valid_simple_string_command(message, expected_data):
    """ Simple strings are encoded as a plus (+) character, followed by a string.
        The string mustn't contain a CR (\r) or LF (\n) character and is terminated by CRLF (i.e., \r\n).
        format=> +<data>\r\n
    """

    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type != None and data_type == RespDataTypes.SIMPLE_STRING
    assert length == 0
    assert data != None and data == expected_data

@pytest.mark.sad
@pytest.mark.parametrize(
    "message, expected_data",
    [
        (f"+\r\n", RespResponseMessages.NO_DATA),
        (f"+PING", RespResponseMessages.NO_TERMINATOR)
    ]
)
def test_deserialization_of_invalid_simple_string_command(message, expected_data):
    """First byte is + but does not match expected format: +<data>\r\n"""
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(expected_data)



##TESTS FOR ERROR##
@pytest.mark.happy
@pytest.mark.parametrize(
    "message, expected_data",
    [
        (f"-An Error Occurred\r\n", "An Error Occurred")
    ]
)
def test_deserialization_of_error_command(message, expected_data):
    """
        format=> -<data>\r\n
    """

    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(expected_data)


##TESTS FOR INTEGERS##
@pytest.mark.happy
@pytest.mark.parametrize(
    "message, expected_data",
    [
        (f":+3\r\n", 3),
        (f":4\r\n", 4),
        (f":-5\r\n", -5),
        (f":0\r\n", 0)
    ]
)
def test_deserialization_of_valid_integer_command(message, expected_data):
    """RESP encodes integers in the following way:

        format=> :[<+|->]<value>\r\n
        The colon (:) as the first byte.
        An optional plus (+) or minus (-) as the sign.
        One or more decimal digits (0..9) as the integer's unsigned, base-10 value.
        The CRLF terminator.
    """
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.INTEGER
    assert length == 0
    assert data == expected_data

@pytest.mark.sad
@pytest.mark.parametrize(
    "message,  expected_data",
    [
         (f":hii\r\n", RespResponseMessages.NOT_AN_INTEGER),
        (f":\r\n", RespResponseMessages.NO_VALUE)
    ]
)
def test_deserialization_of_invalid_integer_command(message,expected_data):
    """First byte is : but does not match expected format=> :[<+|->]<value>\r\n"""
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(expected_data)



##TESTS FOR BULK STRINGS##
@pytest.mark.happy
@pytest.mark.parametrize(
    "message,expected_length, expected_data",
    [
        (f"$5\r\nhello\r\n",5, "hello"),
        (f"$11\r\nhello world\r\n",11, "hello world"),
        (f"$-1\r\n", 0, None),
        (f"$0\r\n\r\n", 0,"")
    ]
)
def test_deserialization_of_valid_bulk_string_command(message,expected_length,expected_data):
    """
        RESP encodes bulk strings in the following way:

        format=> $<length>\r\n<data>\r\n
        The dollar sign ($) as the first byte.
        One or more decimal digits (0..9) as the string's length, in bytes, as an unsigned, base-10 value.
        The CRLF terminator.
        The data.
        A final CRLF.
    """
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.BULK_STRING
    assert length == expected_length
    assert data == expected_data

@pytest.mark.sad
@pytest.mark.parametrize(
    "message,  expected_data",
    [
        (f"$PING\r\n", RespResponseMessages.MISSING_SIZE),
        (f"$\r\nPING\r\n", RespResponseMessages.MISSING_SIZE),
        (f"$4PING\r\n", RespResponseMessages.MISSING_SIZE),
        (f"$4\r\nhello\r\n", RespResponseMessages.UNEXPECTED_DATA_LENGTH),
        (f"$5\r\nhello", RespResponseMessages.NO_TERMINATOR),
        (f"$-2\r\n", RespResponseMessages.UNEXPECTED_DATA_LENGTH)
    ]
)
def test_deserialization_of_invalid_bulk_string_command(message,expected_data):
    """First byte is $ but does not match expected format: $<length>\r\n<data (same length as length passed)>\r\n"""
    data,data_type,length = RespProtocolSerializer.deserialize(message)
    assert data_type == RespDataTypes.ERROR
    assert length == 0
    assert data == RespError(expected_data)


##TESTS FOR ARRAYS##
@pytest.mark.happy
@pytest.mark.parametrize(
    "message,expected_length, expected_data",
    [
        ("*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n",2, ["hello","world"]),
        ("*2\r\n*3\r\n:1\r\n:2\r\n:3\r\n*2\r\n+Hello\r\n-World\r\n",2,[[1,2,3],['Hello',RespError('World')]]),
        ("*-1\r\n",0,None),
        ("*3\r\n$5\r\nhello\r\n$-1\r\n$5\r\nworld\r\n",3,["hello",None,"world"]),
        ("*3\r\n$5\r\nhello\r\n*-1\r\n$5\r\nworld\r\n",3,["hello",None,"world"])
    ]
)
def test_deserialization_of_valid_array_command(message,expected_length,expected_data):
    """
        RESP Arrays' encoding uses the following format:

        Format=> *<number-of-elements>\r\n<element-1>...<element-n>
        An asterisk (*) as the first byte.
        One or more decimal digits (0..9) as the number of elements in the array as an unsigned, base-10 value.
        The CRLF terminator.
        An additional RESP type for every element of the array.
    """
    data,data_type,length = RespProtocolSerializer.deserialize(message)

    assert data_type == RespDataTypes.ARRAY
    assert length == expected_length
    assert data == expected_data
