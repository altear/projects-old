import paramiko
import re
import socket

class SshMachine:
    def __init__(self, client):
        # connection properties
        self.client = client
        self.channel = client.invoke_shell()
        self.channel.settimeout(3)
        self.buffer_length = 4096

        # machine properties
        self.transitions = []
        self.states = []

        # default setup
        self.data = StateData()
        self.add_state(name='success', state_type='exit')
        self.add_state(name='failure', state_type='exit')
        self.add_state(name='retry')

        # exception handling with retry and failure states
        self.add_transition(trigger=None, target='retry', priority=-1)
        self.add_transition(trigger=Defaults.do_retry_trigger, target=Defaults.get_retry_checkpoint, source='retry', priority=1)
        self.add_transition(trigger=None, target='failure', priority=-1)



    def add_states(self, *args, **kwargs):
        for item in args:
            if isinstance(item, State):
                self.states.append(item)

    def create_state(self, *args, **kwargs):
        self.states.append(State(*args, **kwargs))

    def add_transitions(self, *args):
        # add transitions
        for item in args:
            if isinstance(item, Transition):
                self.transitions.append(item)

    def create_transition(self, *args, **kwargs):
        self.transitions.append(Transition(*args, **kwargs))

    def read_buffer(self, data):
        try:
            while True:
                current_buffer = self.channel.recv(self.buffer_length)
                if len(current_buffer): break
                data.buffer += current_buffer
        except:
            pass

    def get_transition(self, state, data):
        # get the transitions for this state
        _transitions = filter(lambda x: x.source is None or x.source == state.name, self.transitions)

        # sort them by order of priority
        _transitions = sorted(_transitions, key=lambda x: x.priority, reversed=True)

        # loop through transitions
        for transition in _transitions:
            if transition.is_triggered(machine=self, state=state, data=data):
                return transition.get_target(data)

    def process_state(self, state, data):
        # check if this is an exit state
        if state.state_type == 'exit':
            return state.name

        # skip update/action steps if we are resuming a state from an interrupt
        if not data.interrupt or data.interrupt.name != state.name:
            state.update_callback(data)
            state.action_callback(data)

        # and if we are resuming, reset the interrupt
        elif data.interrupt and data.interrupt.name == state.name:
            data.interrupt = None

        # always continue from here
        self.read_buffer(data)

        # find the next transition
        self.get_transition(state, data)

class Transition:
    def __init__(self, trigger, target, source=None, priority=0, trigger_when='end'):
        self.trigger = trigger
        self.target = target
        self.source = source
        self.priority = priority
        self.trigger_when = trigger_when

    def is_triggered(self, data):
        # if there is no trigger, always return true
        if self.trigger is None:
            return True

        # if the trigger is a function, call it
        elif callable(self.trigger):
            return self.trigger(data)

        # if the trigger is a string then treat it like regex
        elif isinstance(self.trigger, str):
            return bool(Defaults.regex_trigger(pattern=self.trigger, data=data))

        # if nothing matches, then return false
        raise Exception("Transition's trigger type, from {state}, is unrecognized".format_map(state=data.history[-1].name))

        return False

    def get_target(self, data):
        if not callable(self.target):
            return self.target
        else:
            return self.target(data)

class StateData:
    def __init__(self):
        self.history = []
        self.buffer = b''
        self.interrupt = None
        self.retries = 0
        self.retry_checkpoint = None

class State:
    state_types = ['entry', 'inner', 'exit']
    def __init__(self, name, state_type='inner'):
        self.name = name
        self.state_type = state_type
        self.update_callback = None
        self.action_callback = None
        self.read_callback = None
        self.transition_callback = None

class Defaults:
    def regex_trigger(**kwargs):
        text = kwargs['data'].buffer.decode('utf-8')
        pattern = kwargs['pattern']
        return bool(re.search(pattern, text, re.MULTILINE))


    # retry related
    def do_retry_trigger(**kwargs):
        data = kwargs['data']
        return data.retry_checkpoint is not None and data.retries < 2

    def get_retry_checkpoint(**kwargs):
        data = kwargs['data']
        return data.retry_checkpoint if data.retry_checkpoint else 'failure'


