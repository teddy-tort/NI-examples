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
class Interpreter:
    """place device information here and rename to suit your needs"""
    lakeshore = Device(addr=8, gpib_num=0)
    device2 = Device(addr=13, gpib_num=0)

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
            if msg_client.lower() == "shutdown":
                print_lock.release()
                c.close()
                break
            else:
                # parse message
                msg_out = Interpreter.parse(msg_client)
                print(repr(msg_out))
                c.send(msg_out.encode('ascii'))
    s.close()


if __name__ == "__main__":
    server_main()
