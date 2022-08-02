"""
Example code created by Teddy Tortorici for the Quantum Forge course
This code allows you to establish connection with an instrument over GPIB in a way that allows multiple scripts to
communicate over the same protocol without hanging up the system

@author: Teddy Tortorici
"""

import time
import threading
import socket
from gpib import Device


print_lock = threading.Lock()


# This is an example of a class which is not meant to be used to create objects. Instead, you reference the class
# directly and use the @classmethod
class Parser:
    """place device information here and rename to suit your needs"""
    lakeshore = Device(addr=8, gpib_num=0)
    device2 = Device(addr=13, gpib_num=0)

    @classmethod
    def parse(cls, message_to_parse):
        """Parse a message of the format INSTRUMENT::READ,RIGHT,orQUERY::MESSAGEtoINSTRUMENT"""
        msg_list = message_to_parse.upper().split('::')

        """MUST EDIT THE FOLLOWING LINES TO SUIT YOUR NEEDS"""
        if msg_list[0] == "LS":
            instrument = cls.lakeshore
            print("Sending message to instrument1")
        elif msg_list[0] == "MAKE THIS INSTRUMENT ID 2":
            instrument = cls.instrument2
            print("Sending message to instrument2")
        else:
            instrument = None

        if instrument:
            if msg_list[1][0] == "W":
                print(f'Writing "{msg_list[2]}" to {msg_list[0]}')
                instrument.write(msg_list[2])
                msgout = 'empty'
            elif msg_list[1][0] == "Q":
                print(f'Querying {msg_list[0]} with "{msg_list[2]}"')
                msgout = instrument.query(msg_list[2])
            elif msg_list[1][0] == "R":
                print(f'Reading from {msg_list[0]}')
                msgout = instrument.read()
        else:
            msgout = 'Failed to connect'
        return msgout


def server_main(host="localhost", port=62535):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print(f"Socket binded to port: {port}")

    # put the socket into listening mode
    s.listen(5)
    print("Socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquire by client
        print_lock.acquire()
        print(f"Connected to :{addr[0]}:{addr[1]}  : {time.ctime(time.time())}")

        # Start a new thread and return its identifier
        while True:
            # message received from client
            msg_client = c.recv(1024)
            msg_client = msg_client.decode('ascii')
            if msg_client == "shutdown":
                print_lock.release()
                c.close()
                break
            else:
                # parse message
                msg_out = Parser.parse(msg_client)
                print(repr(msg_out))
                c.send(msg_out.encode('ascii'))
    s.close()


if __name__ == "__main__":
    server_main()
