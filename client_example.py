"""
Example code created by Teddy Tortorici for the Quantum Forge course
This is an example of code that can be used to communicate over GPIB using the server code so that another script can
also communicate with the same instruments without conflict

@author: Teddy Tortorici
"""

"""MUST BE RUNNING gpib_comm_server.py IN A COMMAND LINE"""

import time


def set_temperature_and_wait(setpoint, dev, power=5):
    dev.set_heater_range(power)
    dev.set_setpoint(setpoint)

    while abs(dev.read_temperature(channel='A', units='K') - setpoint) > 1:
        time.sleep(15)      # wait 15 seconds between checks
    # while loop breaks after temperature comes within 1 K of setpoint


if __name__ == "__main__":
    import gpib_client_tools as client

    ls = client.LakeShore(model_num=331, port=62535)
    set_temperature_and_wait(setpoint=305, dev=ls, power=5)
    print(ls.read('B', 'K'))
