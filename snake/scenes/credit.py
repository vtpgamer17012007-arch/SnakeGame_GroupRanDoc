import pygame
import sys
from snake import settings as s
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake import save_manager
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class Credit:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_scene_obj = None
        self.running = True
        self.selected_mode = None

        self.font_input = pygame.font.SysFont('Arial', 30)
        self.return_state = "INTRO"
        self._define_layout()
        self._load_assets()

    def _load_assets(self):
        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()
        self.img_more_button = pygame.image.load(ASSETS_PATH / "more_button.png").convert_alpha()
        self.img_more_hover_button = pygame.image.load(ASSETS_PATH / "more_hover_button.png").convert_alpha()

        self.img_credit = pygame.image.load(ASSETS_PATH / "credit.png").convert_alpha()
        self.img_what_did_we_do = pygame.image.load(ASSETS_PATH / "what_did_we_do.png").convert_alpha()   
        
    def _define_layout(self):
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)
        self.more_button_rect = pygame.Rect(1118, 632, 141, 64)


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

            if self.selected_mode == "What did we do":
                if clicked:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.selected_mode = None  
            else:
                if clicked:
                    # Xử lý nút Back (Quay lại)
                    if self.back_button_rect.collidepoint(event.pos):
                        self.return_state = "QUIT" # Quan trọng: Phải set là QUIT
                        self.running = False
                    # Xử lý nút Next 
                    if self.more_button_rect.collidepoint(event.pos):
                        self.selected_mode = "What did we do" 

    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):

        if self.selected_mode == "What did we do":
            self.screen.blit(self.img_what_did_we_do, (0, 0))
        else:
            self.screen.blit(self.img_credit, (0, 0))
            # Vẽ nút More
            self.screen.blit(self.img_more_button, self.more_button_rect)
            if self.more_button_rect.collidepoint(pygame.mouse.get_pos()):
                self.screen.blit(self.img_more_hover_button, self.more_button_rect)
        
         # Vẽ nút Back
        self.screen.blit(self.img_back_button, self.back_button_rect)
        if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_back_hover_button, self.back_button_rect)
             
    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.return_state