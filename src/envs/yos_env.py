import gymnasium as gym
from gymnasium import spaces
from gymnasium.spaces import  Dict,MultiDiscrete, MultiBinary

import pygame
import numpy as np
from os import path
import sys
import argparse
from enum import Enum
from typing import List

from lib import ai_schedule
from lib import event_manager
from lib.constants import _TIME_TO_UNSTARVE_MS
from scenes.game import Game
from scene_manager import scene_manager
from game_info import TITLE
from window_size import WINDOW_SIZE


FPS = 60

def compile_auto_script():
    return None



class YosEnv(gym.Env):
    metadata = {"render_modes": ["human", "None"], "render_fps": FPS}

    def __init__(self, render_mode="human"):

        self.render_mode = render_mode

        self.event_manager = event_manager

        self.action_space = spaces.MultiDiscrete([57 for _ in range(16)])

        self.observation_space = Dict({
            "exists": MultiBinary(57,),
            "unstarve_time": MultiDiscrete([5 for _ in range(57)]),
            "starvation_level": MultiDiscrete([6 for _ in range(57)]),
            "has_cpu": MultiBinary(57,),
            "waiting_for_io": MultiBinary(57,)
        })


        self.observation_mapping: List[Dict[str, np.ndarray]] = []


    def reset(self, seed=None, options=None):
        
        self.done = False


        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        difficulty_config = {'name': 'Insane',
                            'num_cpus': 16, 'num_processes_at_startup': 42,
                            'num_ram_rows': 4, 'new_process_probability': 1,
                            'io_probability': 0.3}


        pygame.init()
        if self.render_mode == "human":
            pygame.font.init()
            self.screen = pygame.display.set_mode(WINDOW_SIZE)
        else:
            self.screen = None
        self.clock = pygame.time.Clock()
        self.scenes = {}
        self.game_scene = Game(self.screen, self.scenes, difficulty_config, None, standalone=True, ai_mode=True)
        self.scenes['game'] = self.game_scene
        self.game_scene.start()


        self.scene_manager = scene_manager
        self.event_manager.clear_events()
        self.scheduler = ai_schedule.AiSchedule()
        observation = self.get_obs()

        if self.render_mode == "human":

            icon = pygame.image.load(path.join('assets', 'icon.png'))
            pygame.display.set_caption(TITLE)
            pygame.display.set_icon(icon)            
            self.render()
            
        return observation, {}

    def step(self, action): 
        
        observation = self.get_obs()
        self.game_step(action)

        terminated = self.game_scene.game_over
        if terminated:
            self.done = True
            return observation, self.calc_reward(terminated), terminated, False, {}
    
        if self.render_mode == 'human':
            self.render()

        return observation, self.calc_reward(terminated), terminated, False, {}

    
    def get_obs(self):
        exists = np.ones([57], dtype=np.int8)
        unstarve_time = np.zeros([57], dtype=np.int8)
        starvation_level = np.zeros([57], dtype=np.int8)
        has_cpu = np.zeros([57],dtype=np.int8)
        waiting_for_io = np.zeros([57], dtype=np.int8)
             
        for pid in range(57):
            self.scheduler
            if pid not in self.scheduler.processes:
                exists[pid] = 0

            else:
                if pid in self.scheduler.cpus_active:
                    has_cpu[pid] = 1

                if self.scheduler.processes[pid].waiting_for_io:
                    waiting_for_io[pid] = 1


            for job_time in self.scheduler.job_times.keys():
                if pid in self.scheduler.job_times[job_time]:
                    unstarve_time[pid] = (job_time/(0.5 * _TIME_TO_UNSTARVE_MS)) - 1 
                    break

            for level in self.scheduler.starvation.keys():
                if [process for process in self.scheduler.starvation[level] if process[0] == pid]:
                    starvation_level[pid] = level
                    break


        observation = {
            "exists": exists,
            "unstarve_time": unstarve_time,
            "starvation_level": starvation_level,
            "has_cpu": has_cpu,
            "waiting_for_io": waiting_for_io
        }


        return observation


    def game_step(self, action):
        self.scheduler.handle_events(self.event_manager.get_events())
        self.event_manager.clear_events()
        self.scene_manager.current_scene.update(self.scene_manager.current_scene.current_time, self.scheduler.schedule(action))
        self.scheduler.clear_sched_events()
        

    def calc_reward(self, terminated):
        episode_score = self.game_scene._score_manager.score
        reward = self.scheduler.calc_reward()
        if terminated:
            reward -= 200
        return episode_score + reward


    def render(self):

        if self.scene_manager.current_scene is not None:
            self.scene_manager.current_scene.render()
        self.clock.tick(FPS)


    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
