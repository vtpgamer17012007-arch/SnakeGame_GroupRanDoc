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

class Credit:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.current_scene_obj = None
        self.running = True
        self.selected_mode = None

        self.font_input = pygame.font.SysFont('Arial', 30)
        self.return_state = "INTRO"

        self.sound_manager = SoundManager()
        self.show_setting = False
        self.setting_popup = SettingPopup(self.screen)
        
        self._define_layout()
        self._load_assets()

    def _load_assets(self):
        self.img_back_button = pygame.image.load(ASSETS_PATH/ "back_button.png").convert_alpha()
        self.img_back_hover_button = pygame.image.load(ASSETS_PATH/ "back_hover_button.png").convert_alpha()
        self.img_more_button = pygame.image.load(ASSETS_PATH / "more_button.png").convert_alpha()
        self.img_more_hover_button = pygame.image.load(ASSETS_PATH / "more_hover_button.png").convert_alpha()

        self.img_credit = pygame.image.load(ASSETS_PATH / "credit.png").convert_alpha()
        self.img_what_did_we_do = pygame.image.load(ASSETS_PATH / "what_did_we_do.png").convert_alpha()   
        
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
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)
        self.more_button_rect = pygame.Rect(1118, 632, 141, 64)

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

            if self.show_setting:
                is_open = self.setting_popup.handle_input(event)
                if not is_open:
                    self.show_setting = False
                continue

            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

            if clicked and self.setting_button_rect.collidepoint(event.pos):
                self.sound_manager.play_sfx("click")
                self.show_setting = True
                continue 

            # 3. Xử lý các nút riêng theo từng màn hình
            if self.selected_mode == "What did we do":
                # --- Màn hình "More" ---
                if clicked:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click")
                        self.selected_mode = None  # Quay lại màn hình Credit chính
            else:
                # --- Màn hình Credit chính ---
                if clicked:
                    # Nút Back -> Thoát ra Intro
                    if self.back_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click")
                        self.return_state = "QUIT" 
                        self.running = False
                    
                    # Nút More -> Vào màn hình "What did we do"
                    if self.more_button_rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx("click")
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
            
        # vẽ nút Setting
        if self.setting_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_gear_hover, self.setting_button_rect)
        else:
            self.screen.blit(self.img_gear_normal, self.setting_button_rect)

        #Vẽ Popup
        if self.show_setting:
            self.setting_popup.draw()
        
             
    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.return_state