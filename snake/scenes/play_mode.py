import pygame
import sys
from snake import settings as s
from pathlib import Path

# Đường dẫn đến thư mục assets
ASSETS_PATH = Path(__file__).parent.parent / "assets"

class PlayMode:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Biến lưu kết quả mode người chơi chọn
        self.selected_mode = None

        self._load_assets()
        self._define_layout()

    def _load_assets(self):
        try:
            # Load Background
            self.img_mode_background = pygame.image.load(ASSETS_PATH / "play_mode_background.png").convert()
            
            self.img_solo_leveling_button = pygame.image.load(ASSETS_PATH / "solo_leveling_button.png").convert_alpha()
            self.img_play_together_button = pygame.image.load(ASSETS_PATH / "play_together_button.png").convert_alpha()
            self.img_battle_royale_button = pygame.image.load(ASSETS_PATH / "battle_royale_button.png").convert_alpha()
            
            self.img_back_button = pygame.image.load(ASSETS_PATH / "back_button.png").convert_alpha()
            self.img_back_hover_button = pygame.image.load(ASSETS_PATH / "back_hover_button.png").convert_alpha()
            
            self.img_back_button = pygame.transform.smoothscale(self.img_back_button, (80, 60))
            self.img_back_hover_button = pygame.transform.smoothscale(self.img_back_hover_button, (80, 60))

        except FileNotFoundError as e:
            print(f"Lỗi thiếu file ảnh trong PlayMode: {e}")
            sys.exit()

    def _define_layout(self):
        # Định nghĩa vùng bấm (Hitbox)
        self.solo_leveling_button_rect = pygame.Rect(157, 319, 277, 70)
        self.play_together_button_rect = pygame.Rect(224, 406, 277, 70)
        self.battle_royale_button_rect = pygame.Rect(157, 492, 277, 70)
        
        # Hitbox nút Back
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT" # Thoát hẳn game
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # Xử lý chọn Mode
                if self.solo_leveling_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "SOLO_LEVELING"
                    self.running = False
                elif self.play_together_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "PLAY_TOGETHER"
                    self.running = False
                elif self.battle_royale_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "BATTLE_ROYALE"
                    self.running = False
                
#---------------------------------------
                elif self.back_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "BACK" # Trở về menu chính
                    self.running = False
#---------------------------------------

    def Hover(self, img, rect):
        """Hàm vẽ hiệu ứng hover cho các nút Mode"""
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img, (0, 0))

    def _draw_elements(self):
        # 1. Vẽ nền
        self.screen.blit(self.img_mode_background, (0, 0))
        
        # 2. Vẽ hiệu ứng Hover cho các nút chọn Mode
        self.Hover(self.img_solo_leveling_button, self.solo_leveling_button_rect)
        self.Hover(self.img_play_together_button, self.play_together_button_rect)
        self.Hover(self.img_battle_royale_button, self.battle_royale_button_rect)

        # 3. Vẽ nút Back (Với logic Hover chuẩn)
        if self.back_button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.img_back_hover_button, self.back_button_rect)
        else:
            self.screen.blit(self.img_back_button, self.back_button_rect)

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.selected_mode