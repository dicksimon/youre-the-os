import gymnasium  as gym
from gymnasium.envs.registration import register

# Register the environment
gym.register(
    id='YOS-v0',
    entry_point='envs.yos_env:YosEnv'
)

env = gym.make('YOS-v0');
obs = env.reset()

print(env.observation_space.sample())
print(env.action_space.sample())