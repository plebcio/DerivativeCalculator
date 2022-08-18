

class myException(Exception):
    def __init__(self, tokens, text=""):
        self.text = text
        self.tokens = tokens