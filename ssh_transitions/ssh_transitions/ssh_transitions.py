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

import logging
import paramiko
import socket
import re
from functools import partial

logger = logging.getLogger("ssh_transitions")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def do_retry(trig):
    print(trig.machine.retries, trig.machine.max_retries)
    return trig.machine.retries <= trig.machine.max_retries

def get_last_checkpoint(trig):
    return trig.machine.checkpoint.name

def standard_update(state):
    # check that this state is a checkpoint and isn't retrying (or cycling)
    if state.is_checkpoint and (not state.machine.checkpoint or state.machine.checkpoint.name != state.name):
        state.machine.checkpoint = state
        state.machine.retries = 0

def get_sudo(trig):
    return trig.machine.interrupt.name

class Machine:
    def __init__(self, connection_args):
        self.states = []
        self.transitions = []

        # maximum number of transitions
        self.transitions_count = 0
        self.transitions_max = 100

        # initialize state related info
        self.current_state = None
        self.previous_state = None
        self.history = []

        # retry related
        self.retries = 0
        self.max_retries = 1
        self.checkpoint = None

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
        self.channel.settimeout(60)

        self.sftp_client = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())

    def run(self):
        # get the first state by searching for the enter state (there should only be 1 for predictable behaviour)
        next_state = None
        for state in self.states:
            if state.state_type == 'enter':
                next_state = state

        # main loop
        while next_state:
            # set machine state info
            self.previous_state = self.current_state
            self.history.append(self.previous_state)
            self.current_state = next_state

            logger.info('running state: "{name}"; type: {stype}'.format(name=self.current_state.name, stype=self.current_state.state_type))

            # do not run state if it is an exit state
            if self.current_state.state_type == 'exit':
                break

            # run the state
            self.current_state.run()

            # get the next state
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

    def send(self, msg):
        self.channel.send(msg + '\n')

class State:
    def __init__(self, machine, name, is_checkpoint=True, state_type='inner', update_callback=standard_update, action=None):
        self.machine = machine
        self.name = name
        self.state_type = state_type
        self.is_checkpoint = is_checkpoint

        # set callbacks
        self.update_callback = update_callback
        self.action = action

    def run(self):
        # reset the buffer
        self.machine.buffer = b''

        # are we returning from an interrupt
        _returning_from_interrupt = self.machine.interrupt and self.machine.interrupt == self.name

        if not _returning_from_interrupt:
            # step 1. Update
            if self.update_callback:
                self.update_callback(self)

            # step 2. Actions
            if self.action:
                if isinstance(self.action, str):
                    self.machine.send(self.action)
                elif callable(self.action):
                    self.action(self)
        else:
            self.machine.interrupt = None

        # step 3. Read
        self.machine.listen()
        print(self.machine.buffer.decode('utf-8'))

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
            return bool(re.search(self.trigger, self.machine.buffer.decode('utf-8')))
        elif callable(self.trigger):
            return bool(self.trigger(self))
        return False

    def get_destination(self):
        if callable(self.destination):
            return self.destination(self)
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
    machine.add_state(name="entry", state_type='enter')
    # create exit states
    machine.add_state(name='success', state_type='exit')
    machine.add_state(name='failure', state_type='exit')

    # create retry state
    def increment_retries(state):
        state.machine.retries += 1
    machine.add_state(name='retry', is_checkpoint=False, update_callback=increment_retries)

    # create sudo state
    machine.add_state(name="sudo", action=connection_args['password'])

    # BUILTIN TRANSITIONS
    # retry/failure
    machine.add_transition(destination='retry', priority=-100)
    machine.add_transition(source='retry', destination='failure', priority=-1)
    machine.add_transition(source='retry', destination=get_last_checkpoint, trigger=do_retry, priority=0)

    # sudo
    machine.add_transition(destination='sudo', trigger="\[sudo\] password for")
    machine.add_transition(source='sudo', destination='failure', trigger="incorrect password attempts", priority=1)
    machine.add_transition(source='sudo', destination=get_sudo, priority=-200)

    return machine

if __name__ == '__main__':
    machine = default_setup()

    # USER DEFINED AREA
    # State 1: Get updates
    machine.add_transition(destination='update', source='entry')
    machine.add_state(name="update", action="sudo apt-get update -y")

    # State 2
    machine.add_transition(destination='upgrade', source='update', trigger="stretch InRelease")
    machine.add_transition(destination='upgrade', source='update', trigger="successfully updated")
    machine.add_state(name="upgrade", action="sudo apt-get upgrade -y")

    # State 2: Install tmux
    machine.add_transition(destination='install tmux', source="upgrade", trigger="successfully upgraded")
    machine.add_state(name="install tmux", action="sudo apt-get install -y tmux")

    # Success case
    machine.add_transition(source="install tmux", destination='success', trigger="tmux is already the newest version", priority=1)
    machine.add_transition(source="install tmux", destination='success', trigger="successfully installed tmux", priority=1)


    answer = machine.run()
    print("result", answer.name)