from syntax_error import *

class Mapper:

    def __init__(self, generator):
        self.idgen = generator
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

    ############################################################
    def build_binary_op_asm(self, op):
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
    
    ############################################################
    def build_unary_op_asm(self, op):
        return (
            "@SP\n"      +
            "A=M-1\n"    +  # get addr of last element
            f"D={op}M\n" +  # compute unary operation on last element
            "M=D"           # save
        )
    
    ############################################################
    def build_cmp_op_asm(self, cmp_op):
        id1 = self.idgen.get_unique_id()
        id2 = self.idgen.get_unique_id()
        return (
            "@SP\n"                  +
            "A=M-1\n"                + # get second element addr 
            "D=M\n"                  + # get second element
            "A=A-1\n"                + # get addr of first element 
            "D=M-D\n"                + # compute difference
            f"@__{id1}__\n"          + # set jump label
            f"D;J{cmp_op.upper()}\n" +
            "@SP\n"                  + # cmp is false
            "A=M-1\n"                +
            "A=A-1\n"                +
            "M=0\n"                  + # set stack memory to false
            f"@__{id2}__\n"          +
            "0;JMP\n"                +
            f"(__{id1}__)\n"         +
            "@SP\n"                  + # cmp is true
            "A=M-1\n"                +
            "A=A-1\n"                +
            "M=-1\n"                 + # set stack memory to true
            f"(__{id2}__)\n"
            "@SP\n"                  + # decrement stack pointer
            "M=M-1"
        )
    
    ############################################################
    def build_push_op_asm(self, unit_filename, segment, value):
        if (segment == 'local' or segment == 'argument' 
            or segment == 'this' or segment == 'that'):
            prefix = (
                f"@{value}\n"                      + # read address index
                f"D=A\n"                           + # save it
                f"@{self.segment_dict[segment]}\n" + # load segment address
                "A=M+D\n"                          + # compute offset
                "D=M\n"                              # save memory value into D
            )
        elif segment == 'constant':
            prefix = (
                f"@{value}\n"  + # read const value
                f"D=A\n"         # save it into D
            )
        elif segment == 'static':
            prefix = (
                f"@{unit_filename}.{value}\n" + # create a label with name filename.value
                f"D=M\n"                        # save it into D
            )
        elif segment == 'temp':
            num = int(value)
            if num < 0 or num > 7:
                raise SyntaxError("the temp index must be between 0 and 7")
            prefix = (
                f"@{5 + num}\n" +
                f"D=M\n"          # save it into D
            )
        elif segment == 'pointer':
            value = "THIS" if value == "0" else "THAT"
            prefix = (
                f"@{value}\n" +
                f"D=M\n"          # save it into D
            )    
        else:
            raise SyntaxError('invalid push segment')

        suffix = (
            "@SP\n"   + # push D onto stack
            "A=M\n"   +
            "M=D\n"   + 
            "@SP\n"   + # increment stack pointer
            "M=M+1"
        )
        return prefix + suffix

    ############################################################
    def build_pop_op_asm(self, unit_filename, segment, value):

        prefix = ""
        if (segment == 'local' or segment == 'argument' 
            or segment == 'this' or segment == 'that'):
            prefix = (
                f"@{value}\n"                      + # read address index
                f"D=A\n"                           + # save it
                f"@{self.segment_dict[segment]}\n" + # load segment address
                "D=M+D\n"                            # save sum addr into D
                )                
        elif segment == 'constant':
            raise SyntaxError("cannot pop from constant segment")
        elif segment == 'static':
            
            prefix = (
                f"@{unit_filename}.{value}\n" + # create a label with name filename.value
                f"D=A\n"                        # save it into D
            )
        elif segment == 'temp':
          num = int(value)
          if num < 0 or num > 7:
              raise SyntaxError("the temp index must be between 0 and 7")
          prefix = (
                f"@{5 + num}\n" + # read address index
                f"D=A\n"          # save it
                )
        elif segment == 'pointer':
            value = "THIS" if value == "0" else "THAT"
            prefix = (
                f"@{value}\n" +
                f"D=A\n"        # save it into D
            )               
        else:
            raise SyntaxError('invalid pop segment')
        
        suffix =  (
            "@R13\n"  + # save D into temporary register
            "M=D\n"   +

            "@SP\n"   + # decrement stack pointer
            "M=M-1\n" +
            "A=M\n"   + # go to top element which has to be popped
            "D=M\n"   + # save it into D

            "@R13\n"  + # get addr of segment index
            "A=M\n"   + # go there
            "M=D"       # write popped element at that address
        )
        return prefix + suffix
    
    ############################################################
    def build_label_asm(self, name):
        return f"({name})"

    ############################################################
    def build_goto_asm(self, name):
        return (
            f"@{name}\n" +
            f"0;JMP"
        )

    ############################################################
    def build_ifgoto_asm(self, name):
        return (
            "@SP\n"                 +
            "M=M-1\n"               + # decrement SP
            "A=M\n"                 +
            "D=M\n"                 + # get popped element
            f"@{name}\n" +
            f"D;JNE"                  # jump based on popped element
        )

    ############################################################