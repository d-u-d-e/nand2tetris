from syntax_error import *
from identifier_generator import *

class AsmBuilder:

    def __init__(self, generator: IdGenerator):
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
            "M=M-1\n"
        )
    
    ############################################################
    def build_unary_op_asm(self, op):
        return (
            "@SP\n"      +
            "A=M-1\n"    +  # get addr of last element
            f"D={op}M\n" +  # compute unary operation on last element
            "M=D\n"         # save
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
            "M=M-1\n"
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
            "M=M+1\n"
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
            "M=D\n"     # write popped element at that address
        )
        return prefix + suffix
    
    ############################################################
    def build_label_asm(self, name):
        return f"({name})\n"

    ############################################################
    def build_goto_asm(self, name):
        return (
            f"@{name}\n" +
            f"0;JMP\n"
        )

    ############################################################
    def build_ifgoto_asm(self, name):
        return (
            "@SP\n"                 +
            "M=M-1\n"               + # decrement SP
            "A=M\n"                 +
            "D=M\n"                 + # get popped element
            f"@{name}\n" +
            f"D;JNE\n"                # jump based on popped element
        )

    ############################################################
    def build_function_asm(self, func_label, nVars):
        # right below the label definition, we have nVars local variables
        # the space must be init'd to zero
        
        # small optimization
        if nVars < 4:
            # here we have 4 * nVars instructions <= 12
            return (
                f"({func_label})\n" +
                ("@SP\n"    +
                "M=M+1\n"   +
                "A=M-1\n"   +
                "M=0\n") * nVars
            )
        else:
            # here we have 15 instructions, so the init loop is faster
            loop = self.idgen.get_unique_id()
            endl = self.idgen.get_unique_id()
            return(
                f"({func_label})\n"  +
                f"@{nVars}\n"        + # save nVars into temporary register R13
                "D=A\n"              + 
                "@R13\n"             + 
                "M=D\n"              +

                f"(__{loop}__)\n"    + # begin init loop
                f"@__{endl}__\n"   +
                "D;JEQ\n"            + # end loop if nVars == 0
                "@SP\n"              +
                "M=M+1\n"            + # grow stack to accomodate for local variables
                "A=M-1\n"            +
                "M=0\n"              + # init element to 0
                "@R13\n"             +
                "M=M-1\n"            +
                "D=M\n"              + # nVars--
                f"@__{loop}__\n"   +
                "0;JMP\n"            +
                f"(__{endl}__)\n"    
            )
    
    def __push_value_at(self, addr):
        # simple helper that pushes MEM[addr] into the stack
        return (
            f"@{addr}\n" +
            "D=M\n"      +
            "@SP\n"      +
            "M=M+1\n"    +
            "A=M-1\n"    +
            "M=D\n"     
        )
    
    def __push_value(self, value):
        # simple helper that pushes value into the stack
        return (
            f"@{value}\n" +
            "D=A\n"       +
            "@SP\n"       +
            "M=M+1\n"     +
            "A=M-1\n"     +
            "M=D\n"     
        )

    ############################################################
    def build_call_asm(self, callee, args, ret_label):
        # We are inside the caller. The compiler has generated
        # code that pushes #args elements into the stack, if #args > 0.
        # Now we need to push the caller context (return addr, LCL, ARG, THIS, THAT).
        # We need somehow to reset ARG so that it points to the first arg element.
        # The last step is setting the LCL pointer to the current SP.
        # Note: if args is zero, where should we store the return value?
        # Recall that a return value always exists. We can store it at the return
        # address, provided this is retrieved before it is overwritten.

        return (
            self.__push_value(f"{ret_label}")    + # see below
            self.__push_value_at("LCL")          +
            self.__push_value_at("ARG")          +
            self.__push_value_at("THIS")         +
            self.__push_value_at("THAT")         +

            f"@{args}\n"   +  
            "D=A\n"        +   # save args into D
            "@SP\n"        +
            "D=M-D\n"      +
            "@5\n"         +
            "D=D-A\n"      +   # D = *SP - args - 5
            "@ARG\n"       +  
            "M=D\n"        +   # *ARG = D
            "@SP\n"        +
            "D=M\n"        +
            "@LCL\n"       +
            "M=D\n"        +   # *LCL = *SP
            f"@{callee}\n" +
            "0;JMP\n"      +   # jump to callee
            f"({ret_label})\n" # this is the return address for the callee
        )
    
    ############################################################
    def build_return_asm(self):
        # We are inside the callee.
        # We need the retrieve the return address that was pushed into the stack.
        # We need to store the return value in the first argument location.
        # We need to free the stack, by adjusting SP.
        # We need to restore the previous context.
        # Finally we can return.

        return (
            "@LCL\n"   +
            "D=M\n"    + # save beginning of current stack frame (which will disappear after the return)
            "@5\n"
            "A=D-A\n"  + # A is pointing at the return address
            "D=M\n"    +
            "@R14\n"
            "M=D\n"    + # store the return address temporarily in R14
            
            "@SP\n"    + # we know that the compiler pushed the return value right at the top of stack
            "A=M-1\n"
            "D=M\n"    +
            "@ARG\n"   + 
            "A=M\n"    +
            "M=D\n"    + # store ret value in the first arg location

            "@ARG\n"
            "D=M+1\n"  + # D contains the next value for SP
            "@SP\n"
            "M=D\n"    + # fix SP

            "@LCL\n"
            "D=M\n"    + # beginning of current stack frame  
            "@R13\n"   +
            "M=D\n"    + # save it into R13

            "A=D-1\n"  +
            "D=M\n"    +
            "@THAT\n"  + 
            "M=D\n"    + # fix THAT

            "@2\n"     +
            "D=A\n"    +
            "@R13\n"   +
            "A=M-D\n"  +
            "D=M\n"    +
            "@THIS\n"  + 
            "M=D\n"    + # fix THIS
            
            "@3\n"     +
            "D=A\n"    +
            "@R13\n"   +
            "A=M-D\n"  +
            "D=M\n"    +
            "@ARG\n"   + 
            "M=D\n"    + # fix ARG
                        
            "@4\n"     +
            "D=A\n"    +
            "@R13\n"   +
            "A=M-D\n"  +
            "D=M\n"    +
            "@LCL\n"   + 
            "M=D\n"    + # fix LCL

            "@R14\n"   +
            "A=M\n"    +
            "0;JMP\n"   # jump to caller        
        )
    
    ############################################################