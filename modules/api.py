import sys
import pickle
import io
# from clingo.symbol import Number
from clingo.application import Application, clingo_main
from modules.convert import convert_to_clingo
from modules.actionlist import build_action_list, build_context_from_save
from clingo import Control, Number, String, Function
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
                        if not program_name in program_names:
                            program_names.append(program_name)
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"An error occurred while reading {filename}: {e}")
    
    if not "base" in program_names:
        program_names.append("base")
    program_names.sort()
    return program_names

def output_conversion(output, output_files):
    # this is just a function to convert output into into correct flatland actions

    ctl = Control(["0"])
    
    # load input
    for o in output_files:
        ctl.load(o)
    for a in output[0]:
        ctl.add("base", [], str(a) + ".")

    ctl.ground([("base", [])])

    models = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            models.append(model.symbols(shown=True))

    return models

class FlatlandPlan(Application):
    """ takes an environment and a set of primary encodings """
    program_name = "flatland"
    version = "1.0"

    def __init__(self, env, actions, supress_env=False, output_files=None):
        self.env = env
        self.actions = actions
        self.action_list = None
        self.save_context = None
        self.supress_env = supress_env
        self.stats = None
        self.output_files = output_files

    def get(self, val, default):
        return val if val != None else default

    def main(self, ctl, files):
        ctl.configuration.solve.models="-1"
        thy = ClingoDLTheory()
        thy.register(ctl)

        # the loading of the encodings and facts
        with ProgramBuilder(ctl) as bld:
            # add env
            if not self.supress_env:
                parse_string("#program base." + convert_to_clingo(self.env), lambda ast: thy.rewrite_ast(ast, bld.add))
            # add encoding
            parse_files(files, lambda ast: thy.rewrite_ast(ast, bld.add))
            # add actions
            if self.actions is not None:
                parse_string("#program base." + "".join(self.actions), lambda ast: thy.rewrite_ast(ast, bld.add))
        
        imin   = self.get(ctl.get_const("imin"), Number(0))
        imax   = ctl.get_const("imax")
        istop  = self.get(ctl.get_const("istop"), String("SAT"))

        step, ret = 0, None
        models = []
        while ((imax is None or step < imax.number) and
            (step == 0 or step < imin.number or (
                (istop.string == "SAT"     and not ret.satisfiable) or
                (istop.string == "UNSAT"   and not ret.unsatisfiable) or 
                (istop.string == "UNKNOWN" and not ret.unknown)))):
            parts = []
            parts.append(("check", [Number(step)]))
            if step > 0:
                ctl.release_external(Function("query", [Number(step-1)]))
                parts.append(("step", [Number(step)]))
            else:
                parts.append(("base", []))
            ctl.ground(parts)
            thy.prepare(ctl)
            ctl.assign_external(Function("query", [Number(step)]), True)
            with ctl.solve(yield_=True, on_model=thy.on_model) as handle:
                for model in handle:
                    models.append(model.symbols(shown=True, theory=True))
                ret = handle.get()
            step += 1

        self.stats = ctl.statistics
        if self.output_files:
            models = output_conversion(models,self.output_files)
        self.action_list = build_action_list(models)
        self.save_context = build_context_from_save(models)

# let's see later whether we even need this
class FlatlandReplan(Application):
    """ takes an environment, a set of secondary encodings, and additional context """
    program_name = "flatland"
    version = "1.0"

