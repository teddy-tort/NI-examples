"""
Example code created by Teddy Tortorici for the Quantum Forge course
This code allows you to establish connection with an instrument over GPIB in a way that allows multiple scripts to
communicate over the same protocol without hanging up the system

@author: Teddy Tortorici
"""

import time
import threading
import socket
import gpib


lock = threading.Lock()


# This is an example of a class which is not meant to be used to create objects. Instead, you reference the class
# directly and use the @classmethod
class Interpreter:
    """place device information here and rename to suit your needs"""
    # lakeshore = gpib.Device(8)
    # device2 = gpib.Device(13)

    @classmethod
    def parse(cls, message_to_parse):
        """Parse a message of the format INSTRUMENT::READ,RIGHT,orQUERY::MESSAGEtoINSTRUMENT"""
        msg_list = message_to_parse.upper().split('::')
        dev_id = msg_list[0]
        command = msg_list[1]
        try:
            message = msg_list[2]
        except IndexError:
            message = ''

        """MUST EDIT THE FOLLOWING LINES TO SUIT YOUR NEEDS"""
        if dev_id == "LS":
            instrument = cls.lakeshore
            print("Sending message to Lakeshore temperature controller")
        elif dev_id == "MAKE THIS INSTRUMENT ID 2":
            instrument = cls.instrument2
            print("Sending message to instrument2")
        else:
            instrument = None

        if instrument:
            if command[0] == "W":
                print(f'Writing "{message}" to {dev_id}')
                instrument.write(message)
                msgout = 'empty'
            elif command[0] == "Q":
                print(f'Querying {dev_id} with "{message}"')
                msgout = instrument.query(message)
            elif command[0] == "R":
                print(f'Reading from {dev_id}')
                msgout = instrument.read()
        else:
            msgout = 'Did not give a valid device id'
        return msgout


def server_echo_rev(host: str = "localhost", port: int = 62538):
    """Receives messages from a client and returns the message reversed"""
    global lock

    running = True
    # open a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        print(f"Socket bound to port: {port}")

        # put the socket into listening mode
        s.listen()

        # loop until client wants to exit with "shutdown" command
        while running:
            # establish connection with client
            conn, addr = s.accept()
            lock.acquire()
            with conn:
                print(f"Connected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                while True:
                    msg_client = conn.recv(1024)
                    print(repr(msg_client))
                    if not msg_client:
                        lock.release()
                        break
                    elif msg_client == b"shutdown":
                        running = False
                        break
                    else:
                        print(f'Recieved message: {msg_client.decode()}')
                        msg_server = msg_client.decode()[::-1]
                    conn.sendall(msg_server.encode())


def server_gpib(host="localhost", port=62538):
    running = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        print(f"Socket binded to port: {port}")

        # put the socket into listening mode
        s.listen()

        # loop until client wants to exit with "shutdown" command
        while running:
            # establish connection with client
            conn, addr = s.accept()
            lock.acquire()
            with conn:
                print(f"Connected to :{addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                while True:
                    msg_client = conn.recv(1024)
                    # print(repr(msg_client))
                    if not msg_client:
                        lock.release()
                        break
                    elif msg_client == b"shutdown":
                        running = False
                        break
                    else:
                        print(f'Recieved message: {msg_client.decode()}')
                        # parse message
                        msg_server = Interpreter.parse(msg_client.encode())
                        print(repr(msg_server))
                    conn.sendall(msg_server.encode())


if __name__ == "__main__":
    server_echo_rev()
