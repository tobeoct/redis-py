from redis_py.resp.models import RespCommands
from redis_py.persistence import db
class Processor:

    def handle_command(self, command, args):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        if command == RespCommands.SET:
            if len(args) != 2:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.set(args[0], args[1])
        elif command == RespCommands.GET:
            if len(args) != 1:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.get(args[0])
        elif command == RespCommands.DEL:
            if len(args) != 1:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.delete(args[0])
        elif command == RespCommands.PING:
            if len(args) != 0:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.ping()
        elif command == RespCommands.ECHO:
            if len(args) != 1:
                return "ERROR"  # Return 'ERROR' if the command format is wrong
            return self.echo(args[0])

        return "ERROR"  # Return 'ERROR' if the command type is unknown

    def ping(self):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        return "PONG"

    def echo(self, value):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        return value

    def set(self, key, value):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        db[key] = value  # Store the key-value pair in our dictionary
        return "OK"  # Return a success message

    def get(self, key):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        # Return the value for the given key if it exists, otherwise return '(nil)'
        return db.get(key, None)

    def delete(self, key):
        """
        Deserializes a message from a resp protocol to a format that can be understood
        by the system

        Args:
            resp_string: message

        Returns:
            A tuple of 3 (prefix,length,data)
        """
        if key in db:
            del db[key]  # Delete the key-value pair from our dictionary
            return "OK"  # Return a success message
        return None  # Return '(nil)' if the key does not exist
