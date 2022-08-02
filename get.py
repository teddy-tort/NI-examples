"""
Example code created for the Quantum Forge course
This is the kind of script you would have in your repository to make it so your code can easily be transported to new
machines that have folders in different locations.

This code "gets" the location of certain important folders like a Google Drive that you want to save to or the
serialport of a USB device

@author: Teddy Tortorici
"""

import sys
import os
import getpass


def googledrive():
    """Locates the google drive folder on your machine (you will likely have to put new conditions here for each
    machine (probably out of date for mac and linux versions, but example gets the idea across)"""
    user = getpass.getuser()
    if sys.platform == "darwin":    # for mac users
        path = f"/Users/{user}/Google_Drive/"
    elif sys.platform == "linux":
        path = f"/home/{user}/Documents/Google_Drive"
    else:       # if it's not linux or max it's probably windows
        if os.name == 'nt':     # just double checking that it's windows
            path = "G:\\My Drive"
        else:
            path = ''
    return path
