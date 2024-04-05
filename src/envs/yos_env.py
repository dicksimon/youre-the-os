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


class YosEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": FPS}

    def __init__(self, render_mode=None, size=5):

        self.render_mode = None

        self.action_space = spaces.MultiDiscrete([57 for _ in _ range(16)])

        self.observation_space = Dict({

            "events":MultiDiscrete([57,57,57]),

            "exists": MultiBinary(57,),
            "unstarve_time": MultiDiscrete([5 for _ in range(57)]),
            "starvation_level": MultiDiscrete([6 for _ in range(57)]),
            "in_use": MultiBinary(57,),
            "waiting_for_page": MultiBinary(57,),
            "has_ended": MultiBinary(57,),
            "pages": Dict({
                "exists": MultiBinary([57, 57, 57]),
                "in_use": MultiBinary([57, 57, 57]),
                "in_swap": MultiBinary([57, 57, 57]) 
            })
        
        })



    def reset(self, seed=None, options=None):
        

        self.events = []
        self.done = False
        # We need the following line to seed self.np_random

        super().reset(seed=seed)
        observation = self.get_obs()
        info = dict()

        if self.render_mode == "human":
            
            source_filename, difficulty_config = parse_arguments()
            compiled_script = compile_auto_script(source_filename)
            
            pygame.init()
            pygame.font.init()
            
            screen = pygame.display.set_mode(WINDOW_SIZE)
            self.clock = pygame.time.Clock()
            
            icon = pygame.image.load(path.join('assets', 'icon.png'))
            pygame.display.set_caption(TITLE)
            pygame.display.set_icon(icon)
            
            scenes = {}
            game_scene = Game(screen, scenes, difficulty_config, compile_auto_script(), True)
            scenes['game'] = game_scene
            game_scene.start()

            self.render()
            

        return observation, info

    def step(self, action): 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        self.scene_manager.current_scene.update(self.scene_manager.current_scene.current_time, [])



        ##generate actions 




        ##handle actions
        ##Part of the Skript

        #events = list()
        #self._event_queue.clear()
        ## update the status of process/memory
        #for event in events:
        #    handler = getattr(self, f"_update_{event.etype}", None)
        #    if handler is not None:
        #        handler(event)
        ## run the scheduler
        #self.schedule()
  

        terminated = False
        reward = 0
        observation = self._get_obs()
        info = dict()
        
        if self.render_mode == 'human':
            self.render()

        return observation, reward, terminated, False, info

    
    def get_obs(self):
        return self.observation_space.sample()


    def render(self):

        self.scene_manager.current_scene.render()
        self.clock.tick(FPS)

    

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
