import pygame
import sys
from snake import settings as s
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
import snake.core.save_manager as save_manager
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"
ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"
TWO_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/2_player_asset"

class Rules:
    def __init__(self, screen, mode):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_scene_name = "PLAY_MODE"
        self.current_scene_obj = None
        self.running = True

        self.mode = mode
        self.selected_mode = None

        self.font_input = pygame.font.SysFont('Arial', 30)
#---------------------------------------
        self.return_state = "QUIT"
#---------------------------------------
        self._define_layout()
        self._load_assets()


    def _load_assets(self):
        #self.img_panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()

        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()
       
        self.img_rule_solo_leveling = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "rule_solo_leveling.png").convert_alpha()
        self.img_rule_solo_leveling_next = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "rule_solo_leveling_next.png").convert_alpha()
        self.img_rule_play_together = pygame.image.load(ASSETS_PATH / "rule_play_together.png").convert_alpha()
        self.img_rule_play_together_next = pygame.image.load(ASSETS_PATH / "rule_play_together_next.png").convert_alpha()
        self.img_rule_battle_royale = pygame.image.load(TWO_PLAYER_ASSETS_PATH / "rule_battle_royale.png").convert_alpha()
        self.img_rule_battle_royale_next = pygame.image.load(TWO_PLAYER_ASSETS_PATH / "rule_battle_royale_next.png").convert_alpha()

    def _define_layout(self):
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

        self.next_button_rect = pygame.Rect(430, 600, 275, 70)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
            
            if clicked:
                # Xử lý nút Back (Quay lại)
                if self.back_button_rect.collidepoint(event.pos):
#---------------------------------------
                    self.return_state = "QUIT" # Quan trọng: Phải set là QUIT
                    self.running = False
#---------------------------------------

                # Xử lý nút Next (Vào game)
                # Lưu ý: Cả 3 chế độ đều dùng chung self.next_button_rect được định nghĩa ở _define_layout
                is_next_clicked = False
                
                if self.mode == "SOLO_LEVELING" and self.next_button_rect.collidepoint(event.pos):
                    is_next_clicked = True
                elif self.mode == "PLAY_TOGETHER" and self.next_button_rect.collidepoint(event.pos):
                    is_next_clicked = True
                elif self.mode == "BATTLE_ROYALE" and self.next_button_rect.collidepoint(event.pos):
                    # Đã sửa tên biến từ player_info_next_button_rect thành next_button_rect
                    is_next_clicked = True
                
                if is_next_clicked:
#---------------------------------------
                    self.return_state = "PLAY" # Quan trọng: Phải set là PLAY để app.py biết mà vào game
                    self.running = False
#---------------------------------------
                
    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):
        if self.mode == "SOLO_LEVELING":
            self.screen.blit(self.img_rule_solo_leveling, (0, 0))
            self.Hover(self.img_rule_solo_leveling_next, self.next_button_rect)
        elif self.mode == "PLAY_TOGETHER":
            self.screen.blit(self.img_rule_play_together, (0, 0))
            self.Hover(self.img_rule_play_together_next, self.next_button_rect)
        elif self.mode == "BATTLE_ROYALE":    
            self.screen.blit(self.img_rule_battle_royale, (0, 0))
            self.Hover(self.img_rule_battle_royale_next, self.next_button_rect)
            
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