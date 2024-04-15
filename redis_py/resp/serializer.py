from redis_py.exception import AppException
from redis_py.resp.models import (
    TERMINATOR,
    RespCommands,
    RespDataTypes,
    RespError,
    RespResponseMessages,
)
from redis_py.utility import to_int


class RespProtocolSerializer:

    @staticmethod
    def serialize(value):
        if value is None:
            return f"_{TERMINATOR}"
        if value == "ERROR":
            return f"{RespDataTypes.ERROR.value}{TERMINATOR}"

        if isinstance(value, str) and (value == RespCommands.OK.value or repr(value).find('\\')==-1):
            return f"{RespDataTypes.SIMPLE_STRING.value}{str(value)}{TERMINATOR}"
        value =str(value)
        length = len(value)
        return f"{RespDataTypes.BULK_STRING.value}{length}{TERMINATOR}{value}{TERMINATOR}"

    @staticmethod
    def deserialize(serialized_str):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            serialized_str: message

        Returns:
            A tuple of 3 (data_type,length,data)
        """
        try:

            data_type = RespProtocolSerializer.__validate_serialized_str(serialized_str)

            if data_type == RespDataTypes.SIMPLE_STRING:
                return RespProtocolSerializer.__parse_simple_strings(serialized_str)

            elif data_type == RespDataTypes.INTEGER:
                return RespProtocolSerializer.__parse_integers(serialized_str)

            elif data_type == RespDataTypes.ERROR:
                return RespProtocolSerializer.__parse_errors(serialized_str)

            elif data_type == RespDataTypes.BOOLEAN:
                return RespProtocolSerializer.__parse_booleans(serialized_str)

            elif data_type == RespDataTypes.BULK_STRING:
                return RespProtocolSerializer.__parse_bulk_strings(serialized_str)

            elif data_type == RespDataTypes.ARRAY:
                return RespProtocolSerializer.__parse_arrays(serialized_str)

        except AppException as e:
            print("ERROR:", str(e))
            return RespError(str(e)), RespDataTypes.ERROR, 0

        return None, data_type, 0

    @staticmethod
    def __validate_serialized_str(serialized_str):
        if not serialized_str:
            raise AppException(RespResponseMessages.NO_DATA)

        if not serialized_str.endswith(TERMINATOR):
            raise AppException(RespResponseMessages.NO_TERMINATOR)

        data_type = serialized_str[0]
        if not RespDataTypes.is_valid(data_type):
            raise AppException(RespResponseMessages.INVALID_DATA_TYPE)

        return RespDataTypes(data_type)

    @staticmethod
    def __parse_booleans(serialized_str):
        start_index = serialized_str.find(RespDataTypes.BOOLEAN.value) + 1
        value = RespProtocolSerializer.__get_data(serialized_str, start_index)

        if value not in ["t", "f"]:
            raise AppException(RespResponseMessages.UNRECOGNIZED_BOOLEAN_DATA)

        is_integer, value = to_int(value)

        if not is_integer:
            raise AppException(RespResponseMessages.NOT_AN_INTEGER)

        return value, RespDataTypes.INTEGER, 0

    @staticmethod
    def __parse_integers(serialized_str):
        start_index = serialized_str.find(RespDataTypes.INTEGER.value) + 1
        value = RespProtocolSerializer.__get_data(serialized_str, start_index)

        if not value:
            raise AppException(RespResponseMessages.NO_VALUE)

        is_integer, value = to_int(value)

        if not is_integer:
            raise AppException(RespResponseMessages.NOT_AN_INTEGER)

        return value, RespDataTypes.INTEGER, 0

    @staticmethod
    def __parse_simple_strings(serialized_str):
        start_index = serialized_str.find(RespDataTypes.SIMPLE_STRING.value) + 1
        data = RespProtocolSerializer.__get_data(serialized_str, start_index)
        if not data:
            raise AppException(RespResponseMessages.NO_DATA)
        return data, RespDataTypes.SIMPLE_STRING, 0

    @staticmethod
    def __parse_errors(serialized_str):
        start_index = serialized_str.find(RespDataTypes.ERROR.value) + 1
        data = RespProtocolSerializer.__get_data(serialized_str, start_index)
        if not data:
            raise AppException(RespResponseMessages.NO_DATA)
        return RespError(data), RespDataTypes.ERROR, 0

    @staticmethod
    def __parse_bulk_strings(serialized_str):
        size, end_index = RespProtocolSerializer.__get_size(
            RespDataTypes.BULK_STRING.value, serialized_str
        )

        if size is None:
            raise AppException(RespResponseMessages.MISSING_SIZE)
        if size < -1:
            raise AppException(RespResponseMessages.UNEXPECTED_DATA_LENGTH)
        if size == -1:
            return None, RespDataTypes.BULK_STRING, 0
        if size == 0:
            return "", RespDataTypes.BULK_STRING, size
        start_index = end_index + 2
        data = RespProtocolSerializer.__get_data(serialized_str, start_index)

        if len(data) != size:
            raise AppException(RespResponseMessages.UNEXPECTED_DATA_LENGTH)
        return data, RespDataTypes.BULK_STRING, size

    @staticmethod
    def __parse_arrays(serialized_str):
        size, _ = RespProtocolSerializer.__get_size(
            RespDataTypes.ARRAY.value, serialized_str
        )

        if size is None:
            raise AppException(RespResponseMessages.MISSING_SIZE)
        if size < -1:
            raise AppException(RespResponseMessages.UNEXPECTED_DATA_LENGTH)
        if size == -1:
            return None, RespDataTypes.ARRAY, 0
        if size == 0:
            return "", RespDataTypes.ARRAY, size

        serialized_str, result = RespProtocolSerializer.__parse(serialized_str)

        if serialized_str != "" and serialized_str is not None:
            raise AppException("Incomplete deserialization")
        return result, RespDataTypes.ARRAY, size

    @staticmethod
    def __parse(str):
        if not str:
            return None, []
        result = []
        size, end_index = RespProtocolSerializer.__get_size(
            RespDataTypes.ARRAY.value, str
        )
        str = str[end_index:]

        if size == -1:
            return str[str.find(TERMINATOR) + 2 :], None

        while len(result) < size and str:
            if not str.startswith(TERMINATOR):
                if RespDataTypes.is_scalar(str[0]):
                    end_index = str.find(TERMINATOR, 0) + 2
                    data, data_type, _ = RespProtocolSerializer.deserialize(
                        str[:end_index]
                    )
                    if (
                        data_type == RespDataTypes.ERROR
                        and str[0] != RespDataTypes.ERROR.value
                    ):
                        raise AppException(data.message)
                    result.append(data)
                    str = str[end_index:]
                elif str.startswith(RespDataTypes.BULK_STRING.value):
                    s, _ = RespProtocolSerializer.__get_size(
                        RespDataTypes.BULK_STRING.value, str
                    )
                    if s == -1:
                        start_index = 0
                        end_index = str.find(TERMINATOR, start_index) + 2
                    else:
                        start_index = str.find(TERMINATOR, 0) + 2
                        end_index = str.find(TERMINATOR, start_index) + 2
                    data, data_type, _ = RespProtocolSerializer.deserialize(
                        str[:end_index]
                    )
                    if data_type == RespDataTypes.ERROR:
                        raise AppException(data.message)
                    result.append(data)
                    str = str[end_index:]
                elif str.startswith(RespDataTypes.ARRAY.value):
                    str, nested_result = RespProtocolSerializer.__parse(str)
                    result.append(nested_result)
                else:
                    continue
            else:
                str = str[str.find(TERMINATOR) + 2 :]

        return str, result

    @staticmethod
    def __get_size(data_type, str):
        if RespDataTypes.is_scalar(data_type):
            return None, 0
        start_index = str.find(data_type) + 1
        end_index = str.find(TERMINATOR, start_index)
        is_integer, size = to_int(str[start_index:end_index])
        if not is_integer:
            return None, end_index
        return size, end_index

    @staticmethod
    def __get_data(str, start_index):
        end_index = str.find(TERMINATOR, start_index)
        return str[start_index:end_index]
