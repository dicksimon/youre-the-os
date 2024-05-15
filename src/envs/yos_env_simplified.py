import gymnasium as gym
from gymnasium import spaces
from gymnasium.spaces import  Dict,MultiDiscrete, MultiBinary
import pygame
import numpy as np
import asyncio
from os import path
import sys
import argparse
from enum import Enum

from lib import ai_schedule
from lib import event_manager
from scenes.game import Game
from scene_manager import scene_manager
from game_info import TITLE
from window_size import WINDOW_SIZE


FPS = 60

def compile_auto_script():
    if len(sys.argv) == 1:
        return None
    try:
        source_file = sys.argv[1]
        if not path.isabs(source_file):
            source_file = '../' + source_file
        print('reading source file' , source_file, file=sys.stderr)
        with open(source_file, encoding="utf_8") as in_file:
            source = in_file.read()
        return compile(source, source_file, 'exec')
    except (SyntaxError, ValueError):
        print('Compilation failed, ignoring argument', file=sys.stderr)
        return None


class YosEnvSimplified(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": FPS}

    def __init__(self, render_mode="human"):

        self.render_mode = "human"

        self.action_space = spaces.MultiDiscrete([57 for _ in range(16)])


        #self.action_space = spaces.Discrete(4)


        self.observation_space = spaces.Discrete(4)



    def reset(self, seed=None, options=None):
        
        self.scene_manager = scene_manager
        self.scheduler = ai_schedule.AiSchedule()
        self.events = []
        self.done = False


        # We need the following line to seed self.np_random
        super().reset(seed=seed)
        observation = self.get_obs()
        info = dict()

        difficulty_config = {'name': 'Insane',
                            'num_cpus': 16, 'num_processes_at_startup': 42,
                            'num_ram_rows': 4, 'new_process_probability': 1,
                            'io_probability': 0.3}


        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        icon = pygame.image.load(path.join('assets', 'icon.png'))
        pygame.display.set_caption(TITLE)
        pygame.display.set_icon(icon)
        
        self.scenes = {}
        self.game_scene = Game(self.screen, self.scenes, difficulty_config, compile_auto_script(), standalone=True, ai_mode=True)
        self.scenes['game'] = self.game_scene
        self.game_scene.start()

        if self.render_mode == "human":
            self.render()
            
        return observation, info

    def step(self, action): 
        
        self.scheduler.handle_events(event_manager.get_events())
        event_manager.clear_events()
        self.scene_manager.current_scene.update(self.scene_manager.current_scene.current_time, self.scheduler.schedule(action))
        self.scheduler.clear_sched_events()

        terminated = self.game_scene.game_over
        if terminated:
            self.done = True
        
        reward = self.calc_reward(terminated)

        observation = self.get_obs()
        info = dict()
        
        if self.render_mode == 'human':
            self.render()

        return observation, reward, terminated, False, info

    
    def get_obs(self):
        return self.observation_space.sample()


    def calc_reward(self, terminated):
        reward = self.scheduler.calc_reward()
        if terminated:
            reward -= 200
        return reward


    def render(self):

        if self.scene_manager.current_scene is not None:
            self.scene_manager.current_scene.render()
        self.clock.tick(FPS)


    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
