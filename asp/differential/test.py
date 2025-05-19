
import sys
import pickle
import io
from clingo import Control
from clingo.symbol import Number, Function
from clingo.application import Application, clingo_main

from clingo.ast import parse_string, parse_files, ProgramBuilder
from clingodl import ClingoDLTheory

def extract_program_names(filenames):
    program_names = []
    
    for filename in filenames:
        try:
            with open(filename, 'r') as file:
                for line in file:
                    # Check if the line starts with '#program '
                    if line.startswith('#program '):
                        # Extract the program name by stripping the line
                        program_name = line[len('#program '):].strip()[:-1]
                        program_names.append(program_name)
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"An error occurred while reading {filename}: {e}")
    
    program_names.sort()
    return program_names


def main(files):
    previous = ""

    for p in extract_program_names(files):
        ctl = Control(['0'])
        thy = ClingoDLTheory()
        thy.register(ctl)
        # add encodings
        for f in files: 
            with ProgramBuilder(ctl) as bld:
                parse_files([f], lambda ast: thy.rewrite_ast(ast, bld.add))
        
        previous += p + "_mode."
        if previous:
            with ProgramBuilder(ctl) as bld:
                parse_string("#program " + p + "." + previous, lambda ast: thy.rewrite_ast(ast, bld.add))
        
        ctl.ground([(p, [])])
        thy.prepare(ctl)

        # solve and save models
        models = []
        with ctl.solve(yield_=True, on_model=thy.on_model) as handle:
            for model in handle:
                models.append(model.symbols(shown=True,theory=True))
    
        previous = ""
        for a in models[-1]:
            previous += str(a) + "."
    
    return previous

print(main(["test/example.lp"]))