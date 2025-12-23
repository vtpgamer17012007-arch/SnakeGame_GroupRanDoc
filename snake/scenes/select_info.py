import pygame
import sys
from snake import settings as s
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake import save_manager
from pathlib import Path
from snake.core.sound_manager import SoundManager
from snake.scenes.setting import SettingPopup

ASSETS_PATH = Path(__file__).parent.parent / "assets"
ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"
FONT_PATH = Path(__file__).parent.parent / "assets/fonts"

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
        self.font_file = None

        self.avatar_idx1 = 0
        self.avatar_idx2 = 0
        self.img_avatars = []

        self.selected_save = None
        self.difficulty = s.DIFFICULTY_NORMAL

        self.font_input = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 37)

        self.sound_manager = SoundManager() 
        self.sound_manager.play_music("menu")
        
        self.show_setting = False
        self.setting_popup = SettingPopup(self.screen)

        self._define_layout()
        self._load_assets()

    def _load_assets(self):
        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()
        # Load assets cho chế độ 1 người chơi
        self.img_1_player_info = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "1_player_info.png").convert_alpha()
        self.img_easy_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "easy_next_button.png").convert_alpha()
        self.img_normal_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "normal_button.png").convert_alpha()
        self.img_normal_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "normal_next_button.png").convert_alpha()
        self.img_hard_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "hard_button.png").convert_alpha()
        self.img_hard_next_button = pygame.image.load(ONE_PLAYER_ASSETS_PATH / "hard_next_button.png").convert_alpha()
        # Load assets cho chế độ 2 người chơi   
        self.img_2_player_info = pygame.image.load(ASSETS_PATH / "2_player_info.png").convert_alpha()
        self.img_2_player_info_next = pygame.image.load(ASSETS_PATH / "2_player_info_next.png").convert_alpha()
        # Load nút setting
        btn_w, btn_h = 120, 80 
        try:
            raw_gear = pygame.image.load(ASSETS_PATH / "setting_button.png").convert_alpha()
            self.img_gear_normal = pygame.transform.smoothscale(raw_gear, (btn_w, btn_h))
            try:
                raw_hover = pygame.image.load(ASSETS_PATH / "setting_button_hover.png").convert_alpha()
                self.img_gear_hover = pygame.transform.smoothscale(raw_hover, (btn_w, btn_h))
            except FileNotFoundError:
                self.img_gear_hover = self.img_gear_normal.copy()
                self.img_gear_hover.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_ADD)
        except FileNotFoundError:
                self.img_gear_normal = pygame.Surface((btn_w, btn_h)); self.img_gear_normal.fill((100,100,100))
                self.img_gear_hover = pygame.Surface((btn_w, btn_h)); self.img_gear_hover.fill((150,150,150))
        # load avatar
        for name in s.AVATAR_LIST:
            self.avatar_image = pygame.image.load(ASSETS_PATH / f"{name}.png").convert_alpha()
            self.img_avatars.append(self.avatar_image)

        #load font
        self.font_file = ASSETS_PATH / "fonts/Ruso-Regular.ttf"
            
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

        btn_width, btn_height = 120, 80
        rect_x = s.SCREEN_WIDTH - btn_width - 8
        rect_y = 10
        self.setting_button_rect = pygame.Rect(rect_x, rect_y, btn_width, btn_height)


    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            if self.show_setting:
                if not self.setting_popup.handle_input(event):
                    self.show_setting = False
                continue 
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
            if clicked and self.setting_button_rect.collidepoint(event.pos):
                self.sound_manager.play_sfx("click")
                self.show_setting = True
                continue
            
            if event.type == pygame.KEYDOWN:
                    if event.key != pygame.K_RETURN: 
                        self.sound_manager.play_sfx("input")
                    if self.nickname_player1_active:
                        if event.key == pygame.K_BACKSPACE: self.nickname_player1 = self.nickname_player1[:-1]
                        elif len(self.nickname_player1) < 15: self.nickname_player1 += event.unicode
                    if self.nickname_player2_active:
                        if event.key == pygame.K_BACKSPACE: self.nickname_player2 = self.nickname_player2[:-1]
                        elif len(self.nickname_player2) < 15: self.nickname_player2 += event.unicode  

            if self.mode == "SOLO_LEVELING":
                if clicked:
                    # name
                    self.nickname_player1_active = self.nickname_player_1_blank_rect.collidepoint(event.pos)
                    # difficulty
                    if self.difficulty_easy_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.difficulty = s.DIFFICULTY_EASY
                    elif self.difficulty_normal_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.difficulty = s.DIFFICULTY_NORMAL
                    elif self.difficulty_hard_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.difficulty = s.DIFFICULTY_HARD
                    # avatar
                    if self.next_avatar_player_1_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx1 = (self.avatar_idx1 + 1) % len(s.AVATAR_LIST)
                    elif self.back_avatar_player_1_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx1 = (self.avatar_idx1 - 1) % len(s.AVATAR_LIST)
                    
            elif self.mode == "PLAY_TOGETHER" or self.mode == "BATTLE_ROYALE":
                if clicked:
                    # name
                    self.nickname_player1_active = self.nickname_player_1_blank_rect.collidepoint(event.pos)
                    self.nickname_player2_active = self.nickname_player_2_blank_rect.collidepoint(event.pos)
                    # avatar
                    if self.next_avatar_player_1_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx1 = (self.avatar_idx1 + 1) % len(s.AVATAR_LIST)
                    elif self.back_avatar_player_1_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx1 = (self.avatar_idx1 - 1) % len(s.AVATAR_LIST)
                    elif self.next_avatar_player_2_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx2 = (self.avatar_idx2 + 1) % len(s.AVATAR_LIST)
                    elif self.back_avatar_player_2_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click") 
                        self.avatar_idx2 = (self.avatar_idx2 - 1) % len(s.AVATAR_LIST)

            if clicked:
                if self.player_info_next_button_rect.collidepoint(event.pos): #nút let's go
                    self.sound_manager.play_sfx("click")  
                    self.running = False
                elif self.back_button_rect.collidepoint(event.pos): #nút back 
                    self.sound_manager.play_sfx("click") 
                    self.mode = "QUIT"
                    self.running = False
                

    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):
        if self.mode == "SOLO_LEVELING":
            # background
            self.screen.blit(self.img_1_player_info, (0, 0))
            # difficulty
            if self.difficulty == s.DIFFICULTY_EASY:
                self.screen.blit(self.img_1_player_info, (0, 0))
                self.Hover(self.img_easy_next_button, self.player_info_next_button_rect)
            elif self.difficulty == s.DIFFICULTY_NORMAL:
                self.screen.blit(self.img_normal_button, (0,0))
                self.Hover(self.img_normal_next_button, self.player_info_next_button_rect)
            elif self.difficulty == s.DIFFICULTY_HARD:
                self.screen.blit(self.img_hard_button, (0,0))
                self.Hover(self.img_hard_next_button, self.player_info_next_button_rect)
            # name 
            player1_txt_name = self.font_input.render(self.nickname_player1, True, (255, 255, 255))
            self.screen.blit(player1_txt_name, (430, 332))
            if not self.nickname_player1 and not self.nickname_player1_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (430, 332))
            # avatar
            self.screen.blit(self.img_avatars[self.avatar_idx1], (175, 415))
                
        elif self.mode in ["PLAY_TOGETHER", "BATTLE_ROYALE"]:
            # background
            self.screen.blit(self.img_2_player_info, (0, 0))
            self.Hover(self.img_2_player_info_next, self.player_info_next_button_rect)

            # name 
            player1_txt_name = self.font_input.render(self.nickname_player1, True, (255, 255, 255))
            self.screen.blit(player1_txt_name, (450, 329))
            if not self.nickname_player1 and not self.nickname_player1_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (450, 329))

            player2_txt_name = self.font_input.render(self.nickname_player2, True, (255, 255, 255))
            self.screen.blit(player2_txt_name, (450, 526))      
            if not self.nickname_player2 and not self.nickname_player2_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (450, 526))
            # avatar
            self.screen.blit(self.img_avatars[self.avatar_idx1], (174, 410))
            self.screen.blit(self.img_avatars[self.avatar_idx2], (174, 602))

        self.screen.blit(self.img_back_button, self.back_button_rect)
        if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_back_hover_button, self.back_button_rect)

            # vẽ nút setting
        if self.setting_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_gear_hover, self.setting_button_rect)
        else:
            self.screen.blit(self.img_gear_normal, self.setting_button_rect)

        if self.show_setting:
            self.setting_popup.draw()

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.mode, self.nickname_player1, self.nickname_player2, s.AVATAR_LIST[self.avatar_idx1], s.AVATAR_LIST[self.avatar_idx2], self.difficulty