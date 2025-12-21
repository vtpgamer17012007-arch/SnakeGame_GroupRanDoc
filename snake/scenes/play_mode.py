import pygame
import sys
from snake import settings as s
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake import save_manager
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class PlayMode:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_scene_name = "PLAY_MODE"
        self.current_scene_obj = None
        self.running = True
        self.nickname = "abs"
        self.input_active = False
        self.showing_load_menu = False
        self.save_list = []
        self.save_rects = []
        self.selected_mode = None
        self.selected_save = None

        self._define_layout()
        self._load_assets()


    def _load_assets(self):

        
        self.img_mode_background = pygame.image.load(ASSETS_PATH / "play_mode_background.png")
        self.img_solo_leveling_button = pygame.image.load(ASSETS_PATH / "solo_leveling_button.png")
        self.img_play_together_button = pygame.image.load(ASSETS_PATH / "play_together_button.png")
        self.img_battle_royale_button = pygame.image.load(ASSETS_PATH / "battle_royale_button.png")
        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()

    def _define_layout(self):
        self.solo_leveling_button_rect = pygame.Rect(157, 319, 277, 70)
        self.play_together_button_rect = pygame.Rect(224, 406, 277, 70)
        self.battle_royale_button_rect = pygame.Rect(157, 492, 277, 70)
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

            if clicked:
                if self.solo_leveling_button_rect.collidepoint(event.pos):
                    self.selected_mode = "SOLO_LEVELING"
                    self.running = False
                elif self.play_together_button_rect.collidepoint(event.pos):
                    self.selected_mode = "PLAY_TOGETHER"
                    self.running = False
                elif self.battle_royale_button_rect.collidepoint(event.pos):
                    self.selected_mode = "BATTLE_ROYALE"
                    self.running = False
                elif self.back_button_rect.collidepoint(event.pos):
                    self.selected_mode = "QUIT"
                    self.running = False

    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):
        self.screen.blit(self.img_mode_background, (0, 0))
        self.Hover(self.img_solo_leveling_button, self.solo_leveling_button_rect)
        self.Hover(self.img_play_together_button, self.play_together_button_rect)
        self.Hover(self.img_battle_royale_button, self.battle_royale_button_rect)

        self.screen.blit(self.img_back_button, self.back_button_rect)
        if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_back_hover_button, self.back_button_rect)
        

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.selected_mode