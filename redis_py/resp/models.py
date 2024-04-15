from enum import Enum

"""
These module contains resp models
"""
TERMINATOR = "\r\n"


class MyEnum(Enum):
    @classmethod
    def is_valid(self, value):
        return any(value == item.value for item in self)


class RespDataTypes(MyEnum):
    SIMPLE_STRING = "+"
    BULK_STRING = "$"
    ERROR = "-"
    INTEGER = ":"
    ARRAY = "*"
    BOOLEAN = "#"

    @classmethod
    def is_scalar(self, value):
        return any(
            value == item.value
            for item in [self.SIMPLE_STRING, self.ERROR, self.INTEGER, self.BOOLEAN]
        )


class RespResponseMessages:
    NO_TERMINATOR = "NO TERMINATOR"
    INVALID_DATA_TYPE = "INVALID DATA TYPE"
    INVALID_COMMAND = "INVALID COMMAND"
    UNRECOGNIZED_BOOLEAN_DATA = "UNRECOGNIZED BOOLEAN DATA"
    NO_DATA = "NO DATA"
    NO_VALUE = "NO VALUE"
    MISSING_SIZE = "MISSING SIZE"
    UNEXPECTED_DATA_LENGTH = "UNEXPECTED DATA LENGTH"
    NOT_AN_INTEGER = "NOT AN INTEGER"


class RespCommands(MyEnum):
    PING = "PING"
    OK = "OK"
    SET = "SET"
    GET = "GET"
    DEL = "DEL"
    ECHO = "ECHO"
    PONG = "PONG"


class RespError:
    def __init__(self, message):
        self.message = message

    def __eq__(self, other):
        if isinstance(other, RespError):
            return self.message == other.message
        return False
