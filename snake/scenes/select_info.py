import pygame
import sys
from snake import settings as s
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake import save_manager
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"
ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"

class SelectInfo:
    def __init__(self, screen, mode):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_scene_name = "PLAY_MODE"
        self.current_scene_obj = None
        self.running = True
        self.nickname_player1 = ""
        self.nickname_player2 = ""
        self.nickname_player1_active = False
        self.nickname_player2_active = False
        self.input_active = False
        self.showing_load_menu = False
        self.save_list = []
        self.save_rects = []
        self.mode = mode

        self.selected_save = None
        self.difficulty = "DIFFICULTY_NORMAL"

        self.font_input = pygame.font.SysFont('Arial', 30)

        self._define_layout()
        self._load_assets()


    def _load_assets(self):
        #self.img_panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()

        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()
        # =====================================================
        # Load assets cho chế độ 1 người chơi
        # =====================================================
        self.img_1_player_info = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "1_player_info.png").convert_alpha()
        self.img_easy_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "easy_next_button.png").convert_alpha()
        self.img_normal_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "normal_button.png").convert_alpha()
        self.img_normal_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "normal_next_button.png").convert_alpha()
        self.img_hard_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "hard_button.png").convert_alpha()
        self.img_hard_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "hard_next_button.png").convert_alpha()
       

        # =====================================================
        # Load assets cho chế độ 2 người chơi   
        # =====================================================
        self.img_2_player_info = pygame.image.load(ASSETS_PATH / "2_player_info.png").convert_alpha()
        self.img_2_player_info_next = pygame.image.load(ASSETS_PATH / "2_player_info_next.png").convert_alpha()
    def _define_layout(self):
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

        self.next_avatar_player_1_button_rect = pygame.Rect(275, 430, 40, 45)
        self.back_avatar_player_1_button_rect = pygame.Rect(120, 430, 40, 45)
        self.next_avatar_player_2_button_rect = pygame.Rect(275, 620, 40, 45)
        self.back_avatar_player_2_button_rect = pygame.Rect(120, 620, 40, 45)

        self.nickname_player_1_blank_rect = pygame.Rect(95, 320, 640, 70)
        self.nickname_player_2_blank_rect = pygame.Rect(95, 525, 640, 70)

        self.difficulty_easy_button_rect = pygame.Rect(105, 525, 200, 75)
        self.difficulty_normal_button_rect = pygame.Rect(320, 525, 200, 75)
        self.difficulty_hard_button_rect = pygame.Rect(540, 525, 200, 75)

        self.player_info_next_button_rect = pygame.Rect(430, 600, 275, 70)


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
            if event.type == pygame.KEYDOWN:
                    if self.nickname_player1_active:
                        if event.key == pygame.K_BACKSPACE: self.nickname_player1 = self.nickname_player1[:-1]
                        elif len(self.nickname_player1) < 15: self.nickname_player1 += event.unicode
                    if self.nickname_player2_active:
                        if event.key == pygame.K_BACKSPACE: self.nickname_player2 = self.nickname_player2[:-1]
                        elif len(self.nickname_player2) < 15: self.nickname_player2 += event.unicode

            

            if self.mode == "SOLO_LEVELING":
                if clicked:
                    self.nickname_player1_active = self.nickname_player_1_blank_rect.collidepoint(event.pos)
                    if self.difficulty_easy_button_rect.collidepoint(event.pos):
                        self.difficulty = "DIFFICULTY_EASY"
                    elif self.difficulty_normal_button_rect.collidepoint(event.pos):
                        self.difficulty = "DIFFICULTY_NORMAL"
                    elif self.difficulty_hard_button_rect.collidepoint(event.pos):
                        self.difficulty = "DIFFICULTY_HARD"
                    
            elif self.mode == "PLAY_TOGETHER" or self.mode == "BATTLE_ROYALE":
                if clicked:
                    self.nickname_player1_active = self.nickname_player_1_blank_rect.collidepoint(event.pos)
                    self.nickname_player2_active = self.nickname_player_2_blank_rect.collidepoint(event.pos)

            if clicked:
                if self.player_info_next_button_rect.collidepoint(event.pos): #nút let's go 
                    self.running = False
                elif self.back_button_rect.collidepoint(event.pos): #nút back 
                    self.mode = "QUIT"
                    self.running = False
                

    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):
        if self.mode == "SOLO_LEVELING":
            self.screen.blit(self.img_1_player_info, (0, 0))
            
            if self.difficulty == "DIFFICULTY_EASY":
                self.screen.blit(self.img_1_player_info, (0, 0))
                self.Hover(self.img_easy_next_button, self.player_info_next_button_rect)
            elif self.difficulty == "DIFFICULTY_NORMAL":
                self.screen.blit(self.img_normal_button, (0,0))
                self.Hover(self.img_normal_next_button, self.player_info_next_button_rect)
            elif self.difficulty == "DIFFICULTY_HARD":
                self.screen.blit(self.img_hard_button, (0,0))
                self.Hover(self.img_hard_next_button, self.player_info_next_button_rect)

            player1_txt_name = self.font_input.render(self.nickname_player1, True, (255, 255, 255))
            self.screen.blit(player1_txt_name, (460, 328))
            if not self.nickname_player1 and not self.nickname_player1_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (460, 328))
                
        elif self.mode in ["PLAY_TOGETHER", "BATTLE_ROYALE"]:
            self.screen.blit(self.img_2_player_info, (0, 0))
            self.Hover(self.img_2_player_info_next, self.player_info_next_button_rect)

            # =====================================================
            # nhap ten 2 nguoi choi
            # =====================================================
            player1_txt_name = self.font_input.render(self.nickname_player1, True, (255, 255, 255))
            self.screen.blit(player1_txt_name, (460, 328))
            if not self.nickname_player1 and not self.nickname_player1_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (460, 328))

            player2_txt_name = self.font_input.render(self.nickname_player2, True, (255, 255, 255))
            self.screen.blit(player2_txt_name, (460, 525))      
            if not self.nickname_player2 and not self.nickname_player2_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (460, 525))
            # =====================================================
            
        self.screen.blit(self.img_back_button, self.back_button_rect)
        if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_back_hover_button, self.back_button_rect)

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.mode, self.nickname_player1, self.nickname_player2, self.difficulty