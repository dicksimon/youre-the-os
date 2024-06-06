import gymnasium as gym
import ray
from ray.rllib.algorithms import ppo
from envs import yos_env_simplified

algo = (
    ppo.PPOConfig()
    .env_runners(num_env_runners=1)
    .resources(num_gpus=0)
    .environment(env=yos_env_simplified.YosEnvSimplified).
    build()
)


for i in range(10):
    result = algo.train()
    print(result)

    if i % 5 == 0:
        checkpoint_dir = algo.save().checkpoint.path
        print(f"Checkpoint saved in directory{checkpoint_dir}")

