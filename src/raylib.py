import argparse
import gymnasium as gym

from ray import tune
from envs import yos_env
from envs import yos_env_simplified
import ray
from ray.rllib.algorithms.algorithm import Algorithm

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



    args = parser.parse_args()
    

    return args.algo_name, args.render, args.iterations, args.checkpoint_load , args.checkpoint_save, args.env_num, args.gpu_num, args.simple


class Raylib_Generic():

    def __init__(self,path, algo_name, env_num=1, gpu_num=0, env_class = yos_env.YosEnv):
        self.path = path
        self.algo_name = algo_name
        self.env_num = env_num
        self.gpu_num = gpu_num
        self.dirname = "/v5/"
        self.env_class = env_class

    def setup(self, algo_name):
        
        if algo_name == "ppo":
            self.config = PPOConfig()
            self.config = self.config.training(gamma=0.9, lr=0.01, kl_coeff=0.3,train_batch_size=128)
            self.config = self.config.env_runners(num_env_runners=self.env_num)

        elif algo_name == "cql":
            self.config = CQLConfig().training(gamma=0.9, lr=0.01)
            self.config = self.config.env_runners(num_env_runners=self.env_num)

        elif algo_name == "appo":
            self.config = APPOConfig().training(lr=0.01, grad_clip=30.0, train_batch_size=50)
            self.config = self.config.env_runners(num_env_runners=self.env_num)

        elif algo_name == "impala":
            self.config = ImpalaConfig()
            self.config = self.config.training(lr=0.0003, train_batch_size=512)
            self.config = self.config.env_runners(num_env_runners=self.env_num)

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
            self.config = self.config.env_runners(num_env_runners=self.env_num)

        elif algo_name == "sac":
            self.config = SACConfig().training(gamma=0.9, lr=0.01, train_batch_size=32)
            self.config = self.config.env_runners(num_env_runners=self.env_num)

        if self.gpu_num:
            self.config = self.config.resources(num_gpus=0.0001)
            self.config = self.config.env_runners(num_gpus_per_env_runner=((float(self.gpu_num) - 0.0001)/self.env_num))  
        else:
            self.config = self.config.resources(num_gpus=0)
            self.config = self.config.learners(num_gpus_per_learner=0)
            self.config = self.config.env_runners(num_gpus_per_env_runner=0)

        self.algo = self.config.build(env=self.env_class)

        

    def train(self, iterations, path):
        for i in range(iterations):
            self.algo.train()
        self.algo.save(checkpoint_dir= self.path + self.algo_name + self.dirname + path)


    def load(self, path):
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
        self.algo.restore(self.path + self.algo_name + self.dirname + path)


        #self.algo = Algorithm.from_checkpoint(self.path + algo_name + "/v2-multiple/" + path)

    def test(self):

        env = self.env_class()

        # run until episode ends
        episode_reward = 0
        done = False
        obs , _ = env.reset()
        while not done:
            action = self.algo.compute_single_action(obs)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward

        print(env.game_scene._score_manager.score)
        return episode_reward, reward
    

if __name__=="__main__":
    algo_name, render, iterations, checkpoint_load , checkpoint_save, env_num, gpu_num, simple = parse_arguments()
    if simple:
        agent = Raylib_Generic("/home/simon/youre-the-os/agent-results/", algo_name, env_num, gpu_num, yos_env_simplified.YosEnvSimplified)
    else:
        agent = Raylib_Generic("/home/simon/youre-the-os/agent-results/", algo_name, env_num, gpu_num)

    
    if render:
        agent.load(checkpoint_load)
        agent.test()

    elif checkpoint_load:
        agent.load(checkpoint_load)
        agent.train(iterations, checkpoint_save)

    elif checkpoint_save:
        agent.setup(algo_name)
        agent.train(iterations, checkpoint_save)