'''

Machine.run() procedures:
~~~~~~~~~~~~~~~~~~~~~~~~~
while transition:
    1. get state from transition
    2. run state
    3. get transition by regex or function


State.run() procedures:
~~~~~~~~~~~~~~~~~~~~~~~
1. Update
2. Act
3. Listen (enter here if interrupted)

Some exceptions to this are if the state run procedures are interrupted by a sudo command, then resume
from the listen function once the interrupt is completed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Structure: 


                      Entry 
                        |
  Retry <------------> S1 <--,
    |             |     |    |
    |             `--> S2 <--|
  Failure(exit)   |     |    |
                  `--> S3 <--`---> Sudo <-----> Retry ...
                        |
  Success(exit) <-------`


~~~~~~~~~~~~~~~~~~~~~~~~~
Two types of default actions
- send
- put
'''


import paramiko
import socket
import re
from functools import partial

class Machine:
    def __init__(self, connection_args):
        self.states = []
        self.transitions = []

        # maximum number of transitions
        self.transitions_count = 0
        self.transitions_max = 100

        #
        self.current_state = None
        self.history = []

        # retry related
        self.retries = 0
        self.max_retires = 3
        self.retry_checkpoint = None

        # interrupt related
        self.interrupt = None

        # input
        self.buffer = b''
        self.buffer_len = 4096

        # create connections ssh, ssh_channel, and sftp
        self.conection_args = connection_args
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(**connection_args)

        self.channel = self.ssh_client.invoke_shell()
        self.channel.settimeout(2)

        self.sftp_client = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())

    def run(self):
        next_state = None
        for state in self.states:
            if state.state_type == 'enter':
                next_state = state

        while next_state:
            self.current_state = next_state

            # do not run state if it is an exit state
            print(self.current_state.state_type)
            if self.current_state.state_type == 'exit':
                break

            self.current_state.run()
            next_state = self.get_transition()

        return self.current_state

    def add_state(self, *args, **kwargs):
        _state = State(self, *args, **kwargs)
        self.states.append(_state)

    def add_transition(self, *args, **kwargs):
        _transition = Transition(self, *args, **kwargs)
        self.transitions.append(_transition)

    def get_state(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return state
        raise Exception("No state found")

    def get_transition(self):
        # filter so that only the states that derive from current state or none are left
        _valid_transitions = list(filter(lambda x: x.source == self.current_state.name or x.source == None, self.transitions))

        # sort by priority
        _valid_transitions = sorted(_valid_transitions, key=lambda x: x.priority, reverse=True)

        # loop through and return the first trigger
        for _transition in _valid_transitions:
            if _transition.is_triggered():
                return self.get_state(_transition.get_destination())

        raise Exception("No transition found!")

    def listen(self):
        try:
            while True:
                current_buffer = self.channel.recv(self.buffer_len)
                # if len of current buffer is 0 then channel has been closed
                if len(current_buffer) == 0:
                    break
                self.buffer += current_buffer
        except socket.timeout as e:
            pass

class State:
    def __init__(self, machine, name, state_type='inner', update_callback=None, action_callback=None):
        self.machine = machine
        self.name = name
        self.state_type = state_type

        # set callbacks
        self.update_callback = update_callback
        self.action_callback = action_callback

    def run(self):
        # are we returning from an interrupt
        _returning_from_interrupt = self.machine.interrupt and self.machine.interrupt == self.name

        if not _returning_from_interrupt:
            # step 1. Update
            if self.update_callback:
                self.update_callback(self)

            # step 2. Actions
            if self.action_callback:
                self.action_callback(self)
        else:
            self.machine.buffer = b''
            self.machine.interrupt = None

        # step 3. Read
        self.machine.listen()


class Transition:
    def __init__(self, machine, destination, trigger=None, source=None, priority=0):
        self.machine = machine
        self.source = source
        self.destination = destination
        self.trigger = trigger
        self.priority = priority

    def is_triggered(self):
        if self.trigger is None:
            return True
        elif isinstance(self.trigger, str):
            return bool(re.search(self.trigger, self.machine.buffer.decode('utf-8'), re.DOTALL))
        elif callable(self.trigger):
            return bool(self.trigger)
        return False

    def get_destination(self):
        if callable(self.destination):
            return self.destination()
        return self.destination

def default_setup():
    connection_args = {
        'username' : 'pi',
        'password' : 'raspberry',
        'hostname' : '70.79.136.37',
        'port' : 4423
    }

    machine = Machine(connection_args)

    # create entrance state
    machine.add_state(name='enter', state_type='enter')

    # create exit states
    machine.add_state(name='success', state_type='exit')
    machine.add_state(name='failure', state_type='exit')

    # create retry state
    def increment_retries(state):
        state.machine.retries += 1
    machine.add_state(name='retry', update_callback=increment_retries)

    # create sudo state
    def enter_password(state):
        state.machine.channel.send(connection_args['password'] + '\n')
    machine.add_state(name="sudo_password_entry", action_callback=enter_password)

    # create random state
    def test_me(state):
        state.machine.channel.send("ls -l /" + '\n')
    machine.add_state(name="test me", action_callback=test_me)

    # add transitions
    machine.add_transition(destination='test me', source='enter')
    machine.add_transition(destination='failure', priority=-1)

    answer = machine.run()
    print("exit state:", answer.name)
    print(machine.buffer.decode('utf-8'))


if __name__ == '__main__':
    default_setup()