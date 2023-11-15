from symbols import Symbols

class Parser:
    @staticmethod
    def valid_dest(str):
        return str in Symbols.valid_dests.keys()
    
    @staticmethod
    def valid_comp(str):
        return str in Symbols.valid_comps.keys()
    
    @staticmethod
    def valid_jump(str):
        return str in Symbols.valid_jumps.keys()
    
    @staticmethod
    def fatal_error(number, description):
        print(f"error at line: {number}")
        print(description)
        exit(1) 

    def parse_instr_a(self, number, str):
        if str[0].isdigit():
            try:
                val_num = int(str)
                # we have 15 bit addresses
                if val_num < 0 or val_num > 32767:
                    self.fatal_error(number, 
                        "decimal address of A-instruction must be nonnegative and not greater than 32767")
                # all good
                return ["A", val_num]
            except ValueError:
                self.fatal_error(number, "non decimal A address must start with letter")
        elif str[0].isalpha():
            # read label up to space
            pos = 0
            while not str[pos].isspace():
                pos += 1
            val = str[0:pos]
            if not str[pos:].isspace():
                self.fatal_error(number, "A address followed by garbage")
            return ["A", val]
        else:
            self.fatal_error(number, "invalid A instruction")
    
    def parse_pseudo_label(self, number, str):
        # get closing parenthesis
        index = str.find(')')
        if index == -1:
            self.fatal_error(number, "missing ')' in label definition")
        if not str[index + 1:].isspace():
            self.fatal_error(number, "label is followed by garbage")
        val = str[0:index].strip()
        # crude check whitespaces
        if ' ' in val or '\t' in val:
            self.fatal_error(number, "labels cannot contain whitespaces")
        if val[0].isdigit():
            self.fatal_error(number, "labels cannot start with digit")
        return ["L", val]
    
    def parse_instr_c(self, number, str):
        # strip whitespaces
        str = str.strip()

        # get the jump field
        fields = str.split(";")
        if len(fields) == 2:
            # ["dest = comp", "jump"]
            jump = fields[1].strip()
            if jump == '':
                self.fatal_error(number, "invalid C instruction")
        elif len(fields) == 1:
            # ["dest = comp"]
            jump = "null"
        else:
            self.fatal_error(number, "invalid C instruction")

        # get the dest comp fields
        dest_comp = fields[0].split("=")
        if len(dest_comp) == 1:
            # no dest field specified
            dest = 'null'
            comp = '0' if dest_comp[0] == '' else dest_comp[0]
        elif len(dest_comp) == 2:
            # unpack
            dest, comp = dest_comp
        else:
            self.fatal_error(number, "invalid C instruction")

        dest = dest.strip()
        comp = comp.strip()
        
        # now validate
        if (not self.valid_comp(comp) or not self.valid_dest(dest) 
                or not self.valid_jump(jump)):
                self.fatal_error(number, "invalid C instruction")
        return ["C", dest, comp, jump]

    def parse_line(self, number, str):
        # skip all spaces
        pos = 0
        while pos < len(str) and str[pos].isspace():
            pos += 1
        if pos == len(str):
            return []
        str = str[pos:]
        # first char encountered
        if str[0] == '@':
            return self.parse_instr_a(number, str[1:])
        elif len(str) >= 2 and str[0:2] == "//":
            # skip comments
            return []
        elif str[0] == '(':
            return self.parse_pseudo_label(number, str[1:])
        else:
            return self.parse_instr_c(number, str)



