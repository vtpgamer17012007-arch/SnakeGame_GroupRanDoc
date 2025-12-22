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

        self.sound_manager = SoundManager()
        self.show_setting = False
        self.setting_popup = SettingPopup(self.screen)

        self._define_layout()
        self._load_assets()

    def _load_assets(self):    
        self.img_mode_background = pygame.image.load(ASSETS_PATH / "play_mode_background.png")
        self.img_solo_leveling_button = pygame.image.load(ASSETS_PATH / "solo_leveling_button.png")
        self.img_play_together_button = pygame.image.load(ASSETS_PATH / "play_together_button.png")
        self.img_battle_royale_button = pygame.image.load(ASSETS_PATH / "battle_royale_button.png")
        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()

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

    def _define_layout(self):
        self.solo_leveling_button_rect = pygame.Rect(157, 319, 277, 70)
        self.play_together_button_rect = pygame.Rect(224, 406, 277, 70)
        self.battle_royale_button_rect = pygame.Rect(157, 492, 277, 70)
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

        btn_width = 120 
        btn_height = 80
        margin_x = 8
        margin_y = 10
        
        rect_x = s.SCREEN_WIDTH - btn_width - margin_x
        rect_y = margin_y
        self.setting_button_rect = pygame.Rect(rect_x, rect_y, btn_width, btn_height)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            # Xử lý Popup 
            if self.show_setting:
                if not self.setting_popup.handle_input(event):
                    self.show_setting = False
                continue
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

            if clicked:
                # Mở setting
                if self.setting_button_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.show_setting = True
                    continue

                if self.solo_leveling_button_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.selected_mode = "SOLO_LEVELING"
                    self.running = False
                elif self.play_together_button_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.selected_mode = "PLAY_TOGETHER"
                    self.running = False
                elif self.battle_royale_button_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.selected_mode = "BATTLE_ROYALE"
                    self.running = False
                elif self.back_button_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
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
        
        # Vẽ nút Setting và Popup
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
        return self.selected_mode