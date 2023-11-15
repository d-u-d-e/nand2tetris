class SyntaxError(RuntimeError):
    def __init__(self, descr):
        super().__init__()
        self.descr = descr