from collections import deque

class State(object):
    def __init__(self, state_char=None, multiline=False, 
                 exit_char=False, until_eol=False):
        self.state_char = state_char
        self.parsed = ['']
        self.multiline = multiline
        self.exit_char = exit_char or state_char
        self.until_eol = until_eol
    
    def parse(self, char):
        self.parsed[-1]+=char
    
    def new_line(self):
        self.parsed[-1]+="\n"
    
    def change_to_state(self):
        if self.parsed[-1]:
            self.parsed.append('')
    
    @property
    def result(self):
        return [elem.strip() for elem in self.parsed if elem]


class Parser(object):
    def __init__(self):
        self.states = {}
        self.parse_state_char = False
        self.state_stack = deque()
    
    def add_state(self, state):
        if state.state_char is None:
            self.default_state = state
        else:
            self.states[state.state_char] = state
    
    def get_state_by_char(self, char):
        if char in self.states:
            return self.states[char]
        else:
            return False

    def parse_line(self, line):
        for char in line:
            if not self.state.until_eol:
                ret = self.get_state_by_char(char)
                if ret:
                    self.state = ret
                    continue
            self.state.parse(char)
        
        if not self.state.multiline:
            self.state = self.default_state
        else:
            self.state.new_line()
    
    def parse_lines(self, lines):
        for line in lines:
            self.parse_line(line)
    
    def parse_text(self, text):
        self.parse_lines(text.splitlines())
    
    def parse_file(self, file_name):
        open_file = open(file_name)
        try:
            self.parse_text(open_file.read())
        finally:
            open_file.close()
    
    def get_state(self):
        return self._state
    
    def set_state(self, new_state):
        if new_state:
            new_state.change_to_state()
            self._state = new_state
    
    state = property(get_state, set_state)
