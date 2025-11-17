import pygame
import sys
from snake import settings as s
from snake.scenes.board import Board
from snake.scenes.intro import Intro
from snake import save_manager

class SnakeApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pygame.display.set_caption("Game Rắn Săn Mồi")
        self.current_scene_name = "INTRO"
        self.current_scene_obj = None
        self.nickname = ""

    def run(self):
        while True:
            if self.current_scene_name == "INTRO":
                self.current_scene_obj = Intro(self.screen)
                mode, nickname, save_name = self.current_scene_obj.run()
                if nickname: self.nickname = nickname

                if mode == "PLAYER":
                    self.current_scene_obj = Board(self.screen, self.nickname)
                    self.current_scene_name = "BOARD"
                elif mode == "LOAD":
                    state = save_manager.load_game(save_name)
                    if state:
                        self.current_scene_obj = Board(self.screen, state["nickname"], state, save_name)
                        self.current_scene_name = "BOARD"
                    else:
                        self.current_scene_name = "INTRO"
                elif mode == "AI":
                    self.current_scene_name = "INTRO"
                elif mode == "QUIT":
                    break

            elif self.current_scene_name == "BOARD":
                next_scene = self.current_scene_obj.run()
                if next_scene == "INTRO": self.current_scene_name = "INTRO"
                else: break

        pygame.quit()
        sys.exit()