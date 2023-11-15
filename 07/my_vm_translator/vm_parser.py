class Parser:
    @staticmethod
    def fatal_error(number, description):
        print(f"error at line: {number}")
        print(description)
        exit(1)

    def parse_line(self, number, s):
        pos = 0
        tokens = []
        while True:
            # skip all spaces
            while (pos < len(s) and s[pos].isspace()):
                pos += 1
            # break if line ends
            if pos == len(s):
                break
            # read token
            token_start = pos
            if len(s[token_start:]) >= 2 and s[token_start] == '/' and s[token_start + 1] == '/':
                # skip comment
                return tokens
            while True:
                if s[pos].isspace():
                    break
                pos += 1
            # token read
            tokens.append(s[token_start:pos])
        return tokens
