class Protocol:
    def __init__(self, commandHandler):
        self.commandHandler = commandHandler

    def handle(self,command):
        print(command)
        command_parts = command.split()  # Split the command by spaces
        if len(command_parts) == 0:
            return ""
        command_type = command_parts[0].lower()  # Get the command type (set, get, del)
        if command_type == 'set':
            if len(command_parts) != 3:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.commandHandler.set(command_parts[1], command_parts[2])
        elif command_type == 'get':
            if len(command_parts) != 2:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.commandHandler.get(command_parts[1])
        elif command_type == 'del':
            if len(command_parts) != 2:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.commandHandler.delete(command_parts[1])
        elif command_type == 'ping':
            if len(command_parts) != 1:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.commandHandler.ping()
        elif command_type == 'echo':
            if len(command_parts) != 2:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.commandHandler.echo(command_parts[1])
        else:
            return "ERROR"  # Return 'ERROR' if the command type is unknown