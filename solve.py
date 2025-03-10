
# standard packages
import csv
import sys
import warnings
import os 
import time
import pickle
import json
import time
from argparse import ArgumentParser, Namespace
import importlib.util

# custom modules
from modules.api import FlatlandPlan
from modules.convert import convert_malfunctions_to_clingo, convert_formers_to_clingo, convert_futures_to_clingo

# clingo
import clingo
from clingo.application import Application, clingo_main

# rendering visualizations
from flatland.utils.rendertools import RenderTool
from flatland.envs.rail_env import TrainState, RailEnvActions
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont


class MalfunctionManager():
    def __init__(self, num_agents):
        self.num_agents = num_agents
        self.malfunctions = []

    def get(self) -> list:
        """ get the list of malfunctions """
        return(self.malfunctions)

    def deduct(self) -> None:
        """ decrease the duration of each malfunction by one and delete expired malfunctions """
        malfunctions_to_remove = []
        for i, malf in enumerate(self.malfunctions):
            self.malfunctions[i] = (self.malfunctions[i][0], self.malfunctions[i][1] - 1)
            if self.malfunctions[i][1] == 0:
                malfunctions_to_remove.append(i)
        
        # delete expired malfunctions
        for i in sorted(malfunctions_to_remove, reverse=True):
            del self.malfunctions[i]

    def check(self, info) -> set:
        """ check current state of the env for new malfunctions """
        malfunctioning_info = info['malfunction']
        malfunctioning_trains = {train for train, duration in malfunctioning_info.items() if duration > 0}
        existing = {malf[0] for malf in self.malfunctions}
        new = malfunctioning_trains.difference(existing)

        # add new ones to malfunctions
        for train in new:
            self.malfunctions.append((train, malfunctioning_info[train]))

        return(new)


class SimulationManager():
    def __init__(self,env,primary,secondary=None):
        self.env = env
        self.primary = primary
        if secondary is None:
            self.secondary = primary 
        else:
            self.secondary = secondary

        self.save_context = None

    def build_actions(self) -> list:
        """ create initial list of actions """
        # pass env, primary
        app = FlatlandPlan(self.env, None)
        clingo_main(app, self.primary)
        self.save_context = app.save_context
        return(app.action_list, app.stats)

    def provide_context(self, actions, timestep, malfunctions) -> str:
        """ provide additional facts when updating list """
        # provides malfunction information as well as previously saved atoms
        malfunction = convert_malfunctions_to_clingo(malfunctions, timestep)
        saved = self.save_context
        return (malfunction + saved)

    def update_actions(self, context) -> list:
        """ update list of actions following malfunction """
        # pass env, secondary, context
        app = FlatlandPlan(self.env, context, supress_env=True)
        clingo_main(app, self.secondary)
        self.save_context = app.save_context
        return(app.action_list, app.stats)


class OutputLogManager():
    def __init__(self) -> None:
        self.logs = []

    def add(self,info) -> None:
        """ add info from a timestep to the log """
        self.logs.append(info)

    def save(self,filename) -> None:
        """ save output log to local drive """
        #with open(f"output/{filename}/paths.json", "w") as f:
        #    f.write(json.dumps(self.logs))
        with open(f"output/{filename}/paths.csv", "w") as f:
            f.write("agent;timestep;position;direction;status;given_command\n")
            for log in self.logs:
                f.write(log)

def check_params(par):
    """
    verify that all parameters exist before proceedingd
    """
    required_params = {
        "primary": list
        #"secondary": list
    }

    # check that all required parameters exist and have the correct type
    for param, expected_type in required_params.items():
        if not hasattr(par, param):
            raise ValueError(f"Required parameter '{param}' is missing from the params module")
            
        else:
            # check for correct types
            value = getattr(par, param)
        
            if not isinstance(value, expected_type):
                raise TypeError(f"Parameter '{param}' should be of type {expected_type.__name__}, but got {type(value).__name__}")

    return True


def get_args():
    """ capture command line inputs """
    parser = ArgumentParser()
    parser.add_argument('enc', type=str, default='', nargs=1, help='the encoding as a .py file')
    parser.add_argument('env', type=str, default='', nargs=1, help='the Flatland environment as a .pkl file')
    parser.add_argument('--no-render', action='store_true', help='if included, run the Flatland simulation but do not render a GIF')
    parser.add_argument('--no-horizon', action='store_true', help='if included, run the Flatland simulation with no instance ending')
    return(parser.parse_args())

def save_stats(instance_name, primary, secondary, width, height, targets, malfunction_rate, seed, trains, horizon, timesteps, primary_stats, secondary_stats, success, reason, filename="output/log.csv"):
    row = [
        instance_name,
        primary,
        secondary,
        width,
        height,
        targets,
        malfunction_rate,
        seed,
        trains,
        horizon,
        timesteps,
        primary_stats,
        secondary_stats,
        success,
        reason
    ]
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            header = [
                'Instance',
                'Primary',
                'Secondary',
                'Width',
                'Height',
                'Targets',
                'Malfunction Rate',
                'Seed',
                'Trains',
                'Horizon',
                'Timesteps',
                'Primary Stats',
                'Secondary Stats',
                'Success',
                'Reason'
            ]
            writer.writerow(header)
        writer.writerow(row)

def entry_exists(instance_name, primary, secondary, horizon, filename="output/log.csv"):
    if not os.path.isfile(filename):
        return False

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == instance_name and row[1] == str(primary) and row[2] == str(secondary):
                if horizon == None:
                    if row[9] == "":
                        return True
                else:
                    print
                    if row[9] == str(horizon):
                        return True
    return False


def import_module(module_path):
    spec = importlib.util.spec_from_file_location("module.name", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = module
    spec.loader.exec_module(module)
    return module


def main():
    csv.field_size_limit(sys.maxsize)
    start_time = time.time()
    failure_reason = None
    # dev test main
    args: Namespace = get_args()
    env = pickle.load(open(args.env[0], "rb"))
    params = import_module(args.enc[0])
    no_render = args.no_render
    no_horizon = args.no_horizon

    # create manager objects
    mal = MalfunctionManager(env.get_num_agents())
    if hasattr(params,"secondary") and params.secondary != []:
        sim = SimulationManager(env, params.primary, params.secondary)
    else:
        sim = SimulationManager(env, params.primary, None)
    log = OutputLogManager()

    if no_horizon:
        if entry_exists(args.env[0], params.primary, params.secondary, None):
            raise Exception("Already evaluated.")
    else:
        if entry_exists(args.env[0], params.primary, params.secondary, env._max_episode_steps):
            raise Exception("Already evaluated.")

    # envrionment rendering
    env_renderer = None
    if not no_render:
        env_renderer = RenderTool(env, gl="PILSVG", screen_width=2000, screen_height=2000)
        env_renderer.reset()
        images = []

    # create directory
    os.makedirs("tmp/frames", exist_ok=True)
    action_map = {0:'nothing',1:'move_left',2:'move_forward',3:'move_right',4:'wait'}
    state_map = {0:'waiting', 1:'ready to depart', 2:'malfunction (off map)', 3:'moving', 4:'stopped', 5:'malfunction (on map)', 6:'done'}
    dir_map = {0:'n', 1:'e', 2:'s', 3:'w'}

    actions, primary_stats = sim.build_actions()
    secondary_stats = []
    if no_horizon:
        env._max_episode_steps = None

    timestep, end = 0, False
    if actions == None or actions == []:
        failure_reason = "Unsatisfieable"
        success = False
    else:
        while len(actions) > timestep:
            if time.time() - start_time > 3600:
                failure_reason = "Exceeded 60 Minutes"
                break
            # add to the log
            for a in actions[timestep]:
                log.add(f'{a};{timestep};{env.agents[a].position};{dir_map[env.agents[a].direction]};{state_map[env.agents[a].state]};{action_map[actions[timestep][a]]}\n')

            current = actions[timestep]
            for a in current:
                if not env.agents[a].position and current[a] == RailEnvActions.STOP_MOVING:
                    current[a] = RailEnvActions.DO_NOTHING

            print(timestep)
            _, _, done, info = env.step(current)

            # end if simulation is finished
            if done['__all__'] and timestep < len(actions)-1:
                end = True
                warnings.warn('Simulation has reached its end before actions list has been exhausted.')
                break

            # check for new malfunctions
            new_malfs = mal.check(info)

            if len(new_malfs) > 0:
                context = sim.provide_context(actions, timestep, mal.get())
                actions, s = sim.update_actions(context)
                secondary_stats.append(s.copy())
                if actions == None or actions == []:
                    failure_reason = "Unsatisfieable"
                    break
                for a in actions[timestep]:
                    env.agents[a].action_saver.saved_action = None

            mal.deduct() #??? where in the loop should this go - before context?
            
            # render an image
            filename = 'tmp/frames/flatland_frame_{:04d}.png'.format(timestep)
            if env_renderer is not None:
                env_renderer.render_env(show=True, show_observations=False, show_predictions=False)
                env_renderer.gl.save_image(filename)
                env_renderer.reset()

                # add red numbers in the corner
                with Image.open(filename) as img:
                    draw = ImageDraw.Draw(img)
                    padding = 10
                    font_size = int(min(img.width, img.height) * 0.10)
                    try:
                        font = ImageFont.truetype("modules/LiberationMono-Regular.ttf", font_size)
                    except IOError:
                        font = ImageFont.load_default()
                    
                    # prepare text
                    text = f"{timestep}"
                    size = font.getbbox(text)
                    text_width = size[2]-size[0]
                    text_position = (img.width - text_width - padding, padding)
                    
                    # draw text borders
                    x, y = text_position
                    border_color = "black"
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        draw.text((x + dx, y + dy), text, fill=border_color, font=font)
                    
                    # draw text
                    draw.text(text_position, text, fill="red", font=font)
                    img.save(filename)

                images.append(imageio.imread(filename))

            timestep = timestep + 1
            if timestep >= 10000:
                warnings.warn("What the hell is wrong with you. Why are you still running?")
                failure_reason = "Reached 10000 Timesteps"
                break
            if env._elapsed_steps == env._max_episode_steps:
                failure_reason = "Not finished on time."
                break
            if all(info["state"][i] == TrainState.DONE for i in info["state"]):
                break

        # get time stamp for gif and output log
        stamp = time.time()
        os.makedirs(f"output/{stamp}", exist_ok=True)

        # combine images into gif
        if not no_render:
            imageio.mimsave(f"output/{stamp}/animation.gif", images, format='GIF', loop=0, duration=240)

        # save output log
        log.save(stamp)

        success = all(info["state"][i] == TrainState.DONE for i in info["state"])
    
    if failure_reason == None and not success:
        if end:
            failure_reason = "Ended to Early"
        else:
            failure_reason = "Mismatching Actions"

    # save stats
    save_stats(
        args.env[0],
        params.primary,
        params.secondary,
        env.width,
        env.height,
        len(set(agent.target for agent in env.agents)),
        env.malfunction_generator.MFP.malfunction_rate,
        env._seed()[0],
        env.number_of_agents,
        env._max_episode_steps,
        env._elapsed_steps,
        primary_stats,
        secondary_stats,
        success,
        failure_reason
        )
    
    if success:
        print("Successful run!")
    else:
        print(f"Failed due to: {failure_reason}.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        warnings.warn(str(e))
