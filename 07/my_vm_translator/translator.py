import argparse
import os
from vm_parser import Parser
from vm_generator import Generator

def isFile(arg):
    if not os.path.exists(arg) and not os.path.isfile(arg):
        raise TypeError()
    return arg

arg_parser = argparse.ArgumentParser(prog="HACK assembler")
arg_parser.add_argument('-vmfile',
                         type=isFile, 
                         help="vm file to process",
                         dest="vmfile",
                         required=True
                         )
arg_parser.add_argument('-ofile',
                         help="path to out file",
                         default="a.asm",
                         dest="ofile"
                         )

args = arg_parser.parse_args()
# open the file and parse each line individually
source = open(args.vmfile, "rt")

source_line = 0
parser = Parser()
gen = Generator()

with open(args.ofile, mode="wt", encoding='ISO-8859-1') as out:
    for line in source:
        source_line += 1
        tokens = parser.parse_line(source_line, line.lower())
        if len(tokens) > 0:
            # print(tokens)
            asm = gen.line_tokens_to_asm(source_line, tokens)
            # print(asm)
            out.write(asm + "\n")