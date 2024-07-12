import argparse
import gymnasium as gym
import numpy as np

from envs import yos_env
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.cql import CQLConfig
from ray.rllib.algorithms.appo import APPOConfig
from ray.rllib.algorithms.impala import ImpalaConfig
from ray.rllib.algorithms.dqn.dqn import DQNConfig
from ray.rllib.algorithms.sac.sac import SACConfig

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
    parser.add_argument('--iterations',
        type=RangedInt('iterations', 1, 100000000),
        help="number of total timesteps (1-100000000)", required=False)
    parser.add_argument('--env_num',
        type=RangedInt('env_num', 1, 32),
        help="number of envs (1-32)", required=False)
    parser.add_argument('--gpu_num',
        type=RangedInt('gpu_num', 0, 32),
        help="number of gpus (0-32)", required=False)
    parser.add_argument('--render',action='store', help="agent mode", required=False)
    parser.add_argument('--algo_name',action='store', help="algorithm to use", required=True)
    parser.add_argument('--checkpoint_load',action='store', help="checkpoint load name", required=False)
    parser.add_argument('--checkpoint_save',action='store', help="checkpoint save name", required=False)
    parser.add_argument('--simple',action='store', help="use simplified env", required=False)
    parser.add_argument('--reward',action='store', help="use simplified env", required=False)



    args = parser.parse_args()
    

    return args.algo_name, args.render, args.iterations, args.checkpoint_load , args.checkpoint_save, args.env_num, args.gpu_num, args.simple, args.reward


class Raylib_Generic():

    def __init__(self,path, algo_name, env_num=1, gpu_num=0, env_class = yos_env.YosEnv, reward_strategy = "base"):
        self.path = path
        self.algo_name = algo_name
        self.env_num = env_num
        self.gpu_num = gpu_num
        self.env_class = env_class
        self.reward_strategy = f"/{reward_strategy}/"
        

    def setup(self, algo_name):
        
        if algo_name == "ppo":
            self.config = PPOConfig()
            self.config = self.config.training(gamma=0.9, lr=0.01, kl_coeff=0.3,train_batch_size=128)


        elif algo_name == "cql":
            self.config = CQLConfig().training(gamma=0.9, lr=0.01)

        elif algo_name == "appo":
            self.config = APPOConfig().training(lr=0.01, grad_clip=30.0, train_batch_size=50)


        elif algo_name == "impala":
            self.config = ImpalaConfig()
            self.config = self.config.training(lr=0.0003, train_batch_size=512)

        elif algo_name == "dqn":
            self.config = DQNConfig()
            replay_config = {
                    "type": "MultiAgentPrioritizedReplayBuffer",
                    "capacity": 60000,
                    "prioritized_replay_alpha": 0.5,
                    "prioritized_replay_beta": 0.5,
                    "prioritized_replay_eps": 3e-6,
                }
            self.config = self.config.training(replay_buffer_config=replay_config)

        elif algo_name == "sac":
            self.config = SACConfig().training(gamma=0.9, lr=0.01, train_batch_size=32)

        if self.gpu_num:
            self.config = self.config.resources(num_gpus= self.gpu_num)
            self.config = self.config.env_runners(num_env_runners=self.gpu_num)
            self.config = self.config.env_runners(num_gpus_per_env_runner= 1)  
            self.config = self.config.env_runners(num_envs_per_env_runner = self.env_num) 
        else:
            self.config = self.config.env_runners(num_env_runners=self.env_num)
            self.config = self.config.resources(num_gpus=0)
            self.config = self.config.learners(num_gpus_per_learner=0)
            self.config = self.config.env_runners(num_gpus_per_env_runner=0)

        self.algo = self.config.build(env=self.env_class)

        

    def train(self, iterations, path):
        for i in range(iterations):
            self.algo.train()
            save =  i % 500
            if save == 0:
                self.algo.save(checkpoint_dir= self.path + self.algo_name + self.reward_strategy + path + "/" + str(i))


    def load(self, path):
        self.setup(self.algo_name)
        self.algo.restore(self.path + self.algo_name + self.reward_strategy + path)



    def test(self, path):

        if self.algo_name == "ppo":
            self.config = PPOConfig()
            self.config = self.config.training(gamma=0.9, lr=0.01, kl_coeff=0.3,train_batch_size=128)
        

        elif self.algo_name == "appo":
            self.config = APPOConfig()
            self.config = self.config.training(lr=0.01, grad_clip=30.0, train_batch_size=50)

        elif self.algo_name == "impala":
            self.config = ImpalaConfig()
            self.config = self.config.training(lr=0.0003, train_batch_size=512)

        self.config = self.config.resources(num_gpus=0)
        self.config = self.config.learners(num_gpus_per_learner=0)
        self.config = self.config.env_runners(num_gpus_per_env_runner=0) 
        self.config = self.config.env_runners(num_env_runners=1)
        self.algo = self.config.build(env=self.env_class)
        self.algo.restore(self.path + self.algo_name + self.reward_strategy + path)


        env = self.env_class()

        # run until episode ends
        episode_reward = 0
        done = False
        obs , _ = env.reset()
        while not done:
            action = self.algo.compute_single_action(obs)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward

        return env.game_scene._score_manager.score
    

if __name__=="__main__":
    
    algo_name, render, iterations, checkpoint_load , checkpoint_save, env_num, gpu_num, simple, reward  = parse_arguments()

    
    ending = checkpoint_load.replace("/","")
    
    for episode in range(1,iterations+1):
        f = open("../agent-results/" + algo_name + "-" + ending + reward + "-priority-results.csv", "a")
        agent = Raylib_Generic("/home/simon/youre-the-os/agent-results/", algo_name, env_num, gpu_num, yos_env.YosEnv, reward)
        score = agent.test(checkpoint_load)
        f.write(str(episode) + ";" + str(score) + "\n")
        f.close()
    sys.exit()
