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
 These essentially act as comments and serve no actually functional purpose as far as the script is concerned. It is just for user benefit to see what the type should be. The ```-> float``` specifies that the output will be a float.
 
 Use a ```"""comment"""``` to specify how the function works, what it's for, and any relevant units information if applicable. This ensures you remember what things do if you haven't used them in long enough. It also ensures that others are able to understand what your code does if you are working with collaborators or sharing your code with others.

#### get.py
Often times you will be saving data to some kind of cloud-based folder like a Google Drive, Dropbox, or One Drive. You typically won't have your scripts in the same place (as these will be saved where you save your git repos), so you will need to reference them. If you utilize your code on multiple machines, having a get.py file is incredibly useful for making sure your code works equally well on different machines regardless of operating system.

This example shows how to set up a pointer to a Google Drive on your hard drive. The example checks what the operating system is and states where the Google Drive folder will be found. You will likely need to alter this example to fit your needs. Utilizing the script would look something like this
```
import get
import os

path_to_save = os.path.join(get.googledrive(), 'my_data_directory_name')
```

#### gpib.py
This script lays a template for communicating with devices over GPIB protocols. The class ```Device``` is meant to be used to create device objects. The objects will be for specific devices that are connected over GPIB. These can be things like oscilloscopes, waveform generators, temperature controllers, power supplies, etc. You can create an object for one of these devices in the following way: (let's assume we have a waveform generator connected over GPIB with address 12 and a temperature controller with address 15)

```
from gpib import Device

waveform_generator = Device(addr=12)
temperature_controller = Device(addr=15)
```

The ```def```s inside the class are called methods instead of functions. The first method ```__init__``` is called upon generating the object from the class and it's arguments are given when generating the class as seen above (the "addr=" is not necessary, but helps clarify and makes it easier to read and understand the code).

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
creates the locking mechanism that blocks out other requests from scripts until the current request is fulfilled.

The ```Interpreter``` class is used to parse commands sent from the client scripts. You can alter this to accomadate any format of command, but this example uses a "INSTRUMENT-ID::READ/WRITE/QUERY::MESSAGE" structure. There is in ```__init__``` method because we will actually never instantiate the class into an object, we will just use the class method ```parse```. Before the methods are defined you will see the lines
```
    """place device information here and rename to suit your needs"""
    lakeshore = Device(addr=8, gpib_num=0)
    device2 = Device(addr=13, gpib_num=0)
```
These are class variables which in this case are objects for the devices we wish to communicate with. This example establishes communication with a Lakeshore331 on address 8 and a "device2" on address 13. We can access these class variables outside the class, but cannot change them with bits of code (like we can change object variables). We can call upon these variables in the following way

```
Interpreter.lakeshore.query('KRDG? A')
```
In this section you will define all the devices you have connected over GPIB and assign them the appropriate addresses. It doesn't matter what you call them, but naming them something obvious, like "oscilliscope" or "scope" or "oscope" for your oscilliscope is best practice. Don't just call things "dev1", "dev2", etc.

The ```parse``` method is decorated with ```@classmethod``` which allows us to use it the following way

```
Interpreter.parse("LS::Q::KRDG? A")
```
The first line of code in the method

```
msg_list = message_to_parse.upper().split('::')
```

splits the message by the ```"::"``` characters into a list, so ```"LS::Q::KRDG? A"``` becomes ```["LS", "Q", "KRDG?A"]```, so the 0th index is the instrument ID, which is stored in the variable ```dev_id```, the 1st index is the command such as "write", "read", or "query" which is stored in the variable ```command```, and if the command is to write or query the instrument, there needs to be a message to send it which would be the 2nd index stored in ```message```; since it's possible the ```message_to_parse``` won't be a long enough to have a 2nd index,

```
        try:
            message = msg_list[2]
        except IndexError:
            message = ''
```
is a way of avoiding the index error from killing our script.

The first if statement

```
        if dev_id == "LS":
            instrument = cls.lakeshore
            print("Sending message to instrument1")
        elif dev_id == "MAKE THIS INSTRUMENT ID 2":
            instrument = cls.instrument2
            print("Sending message to instrument2")
        else:
            instrument = None
```
you will edit to match the class variables you defined above the method. You will define device IDs, such as "LS" for the lakeshore that will define which device the command is for. It is best to keep these short and sweet (so you don't have to type out something very long every time). ```instrument``` acts as a pointer and depending on what the ```dev_id``` is, ```instrument``` will point to the approriate device. ```cls``` is a shorthand for the class itself, and it's a way of referencing itself in a class method. In normal methods (where you don't decorate with ```@classmethod```) you use ```self``` to self reference the object that has been instantiated by the class. Printing a little message like
```
            print("Sending message to Lakeshore temperature controller")
```

is helpful in keeping track of what the code is doing when you're running it so if there are any issues or errors, it's easier to see where it's happening.

The next if statement
```
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
```
first checks to make sure an instrument was pointed to, and if not, it will return a string letting you know you didn't give a valid id. You could also have the code raise an error if you'd like.

If an instrument was pointed to, it will figure out if the command was to read, write, or query that device, and then do so.

The function ```server_main``` sets up the server that listens for messages from client scripts. The ```host``` input is the ip address. If you're running the server and the client scripts on the same machine, you can assign ```host``` "localhost" (which is the default); the ```port``` can be virtually any number, but some of the lower numbered ports are already being used on your machine, so choosing a 5-6 digit number is usually the safe bet. I put in just a random large number as the default throughout the code, so that it can run without worrying about the port number.

This function sets up the server and begins listening for clients, and then loops forever until a client sends it the string "shutdown" which will end the script. After receiving a string and checking to make sure that it isn't the "shutdown" command, it will then send the string through the Interpreter.parse class method for it do "decide" what it should do.

All you need to do to run the server is open an Anaconda command line, navigate to this script and type

```
python gpib_comm_server.py
```
and leave the command line window open. You will see messages print to the screen as the server receives messages from the clients, so you can check on the window to see how it's doing.

#### gpib_client_tools.py
This script houses classes for specific devices. This way you can have an object for you instrument, and methods for specific actions like reading the temperature or setting a voltage. This way you don't have to memorize commands like "LS::Q::KDRG? A" and instead use a method like ```ls.read_temperature('A', 'K')```.

The first function in the script is ```send``` and all it does is send a message to the server. As long as the host and the port match the server, this should work.

The first class ```Device``` is a template class meant to be inherited from more specific classes. Since all devices will need to be able to be queried, be written to, and read from, it useful to write a template class like this so you don't have to write these methods for every device.

Below this class you will make classes specific for each device. An example for a Lakeshore temperature controller is given. By putting ```Device``` in parantheses in the first line tells Python you wish to inherit all of the methods of ```Device```. When you inherit, unless you want to override the ```__init__``` method of the parent class, you must have a line that initiates the parent ```__init__``` inside the child ```__init__```

```
super(self.__class__, self).__init__(abbreviation="LS", port=port)
```

Following are methods specific for interacting with a Lakeshore. 
