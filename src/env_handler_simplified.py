import gymnasium  as gym
from gymnasium.experimental.wrappers import FlattenObservationV0
from gymnasium.envs.registration import register
from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env

import argparse

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
        type=RangedInt('steps', 1, 100000),
        help="number of total timesteps (1-100000)")
    args = parser.parse_args()

    return args.steps




# Register the environment
gym.register(
    id='YOS-v0',
    entry_point='envs.yos_env_simplified:YosEnvSimplified',
    kwargs={'render_mode': 'None'}
)

timesteps = parse_arguments()

env = gym.make("YOS-v0")
print (env.observation_space.shape)
env = FlattenObservationV0(env)
print (env.observation_space.shape)


model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=timesteps)
model.save("a2c_yos_env")
del model 
model = A2C.load("a2c_yos_env")
obs = env.reset()


while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    print(rewards)
    env.render("human")

