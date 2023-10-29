import argparse
import os
from as_parser import *
from symbols import Symbols

def isFile(arg):
    if not os.path.exists(arg) and not os.path.isfile(arg):
        raise TypeError()
    return arg

arg_parser = argparse.ArgumentParser(prog="HACK assembler")
arg_parser.add_argument('asmfile',
                         type=isFile, help="asm file to process")
arg_parser.add_argument('-ofile',
                         help="path to out file",
                         default="a.hack",
                         nargs=1,
                         dest="ofile"
                         )

args = arg_parser.parse_args()
# open the file and parse each line individually
source = open(args.asmfile, "rt")

symbols = Symbols
sym_table = symbols.table
parser = Parser()
source_line = 0
binary_line = 0
with open(args.ofile, mode="wt", encoding='ISO-8859-1') as out:
    for line in source:
        source_line += 1
        tokens = parser.parse_line(source_line, line)
        if len(tokens) != 0:
            # print(source_line, line, end="")
            # print(source_line, tokens)
            if (tokens[0] == 'L'):
                # we got a label
                # check if symbol is known
                if tokens[1] in sym_table:
                    # error
                    parser.fatal_error(source_line, "label prevously defined")
                else:
                    # add label to symbol table
                    sym_table[tokens[1]] = binary_line
            elif (tokens[0] == 'A'):
                # we got an A instruction
                # do we have a symbol or a decimal address value?
                if isinstance(tokens[1], int):
                    # set value of address to binary form               
                    instruction = "0" + bin(tokens[1])[2:].zfill(15)
                    out.write(instruction + "\n")
                else:
                    # we got a symbol, check symbol table
                    if tokens[1] in sym_table:
                        # already known
                        sym_val = sym_table[tokens[1]]
                        instruction = "0" + bin(sym_val)[2:].zfill(15)
                        out.write(instruction + "\n")
                    else:
                        # whoops, defer translation
                        symbols.undef_table[binary_line] = tokens[1];
                        out.write("0XXXXXXXXXXXXXXX\n")
                binary_line += 1
            elif tokens[0] == 'C':
                # we got a C instruction
                # ['C', dest, comp, jump]
                instruction = "111"
                instruction += symbols.valid_comps[tokens[2]]
                instruction += symbols.valid_dests[tokens[1]]
                instruction += symbols.valid_jumps[tokens[3]]
                out.write(instruction + "\n")
                binary_line += 1
    # source parsed
    # fill remaining unknown symbols
    addr_unknown_sym = 16
    for addr in symbols.undef_table:
        sym = symbols.undef_table[addr]
        if not sym in sym_table:
            # set its value
            # dunno why we must start from 16, why not use binary_line?
            sym_table[sym] = addr_unknown_sym
            addr_unknown_sym += 1
        # write value
        out.seek((16 + 1) * addr)
        out.write("0" + bin(sym_table[sym])[2:].zfill(15) + "\n")