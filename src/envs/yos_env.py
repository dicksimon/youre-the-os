import gymnasium as gym
from gymnasium import spaces, Env
from gymnasium.spaces import Box, Dict, Discrete, MultiDiscrete, MultiBinary
import pygame
import numpy as np
import asyncio
from os import path
import sys
import argparse
from enum import Enum

import sys
import os
yos_lib_dir = '~/youre-the-os/src/lib'
yos_src_dir = '~/youre-the-os/src'
sys.path.append(os.path.dirname(os.path.expanduser(yos_lib_dir)))
sys.path.append(os.path.dirname(os.path.expanduser(yos_src_dir)))
from scenes.game import Game
from scene_manager import scene_manager
from game_info import TITLE
from window_size import WINDOW_SIZE



class YosEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None, size=5):

        self.action_space = spaces.MultiDiscrete([57,57,57,57,57,57,57,57,57,57,57,57,57,57,57,57])

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


        #self.size = size  # The size of the square grid
        #self.window_size = 512  # The size of the PyGame window
        #assert render_mode is None or render_mode in self.metadata["render_modes"]
        #self.render_mode = render_mode

        self.window = None
        self.clock = None



    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)
        observation = self.get_obs()
        info = self.get_info()

        #self._render_frame()

        return observation, info

    def step(self, action): #step == schedule??
        

        # entrypoint
        ###def __call__(self, events: list):
        """Entrypoint from game

        will dispatch each event to the respective handler,
        collecting action events to send back to the game,
        if a handler doesn't exist, will ignore that event.
        """
        events = list()
        self._event_queue.clear()
        # update the status of process/memory
        for event in events:
            handler = getattr(self, f"_update_{event.etype}", None)
            if handler is not None:
                handler(event)
        # run the scheduler
        self.schedule()
        ###return self._event_queue


        #Aktion die ausgeführt werden soll
        
        #ai_schedule.clean_io_queue()
        #ai_schedule.update_ram_schedule()
        #air_scheudle.update_ram_schedule()

        terminated = False

        #reward function
        reward = 0
 
        
        ##reward = 1 if terminated else 0  # Binary sparse rewards
        ##belohnungsfunktion

        observation = self._get_obs()
        info = dict()
        
        #self._render_frame()

        return observation, reward, terminated, False, info

    
    def get_obs(self):
        return self.observation_space.sample()

    def get_info(self):
        return {"info":7}
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):

        if self.window is None:

            pygame.init()
            pygame.font.init()
            screen = pygame.display.set_mode(WINDOW_SIZE)
            icon = pygame.image.load(path.join('assets', 'icon.png'))
            pygame.display.set_caption(TITLE)
            pygame.display.set_icon(icon)
            self.window = pygame.display.set_mode((self.window_size, self.window_size))

            source_filename, difficulty_config = parse_arguments()
            compiled_script = compile_auto_script(source_filename)

            scenes = {}
            game_scene = Game(screen, scenes, difficulty_config, compiled_script, True)
            scenes['game'] = game_scene
            game_scene.start()

        if self.clock is None:
            self.clock = pygame.time.Clock()


        #for event in pygame.event.get():
            #probably unneeded
            #if event.type == pygame.QUIT:
            #    sys.exit()
         #   scene_manager.current_scene.update(scene_manager.current_scene.current_time, [])
         #   scene_manager.current_scene.render()
    

        # We need to ensure that human-rendering occurs at the predefined framerate.
        # The following line will automatically add a delay to keep the framerate stable.
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
