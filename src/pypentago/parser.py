class State(object):
    def __init__(self, parser, state_char=None, multiline=False, 
                 exit_char=False, until_eol=False):
        self.parser = parser
        self.state_char = state_char
        self.parsed = ['']
        self.multiline = multiline
        self.exit_char = exit_char
        self.until_eol = until_eol
        if not state_char:
            self.parser.default_state = self
        self.parser.states.append(self)
    
    def parse(self, char):
        self.parsed[-1]+=char
    
    def new_line(self):
        self.parsed[-1]+="\n"
    
    def change_to_state(self):
        if self.parsed[-1]:
            self.parsed.append('')
    
    def get_result(self):
        return [elem.strip() for elem in self.parsed if elem]
    
    result = property(get_result)


class Parser(object):
    def __init__(self):
        self.states = []
        self.parse_state_char = False
    
    def get_state_by_char(self, char):
        if char == self.state.exit_char:
            return self.default_state
        for state in self.states:
            if state.state_char != None and state.state_char == char:
                return state
        for state in self.states:
            if state.exit_char != None and state.exit_char == char:
                return self.default_state
    
    def parse_line(self, line):
        lst = list(line)
        pass_char = False
        for char in lst:
            if not self.state.until_eol:
                ret = self.get_state_by_char(char)
                self.state = ret
                if ret and not self.parse_state_char:
                    pass_char = True
            if not pass_char:
                self.state.parse(char)
            else:
                pass_char = False
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