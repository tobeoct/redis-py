class Commands:
    def __init__(self, db):
        self.db = db

    def ping(self):
        return 'PONG' 
    
    def echo(self, value):
        return value; 
    
    def set(self,key, value):
        self.db[key] = value  # Store the key-value pair in our dictionary
        return 'OK'  # Return a success message

    def get(self,key):
        # Return the value for the given key if it exists, otherwise return '(nil)'
        return self.db.get(key, "(nil)")
    
    def delete(self,key):
        if key in self.db:
            del self.db[key]  # Delete the key-value pair from our dictionary
            return 'OK'  # Return a success message
        else:
            return "(nil)"  # Return '(nil)' if the key does not exist