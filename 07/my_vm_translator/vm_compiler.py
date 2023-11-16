import argparse
import os
from vm_translator import Translator
from identifier_generator import *

def FileOrDir(arg):
    if not os.path.exists(arg) or (not os.path.isfile(arg) and not os.path.isdir(arg)):
        raise TypeError()
    return arg

arg_parser = argparse.ArgumentParser(prog="HACK assembler")
arg_parser.add_argument('-path',
                         type=FileOrDir, 
                         help="vm file or vm directory to process",
                         dest="inputs",
                         required=True
                         )
arg_parser.add_argument('-out',
                         help="path to out file",
                         dest="out"
                         )

args = arg_parser.parse_args()
if os.path.isdir(args.inputs):
    sources = [f for f in os.listdir(args.inputs) if f.endswith(".vm") and not f.startswith(".")]
    try:
        # make Sys.vm appear at the beginning if present
        sources.remove("Sys.vm")
        sources.insert(0, "Sys.vm")
    except ValueError:
        pass
    sources = [os.path.join(args.inputs, f) for f in sources]
    outfilename = (args.inputs) + ".asm"
else:
    sources = [args.inputs]
    outfilename = (args.inputs)[:-2] + "asm"

id_generator = IdGenerator()
trans = Translator(id_generator, True)

with open(outfilename, mode="wt", encoding='ISO-8859-1') as out:
    out.write(trans.get_bootstrap_code())
    for source_filename in sources:
        print(f"Compiling {source_filename}")
        asm = trans.translate(source_filename)
        out.write(f"\n// ##### obj dump: {source_filename} ##### \n" + 
                  asm + f"// ##### eof: {source_filename} ##### \n")