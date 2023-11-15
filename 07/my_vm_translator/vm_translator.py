import os
from vm_parser import *
from mapper import *
from syntax_error import *

class Translator:
    def __init__(self, vm_file, id_generator):
        self.unit_filename = os.path.basename(vm_file)[:-3] # remove extension .vm
        self.unit_pathname = vm_file
        self.current_function = 'global'
        self.current_lineno = 0
        self.mapper = Mapper(id_generator)

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
                    asm = asm + self.line_tokens_to_asm(tokens) + "\n"
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
                full_label_name = (self.unit_filename + "." + 
                    self.current_function + "$" + tokens[1]) 
                return self.mapper.build_label_asm(full_label_name)
            
            ############################################################
            elif tokens[0] == 'goto':
                if len(tokens) != 2 or tokens[1][0].isnumeric():
                    self.fatal_error("wrong goto syntax")
                # we need to go to a label with the following syntax:
                # filename.current_func$label_name
                full_label_name = (self.unit_filename + "." + 
                    self.current_function + "$" + tokens[1]) 
                return self.mapper.build_goto_asm(full_label_name)
            
            ############################################################
            elif tokens[0] == 'if-goto':
                if len(tokens) != 2 or tokens[1][0].isnumeric():
                    self.fatal_error("wrong if-goto syntax")
                # we need to go to a label with the following syntax:
                # filename.current_func$label_name
                full_label_name = (self.unit_filename + "." + 
                    self.current_function + "$" + tokens[1]) 
                return self.mapper.build_goto_asm(full_label_name)
            
            ############################################################            
            elif tokens[0] == 'function':
                return f"TODO {tokens[0]}\n"
            
            ############################################################  
            elif tokens[0] == 'call':
                return f"TODO {tokens[0]}\n"

            ############################################################  
            elif tokens[0] == 'return':
                return f"TODO {tokens[0]}\n"

            ############################################################  
            else:
                self.fatal_error(f"unknown token '{tokens[0]}'")
        except SyntaxError as e:
            self.fatal_error(e.descr)