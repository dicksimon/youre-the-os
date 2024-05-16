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
    return None
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

        self.render_mode = render_mode

        self.event_manager = event_manager

        self.action_space = spaces.MultiDiscrete([57 for _ in range(16)])


        #self.action_space = spaces.Discrete(4)


        self.observation_space = spaces.Discrete(4)



    def reset(self, seed=None, options=None):
        
        self.done = False


        # We need the following line to seed self.np_random
        super().reset(seed=seed)
        observation = self.get_obs()

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
        self.game_scene = Game(self.screen, self.scenes, difficulty_config, compile_auto_script(), standalone=True, ai_mode=True)
        self.scenes['game'] = self.game_scene
        self.game_scene.start()


        self.scene_manager = scene_manager
        self.event_manager.clear_events()
        self.scheduler = ai_schedule.AiSchedule()

        if self.render_mode == "human":


            
            icon = pygame.image.load(path.join('assets', 'icon.png'))
            pygame.display.set_caption(TITLE)
            pygame.display.set_icon(icon)
            
            self.render()
            
        return observation, {}

    def step(self, action): 
        
        observation = self.get_obs()
        asyncio.run(self.game_step(action))

        terminated = self.game_scene.game_over
        if terminated:
            self.done = True
            return observation, self.calc_reward(terminated), terminated, False, {}
    
        if self.render_mode == 'human':
            self.render()

        return observation, self.calc_reward(terminated), terminated, False, {}

    
    def get_obs(self):
        return self.observation_space.sample()


    async def game_step(self, action):
        self.scheduler.handle_events(self.event_manager.get_events())
        self.event_manager.clear_events()
        self.scene_manager.current_scene.update(self.scene_manager.current_scene.current_time, self.scheduler.schedule(action))
        self.scheduler.clear_sched_events()
        await asyncio.sleep(0)

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
