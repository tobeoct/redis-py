from redis_py.resp.models import (
    TERMINATOR,
    RespCommands,
    RespDataTypes,
    RespResponseMessages,
)
from redis_py.resp.serializer import RespProtocolSerializer


class RespProtocol:
    def __init__(self, command_processor):
        self.processor = command_processor()

    def handle_request(self, message):
        data, type, _ = RespProtocolSerializer.deserialize(message)
        args = []
        if isinstance(data, list):
            command = data[0]
            args = data[1:]
        else:
            command = data

        command = str(command).upper()
        if not RespCommands.is_valid(command):
            return (
                f"{RespDataTypes.ERROR.value}{RespResponseMessages.INVALID_COMMAND}{TERMINATOR}"
            )

        result = self.processor.handle_command(RespCommands(command), args)
        return RespProtocolSerializer.serialize(result)
