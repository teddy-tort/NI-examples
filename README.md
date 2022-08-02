# NI-examples
 examples using the PyVISA Library for Quantum Forge

## Explanation of scripts

#### calculations.py
 Most projects you work on will have some calculations that you will utilize regularly, these can be put into their own script that can be imported. These can be split up into multiple scripts for better organization if needed. You can utilize a function from the script by importing it in the following way
 ```
 import calculations as calc
 
 print(calc.custom_function())
 ```
 It is unlikely the calculations in this example will be useful for you, but it is made to serve as a template for you.
 
 The top of of your file you should give a header explaining what it is useful for.
 
 Then you import any useful packages; for a calculation script, you will no doubt be importing numpy.
 
 Then you can define any constants such as fundamental physics constants. Make sure you comment the units as often "natural units" for coding are not SI. For example, in this script, the electric constant (aka permittivity of free space) is given in pF/um because relevant capacitances are around pF scale and relevant lengths are as small as a few um. This helps avoid numbers getting too large or too small in the script.
 
 Then you define your functions with "def". You can use : notation to help clarify the kinds of inputs it takes as seen in the first function
 ```
 def capacitance(g: float, u: float, N: float, L: float, hS: float, epsS: float) -> float:
 ```
 These essentially act as comments and serve no actually functional purpose as far as the script is concerned. It is just for user benefit to see what the type should be. The "-> float" specifies that the output will be a float.
 
 Use a """comment""" to specify how the function works, what it's for, and any relevant units information if applicable. This ensures you remember what things do if you haven't used them in long enough. It also ensures that others are able to understand what your code does if you are working with collaborators or sharing your code with others.

#### get.py
Often times you will be saving data to some kind of cloud-based folder like a Google Drive, Dropbox, or One Drive. You typically won't have your scripts in the same place (as these will be saved where you save your git repos), so you will need to reference them. If you utilize your code on multiple machines, having a get.py file is incredibly useful for making sure your code works equally well on different machines regardless of operating system.

This example shows how to set up a pointer to a Google Drive on your hard drive. The example checks what the operating system is and states where the Google Drive folder will be found. You will likely need to alter this example to fit your needs. Utilizing the script would look something like this
```
import get
import os

path_to_save = os.path.join(get.googledrive(), 'my_data_directory_name')
```

#### gpib.py
This script lays a template for communicating with devices over GPIB protocols. The class "Device" is meant to be used to create device objects. The objects will be for specific devices that are connected over GPIB. These can be things like oscilloscopes, waveform generators, temperature controllers, power supplies, etc. You can create an object for one of these devices in the following way: (let's assume we have a waveform generator connected over GPIB with address 12 and a temperature controller with address 15)

```
from gpib import Device

waveform_generator = Device(addr=12)
temperature_controller = Device(addr=15)
```

The "def"s inside the class are called methods instead of functions. The first method __init__ is called upon generating the object from the class and it's arguments are given when generating the class as seen above (the "addr=" is not necessary, but helps clarify and makes it easier to read and understand the code).

The other methods will be commonly used across devices. These include reading from and writing to the device as well as querying (which writes and then reads).

The last bit of code
```
if __name__ == "__main__":
    """This only runs when you run this .py script directly, and is skipped if you import the script"""
    address = 12
    dev = Device(address)
    print(dev.id())
```
only runs if you run the script diretly, and will be igored if the script is imported. In this case, you can put some code that tests the script to make sure it works as intended. This example connects to a device on address 12 and then prints the devices ID.

#### temperature_controller.py

This is an example of creating a class that inherits from the gpib.Device class. The reason you may want to do this is to create a class specific to a particular device. This example is for a Lakeshore temperature controller. This way we can make methods specific to interacting with this specific instrument.

The end of the script shows a quick example of connecting to a Lakeshore331 on address 12, asking for its ID and then reading the temperature on channel A.
```
if __name__ == "__main__":
    """This only runs when you run this .py script directly, and is skipped if you import the script"""
    address = 12
    ls = LakeShore(address)
    print(ls.id())
    print(f"Stage A: {ls.read_temperature(channel='A', units='K')} K")
```

There is however, a major flaw in doing things this way. If you want to run multiple scripts simultaneously (for example, one that reads data continuously, and another that controls things), then those scripts will conflict with each other. If we want this capability, we will need to set up some server code.

#### gpib_comm_server.py

This script sets up a server that takes commands from as many clients as necessary and has each request wait in line and gets to each in the order received. The "clients" in this case are just different scripts that would like to request data from the devices over GPIB. Using code like this is only necessary if you have multiple scripts all running together (or multiple threads running together) that all communicate with the devices. If you don't need this feature set, the previous example is perfectly sufficient and far simpler.

```
print_lock = threading.Lock()
```
