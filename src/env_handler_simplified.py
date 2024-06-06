import argparse
import os

import gymnasium  as gym
from gymnasium.experimental.wrappers import FlattenObservationV0
from gymnasium.envs.registration import register
from stable_baselines3 import A2C
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize, DummyVecEnv
from stable_baselines3.common.monitor import Monitor



class RangedInt:
    """Type validator for argparse"""
    def __init__(self, name, vmin, vmax):
        self._name = name
        self._min = vmin
        self._max = vmax

    def __call__(self, arg):
        ival = int(arg)
        if ival < self._min or ival > self._max:
            raise ValueError("not in range")
        return ival

    def __repr__(self):
        """for argparse"""
        return f"{self._name} ({self._min}-{self._max})"


def parse_arguments():

    parser = argparse.ArgumentParser(
                prog="env_handler",
                description="run gymnasium enviroment ")

    # further customize difficulty
    parser.add_argument('--steps',
        type=RangedInt('steps', 1, 100000000),
        help="number of total timesteps (1-100000000)")

    parser.add_argument('--render',action='store', help="render mode", required=False)
    parser.add_argument('--filestore',action='store', help="filename to store model", required=True)
    parser.add_argument('--fileload',action='store', help="filename to load model", required=False)
    args = parser.parse_args()

    return args.steps, args.render, args.filestore,  args.fileload

if __name__=="__main__":

    init = True
    timesteps,  render, filestore, fileload = parse_arguments()

    path = "/home/simon/youre-the-os/output/"

    log_dir = path + filestore + "-monitor"
    os.makedirs(log_dir, exist_ok=True)

    gym.register(
        id='YOS',
        entry_point='envs.yos_env_simplified:YosEnvSimplified',
        kwargs={'render_mode': 'None'}
    )

    if not fileload:
        env = gym.make("YOS")
        env = Monitor(env, log_dir)
        model = A2C("MultiInputPolicy", env, device="cpu")

    else:
        if render:
            env=gym.make("YOS", render_mode= 'human')
        else:
            env=gym.make("YOS")
        env = Monitor(env,log_dir)
        model = PPO.load(path + fileload, env)

    model.learn(total_timesteps=timesteps)
    model.save(path + filestore)
    del model
 




