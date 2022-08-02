"""
Example code created by Teddy Tortorici for the Quantum Forge course
This code allows sends messages to the server created in gpib_comm_server

@author: Teddy Tortorici
"""

import numpy as np
import socket


def send(msg, host="localhost", port=62535):
    """Sends message to server
    The server will lock the thread until it's done, so you can send more messages and they wait in line"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # send message to server
    s.send(msg.encode('ascii'))

    # message returned from the server
    msg_out = s.recv(1024)

    s.close()
    return msg_out.decode('ascii')


class Device:
    """This class is meant to be inherited by classes dedicated to specific devices"""
    def __init__(self, abbreviation, port=62535):
        self.abbr = abbreviation
        self.port = port

    def query(self, msg):
        return send(f"{self.abbr}::Q::{msg}")

    def write(self, msg):
        send(f"{self.abbr}::W::{msg}")
        return "empty"

    def read(self):
        return send(f"{self.abbr}::R::X")

    def read_id(self):
        return self.query('*IDN?')

    def reset(self):
        self.write('*RST')


class LakeShore(Device):
    def __init__(self, model_num=331, port=62535):
        super(self.__class__, self).__init__(abbreviation="LS", port=port)      # initiate the class inherited from

        self.model_num = int(model_num)    # as in for LS331 or LS340

        """Correspond heater power (in Watts) with heater range settings (index of the list)"""
        if model_num == 340:
            self.heater_ranges = [0.0, 0.05, 0.50, 5.0, 50.0]
        else:
            self.heater_ranges = [0.0, 0.5, 5.0, 50.0]

        # get the PID controll settings for loop 1 and loop 2 (there is no loop 0)
        self.pid = [0, self.read_pid(1), self.read_pid(2)]

    def read_heater_output(self) -> float:
        """Query the percent power being output to the heater"""
        return float(self.query('HTR?'))

    def read_heater_range(self) -> float:
        """Query the heater range. Returns value in Watts"""
        return float(self.heater_ranges[int(self.query('RANGE?'))])

    def read_pid(self, loop: int = 1) -> list:
        """Returns in units of Kelvin per minute"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        msg_back = self.query(f"PID? {int(loop)}")
        p = float(msg_back[0])
        i = float(msg_back[1])
        d = float(msg_back[2])
        return [p, i, d]

    def read_ramp_speed(self, loop: int = 1) -> float:
        """Kelvin per minute"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return float(self.query(f"RAMP? {loop}").split(',')[1])

    def read_ramp_status(self, loop: int = 1) -> bool:
        """Check whether the setpoint is ramping or not"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return bool(int(self.query(f"RAMPST? {loop}")))

    def read_setpoint(self, loop=1):
        """Return the value of setpoint in current units"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        return float(self.query(f"SETP? {loop}"))

    def read_temperature(self, channel: str = 'A', units: str = 'K') -> float:
        """Read the temperature on a channel"""
        # Ensure the variables are uppercase
        channel = channel.upper()
        units = units.upper()

        # Ensure the variables are valid
        if channel not in ['A', 'B']:
            raise IOError(f"Invalid channel: {channel}")
        if units not in ['K', 'C']:
            raise IOError(f"Invalid units: {units}")
        return float(self.query(f"{units}RDG? {channel}"))

    def set_heater_range(self, power_range: float, override: bool = False):
        """Sets the heater range"""
        # ensure that the power_range is positive
        power_range = abs(float(power_range))

        # find the nearest valid setting to the power given
        setting = np.argmin(self.heater_ranges - power_range)
        if self.heater_ranges[setting] == 50. and not override:
            print("50V is probably too high and will fry your solder joints. If you disagree, override==True")
        else:
            self.write(f"RANGE {setting}")

    def set_pid(self, p='', i='', d='', loop=1):
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        if p == '':
            p = self.PID[loop][0]
        else:
            self.PID[loop][1] = float(p)
        if i == '':
            i = self.PID[loop][1]
        else:
            self.PID[loop][1] = float(i)
        if d == '':
            d = self.PID[loop][2]
        else:
            self.PID[loop][2] = float(d)
        self.write(f"PID {loop}, {p}, {i}, {d}")

    def set_ramp_speed(self, kelvin_per_min, loop=1):
        """Set the ramp speed to reach set point in Kelvin per min"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        self.write(f"RAMP {loop}, 1, {kelvin_per_min}")

    def set_setpoint(self, value, loop=1):
        """Configure Control loop setpoint.
        loop: specifies which loop to configure.
        value: the value for the setpoint (in whatever units the setpoint is using"""
        if loop != 1 and loop != 2:
            raise IOError(f"invalid loop: {loop}")
        self.write(f"SETP {loop}, {float(value)}")
