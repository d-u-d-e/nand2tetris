import os

class Generator:
    unique_id = None
    def __init__(self):
        self.filename = os.path.basename(__file__)
        self.unique_id = 0
        self.segment_dict = \
        {
            'argument': 'ARG',
            'local'   : 'LCL',
            'this'    : 'THIS',
            'that'    : 'THAT',
            'constant': 'constant',
            'static'  : 'static',
            'temp'    : 'temp',
            'pointer' : 'pointer'
        }

    @staticmethod
    def fatal_error(number, description):
        print(f"error at line: {number}")
        print(description)
        exit(1)
    
    def get_binary_op_asm(self, line_no, op):
        return (
            "@SP\n"       +
            "A=M-1\n"     + # get second element addr 
            "D=M\n"       + # second element
            "A=A-1\n"     + # addr of first element
            f"D=M{op}D\n" + # compute binary operation
            "M=D\n"       + # save result
            "@SP\n"       + # decrement original stack pointer
            "M=M-1"
        )
    
    def get_unary_op_asm(self, line_no, op):
        return (
            "@SP\n"      +
            "A=M-1\n"    +  # get addr of last element
            f"D={op}M\n" +  # compute unary operation on last element
            "M=D"           # save
        )
    
    def get_cmp_op_asm(self, line_no, cmp_op):
        id1 = self.unique_id
        id2 = self.unique_id + 1
        self.unique_id += 2
        return (
            "@SP\n"        +
            "A=M-1\n"      + # get second element addr 
            "D=M\n"        + # get second element
            "A=A-1\n"      + # get addr of first element 
            "D=M-D\n"      + # compute difference
            f"@_{id1}_\n"  + # set jump label
            f"D;J{cmp_op.upper()}\n" +
            "@SP\n"        +  # cmp is false
            "A=M-1\n"      +
            "A=A-1\n"      +
            "M=0\n"        +  # set stack memory to false
            f"@_{id2}_\n"  +
            "0;JMP\n"      +
            f"(_{id1}_)\n" +
            "@SP\n"        +  # cmp is true
            "A=M-1\n"      +
            "A=A-1\n"      +
            "M=-1\n"       +  # set stack memory to true
            f"(_{id2}_)\n"
            "@SP\n"        +  # decrement stack pointer
            "M=M-1"
        )
    
    def get_push_op_asm(self, line_no, segment, value):
        if (segment == 'local' or segment == 'argument' or 
            segment == 'this' or segment == 'that'):
            prefix = (
                f"@{value}\n"   +  # read address index
                f"D=A\n"        + # save it
                f"@{self.segment_dict[segment]}\n" + # load segment address
                "A=M+D\n"       + # compute offset
                "D=M\n"         # save memory value into D
            )
        elif segment == 'constant':
            prefix = (
                f"@{value}\n"  + # read const value
                f"D=A\n"         # save it into D
            )
        elif segment == 'static':
            # create a label with name Filename.value
            prefix = (
                f"@{self.filename}.{value}\n" +
                f"D=M\n"      # save it into D
            )

        elif segment == 'temp':
            num = int(value)
            if num < 0 or num > 7:
                self.fatal_error(line_no, "the temp index must be between 0 and 7")
            prefix = (
                f"@{5 + num}\n" +
                f"D=M\n"      # save it into D
            )
        elif segment == 'pointer':
            value = "THIS" if value == "0" else "THAT"
            prefix = (
                f"@{value}\n" +
                f"D=M\n"      # save it into D
            )    
        else:
            self.fatal_error(line_no, "wrong push syntax")

        suffix = (
            "@SP\n"   + # push D onto stack
            "A=M\n"   +
            "M=D\n"   + 
            "@SP\n"   + # increment stack pointer
            "M=M+1"
        )
        return prefix + suffix

    def get_pop_op_asm(self, line_no, segment, value):

        prefix = ""
        if (segment == 'local' or segment == 'argument' or 
            segment == 'this' or segment == 'that'):
            prefix = (
                f"@{value}\n" + # read address index
                f"D=A\n"      + # save it
                f"@{self.segment_dict[segment]}\n" + # load segment address
                "D=M+D\n"     # save sum addr into D
                )                
        elif segment == 'constant':
            self.fatal_error(line_no, "cannot pop from constant segment")
        elif segment == 'static':
            # create a label with name Filename.value
            prefix = (
                f"@{self.filename}.{value}\n" +
                f"D=A\n" # save it into D
            )
        elif segment == 'temp':
          num = int(value)
          if num < 0 or num > 7:
              self.fatal_error(line_no, "the temp index must be between 0 and 7")
          prefix = (
                f"@{5 + num}\n" + # read address index
                f"D=A\n"        # save it
                )
        elif segment == 'pointer':
            value = "THIS" if value == "0" else "THAT"
            prefix = (
                f"@{value}\n" +
                f"D=A\n"      # save it into D
            )               
        else:
            self.fatal_error(line_no, "wrong pop syntax")
        
        suffix =  (
            "@SP\n"   + # push D
            "A=M\n"   +
            "M=D\n"   +

            "@SP\n"   + # decrement stack pointer
            "M=M-1\n" +
            "A=M\n"   + # go to top element which has to be popped
            "D=M\n"   + # save it into D

            "A=A+1\n" + # go to next stack element which contains addr of seg index
            "A=M\n"   + # get the address of the segment index
            "M=D"     # store the top element at that address

        )
        return prefix + suffix
        

    def line_tokens_to_asm(self, line_no, tokens):
        if (tokens[0] == 'add' or tokens[0] == 'sub' 
            or tokens[0] == 'and' or tokens[0] == 'or'):
            if tokens[0] == 'add':
                sign = '+'
            elif tokens[0] == 'sub':
                sign = '-'
            elif tokens[0] == 'or':
                sign = '|'
            else:
                sign = '&'
            return self.get_binary_op_asm(line_no, sign);
        ############################################################
        elif tokens[0] == 'neg' or tokens[0] == 'not':
            sign = '-' if tokens[0] == 'neg' else '!'
            return self.get_unary_op_asm(line_no, sign)
        ############################################################
        elif tokens[0] == 'eq' or tokens[0] == 'gt' or tokens[0] == 'lt':
            self.unique_id += 1
            return self.get_cmp_op_asm(line_no, tokens[0])
        ############################################################
        elif tokens[0] == 'push' or tokens[0] == 'pop':
            if len(tokens) != 3:
                self.fatal_error(line_no, f"wrong {tokens[0]} syntax")
            segment = tokens[1]
            value = tokens[2]
            if not value.isnumeric():
                self.fatal_error(line_no, "segment value not integer")
        ############################################################
            if tokens[0] == 'push':
                return self.get_push_op_asm(line_no, segment, value)
            else:
                return self.get_pop_op_asm(line_no, segment, value)  
        ############################################################            
        elif tokens[0] == 'label':
            if len(tokens) != 2 or tokens[1][0].isnumeric():
                self.fatal_error(line_no, "wrong label syntax")
            return f"({tokens[1].upper()})"
        ############################################################
        elif tokens[0] == 'goto':
            if len(tokens) != 2 or tokens[1][0].isnumeric():
                self.fatal_error(line_no, "wrong goto syntax")
            return (
                f"@{tokens[1].upper()}\n" +
                f"0;JMP"
            )
        ############################################################
        elif tokens[0] == 'if-goto':
            if len(tokens) != 2 or tokens[1][0].isnumeric():
                self.fatal_error(line_no, "wrong if-goto syntax")
            return (
                "@SP\n"           +
                "M=M-1\n"         + # decrement SP
                "A=M\n"           +
                "D=M\n"           + # get popped element
                f"@{tokens[1].upper()}\n" +
                f"D;JNE"            # jump based on popped element
            )
        ############################################################            
        else:
            return "TODO " + tokens[0]