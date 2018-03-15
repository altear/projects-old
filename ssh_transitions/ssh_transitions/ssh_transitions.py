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

'''

import paramiko
import re

class Machine:
    def __init__(self):
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


    def run(self):
        next_state = self.get_transition()
        while next_state:
            self.current_state = next_state

            # do not run state if it is an exit state
            if self.current_state.state_type == 'exit':
                break

            self.current_state.run()
            next_state = self.get_transition()

    def add_state(self, *args, **kwargs):
        _state = State(self, *args, **kwargs)
        self.states.append(_state)

    def add_transition(self, *args, **kwargs):
        _transition = Transition(self, *args, **kwargs)
        self.transitions.append(_transition)

    def get_transition(self):
        # filter so that only the states that derive from current state or none are left
        _valid_transitions = list(filter(lambda x: x.source == self.current_state.name or x.source == None), self.transitions)

        # sort by priority
        _valid_transitions = sorted(_valid_transitions, key=lambda x: x.priority, reverse=True)

        # loop through and return the first trigger
        for _transition in _valid_transitions:
            if _transition.is_triggered():
                return _transition.get_destination()

    def listen(self):
        pass

class State:
    def __init__(self, machine, name, state_type, update_callback=None, action_callback=None):
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
                self.update_callback()

            # step 2. Actions
            if self.action_callback:
                self.action_callback()
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
    machine = Machine()

    # create exit states
    machine.add_state(name='success', state_type='exit')
    machine.add_state(name='failure', state_type='exit')

    # create retry state
    def increment_retries(state):
        state.machine.retries += 1
    machine.add_state(name='retry', state_type='inner', update_callback=increment_retries)

    #

if __name__ == '__main__':
    default_setup()