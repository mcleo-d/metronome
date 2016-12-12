# metronome

metronome is Symphony bot designed to provide end to end diagnostic information to the 
Symphony Engineering Services team.  This bot is fairly simple. 

It logs into your symphony pod, and then joins a cross pod chat room and begins to send messages with
some basic information about the pod environment.  

Our ES bot listens in and adds information to our local trends database and can alert our team to any problems
directly as needed.

## Installation

this application can be installed as an rpm or from a python setup.py.

   python setup.py install

will install this application, however it is recommended to install it within a virtualenv

You will also need to complete a metronome config file.
