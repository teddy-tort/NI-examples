"""
Example code created by Teddy Tortorici for the Quantum Forge course
This code allows you to establish connection with an instrument over GPIB

@author: Teddy Tortorici
"""

import pyvisa
import numpy as np


class Device:
    def __init__(self, addr: int, gpib_num: int = 0):
        """establish connection with instrument over GPIB
        addr - (int) the GPIB address of the instrument you wish to communicate with
        gpib_num - (int) Which GPIB interface connected to the computer. Typically 0, unless
                   multiple GPIB interfaces are connected"""
        self.addr = addr
        self.rm = pyvisa.ResourceManager()
        self.dev = self.rm.open_resource(f"GPIB{gpib_num}::{addr}::INSTR")

    def query(self, msg):
        """Send message to instrument and return result"""
        try:
            return self.dev.query(msg)
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def query_ascii(self, msg, sep=',', conv='f'):
        """Some instruments allow to transfer to and from the computer larger datasets with a single query. A typical
        example is an oscilloscope, which you can query for the whole voltage trace. Or an arbitrary wave generator to
        which you have to transfer the function you want to generate."""
        try:
            return self.dev.query_ascii_values(msg, container=np.array, separator=sep, converter=conv)
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def read(self):
        """Read from the instrument"""
        try:
            return self.dev.read()
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def write(self, msg):
        """write to the instrument"""
        try:
            self.dev.write(msg)
            return ""
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def id(self):
        return self.query('*IDN?')


if __name__ == "__main__":
    """This only runs when you run this .py script directly, and is skipped if you import the script"""
    address = 12
    dev = Device(address)
    print(dev.id())
