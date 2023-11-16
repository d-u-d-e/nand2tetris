import os
from vm_parser import *
from asm_builder import *
from syntax_error import *

class Translator:
    def __init__(self, vm_file, id_generator: IdGenerator):
        self.unit_filename = os.path.basename(vm_file)[:-3] # remove extension .vm
        self.unit_pathname = vm_file
        self.current_function = 'global'
        self.current_lineno = 0
        self.idgen = id_generator
        self.mapper = AsmBuilder(id_generator)

    def fatal_error(self, description):
        print(f"error in file: '{self.unit_filename}\n'" +  
              f"line: {self.current_lineno}")
        print(description)
        exit(1)

    def translate(self):
        # returns an asm string
        parser = Parser()
        self.current_lineno = 0
        asm = ""
        with open(self.unit_pathname, mode="rt", encoding='ISO-8859-1') as in_file:
            for line in in_file:
                self.current_lineno += 1
                tokens = parser.parse_line(self.current_lineno, line)
                if len(tokens) > 0:
                    # print(tokens)
                    asm = asm + self.line_tokens_to_asm(tokens)
        return asm
    
    def line_tokens_to_asm(self, tokens):
        try:
            if (tokens[0] == 'add' or tokens[0] == 'sub' 
                or tokens[0] == 'and' or tokens[0] == 'or'):

                if tokens[0] == 'add':
                    op = '+'
                elif tokens[0] == 'sub':
                    op = '-'
                elif tokens[0] == 'or':
                    op = '|'
                else:
                    op = '&'
                return self.mapper.build_binary_op_asm(op)
            
            ############################################################
            elif tokens[0] == 'neg' or tokens[0] == 'not':
                op = '-' if tokens[0] == 'neg' else '!'
                return self.mapper.build_unary_op_asm(op)
            
            ############################################################
            elif tokens[0] == 'eq' or tokens[0] == 'gt' or tokens[0] == 'lt':
                return self.mapper.build_cmp_op_asm(tokens[0])
            
            ############################################################
            elif tokens[0] == 'push' or tokens[0] == 'pop':
                if len(tokens) != 3:
                    self.fatal_error(f"wrong {tokens[0]} syntax")
                segment = tokens[1]
                value = tokens[2]
                if not value.isnumeric():
                    self.fatal_error("segment value not integer")
                if tokens[0] == 'push':
                    return self.mapper.build_push_op_asm(self.unit_filename, segment, value)
                else:
                    return self.mapper.build_pop_op_asm(self.unit_filename, segment, value) 
                
            ############################################################            
            elif tokens[0] == 'label':
                if len(tokens) != 2 or tokens[1][0].isnumeric():
                    self.fatal_error("wrong label syntax")
                # we need to generate a label with the following syntax:
                # filename.current_func$label_name
                full_label_name = self.current_function + "$" + tokens[1]
                return self.mapper.build_label_asm(full_label_name)
            
            ############################################################
            elif tokens[0] == 'goto':
                if len(tokens) != 2 or tokens[1][0].isnumeric():
                    self.fatal_error("wrong goto syntax")
                # we need to go to a label with the following syntax:
                # filename.current_func$label_name
                full_label_name = self.current_function + "$" + tokens[1]
                return self.mapper.build_goto_asm(full_label_name)
            
            ############################################################
            elif tokens[0] == 'if-goto':
                if len(tokens) != 2 or tokens[1][0].isnumeric():
                    self.fatal_error("wrong if-goto syntax")
                # we need to go to a label with the following syntax:
                # filename.current_func$label_name
                full_label_name = self.current_function + "$" + tokens[1]
                return self.mapper.build_goto_asm(full_label_name)
            
            ############################################################            
            elif tokens[0] == 'function':
                # we have 'function fName nVars', so 3 tokens
                if len(tokens) != 3 or tokens[1][0].isnumeric() or not tokens[2].isnumeric():
                    self.fatal_error("wrong function syntax")
                # the func label is formatted as
                # filename.current_func
                self.current_function = tokens[1]
                return self.mapper.build_function_asm(tokens[1], int(tokens[2]))
            
            ############################################################  
            elif tokens[0] == 'call':
                # we have 'call fName nArgs', so 3 tokens
                if len(tokens) != 3 or tokens[1][0].isnumeric() or not tokens[2].isnumeric():
                    self.fatal_error("wrong function syntax")

                ret_label = (tokens[1] + 
                    "$ret." + str(self.idgen.get_unique_id()))
                
                return self.mapper.build_call_asm(tokens[1], int(tokens[2]), ret_label)

            ############################################################  
            elif tokens[0] == 'return':
                if len(tokens) != 1:
                    self.fatal_error("wrong return syntax")
                return self.mapper.build_return_asm(self.current_function)

            ############################################################  
            else:
                self.fatal_error(f"unknown token '{tokens[0]}'")
        except SyntaxError as e:
            self.fatal_error(e.descr)