"""
Example code created by Teddy Tortorici for the Quantum Forge course
This is an example of code that can be used to communicate over GPIB using the server code so that another script can
also communicate with the same instruments without conflict. This script takes data and saves it in a Google Drive

@author: Teddy Tortorici
"""

import gpib_client_tools as client
import get
import os
import time


class DataFile:

    def __init__(self, path, filename, header='', host="localhost", port=62535):
        # define object attributes for communicating to the server.
        # These will be for each device involved in taking data for this data file
        self.ls = client.LakeShore(model_num=331, port=port)

        # the full name will be file path plus the filename
        # the file path will be relative to the Google Drive location
        self.name = os.path.join(get.googledrive(), path, filename)

        # make sure the name ends in the correct extension
        # you can write even more checks to ensure the name fits the conditions you desire.
        if '.csv' not in self.name:
            self.name += '.csv'

        # Write header for file
        self.write_comment(f"This data file was created on {time.ctime(time.time())}")
        self.write_comment(header)

        self.start_time = time.time()

    def single_measure(self):
        """Take a single data point"""
        time_elapsed = time.time()-self.start_time
        temp1 = self.ls.read_temperature('A')
        temp2 = self.ls.read_temperature('B')
        data = [time_elapsed, temp1, temp2]
        self.write_row(data)
        print(data)

    def take_data(self):
        """Will just continuously take data until program is cancelled"""
        while True:
            self.single_measure()

    def write_row(self, row_to_write: list):
        """Writes a new line in the csv file comma separated for each element in the list."""
        if isinstance(row_to_write, list):
            with open(self.name, 'a') as f:
                f.write(str(row_to_write).strip('[').strip(']').replace("'", "") + '\n')
        else:
            raise ValueError(f"write_row only accepts a list, -{type(row_to_write)}- given instead")

    def write_comment(self, comment: str):
        with open(self.name, 'a') as f:
            f.write(f'# {str(comment)}\n')

for ii in zip(10):
    print(ii)

if __name__ == "__main__":
    data = DataFile(path=os.path.join('data', '2022'), filename=f'file-{time.time()}', header='example data')
    data.take_data()
