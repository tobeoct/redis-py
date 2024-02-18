from .network import Network;

def start():
    Network().start_server()
def stop():
    Network().stop_server()