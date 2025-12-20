import pygame
from pathlib import Path
from snake import settings as s
from snake.core.sound_manager import SoundManager

ASSETS_PATH = Path(__file__).parent.parent / "assets"
SETTINGS_ASSETS_PATH = Path(__file__).parent.parent / "assets"

class SettingPopup:
    def __init__(self, screen):
        self.screen = screen
        self.sound_manager = SoundManager()
        # Font chữ số to, đậm
        self.font_val = pygame.font.SysFont('more-sugar.thin.ttf', 40, bold=True)
        
        self._load_assets()
        
        
        # Kích thước nút bấm (Rộng, Cao)
        self.btn_size = (160,160) 
        

        btn_y = 375
        self.sfx_val_center = (420, btn_y+70) 
        self.sfx_dec_pos = (282, btn_y)
        self.sfx_inc_pos = (400, btn_y)

        # --- 2. KHU VỰC MUSIC (Bên Phải) ---
    
        self.music_val_center = (855, btn_y + 70)
      
        self.music_dec_pos = (720, btn_y)
        
        self.music_inc_pos = (835, btn_y)

        # --------------------------------------------------------
        # Tạo vùng bấm (Rect) từ tọa độ trên
        self.sfx_dec_rect = pygame.Rect(self.sfx_dec_pos, self.btn_size)
        self.sfx_inc_rect = pygame.Rect(self.sfx_inc_pos, self.btn_size)
        self.music_dec_rect = pygame.Rect(self.music_dec_pos, self.btn_size)
        self.music_inc_rect = pygame.Rect(self.music_inc_pos, self.btn_size)

        self.board_rect = pygame.Rect(100, 50, 1080, 620)
        self.back_button_rect = pygame.Rect(15, 15, 80, 60)

    def _load_assets(self):
        # 1. Background
        try:
            self.bg_image = pygame.image.load(SETTINGS_ASSETS_PATH / "setting_broad.png").convert_alpha()
            self.bg_image = pygame.transform.scale(self.bg_image, (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        except FileNotFoundError:
            print("Thiếu file setting_broad.png")
            self.bg_image = None
            
        # 2. Hàm load nút
        def load_btn(name):
            try:
                img = pygame.image.load(SETTINGS_ASSETS_PATH / name).convert_alpha()
                return pygame.transform.smoothscale(img, (160,160))
            except FileNotFoundError:
                # Nếu thiếu ảnh, tạo hình vuông màu để test
                surf = pygame.Surface((60, 60))
                surf.fill((0, 0, 255)) 
                return surf

        # Load 4 file ảnh nút
        self.btn_left = load_btn("btn_left.png")
        self.btn_left_hover = load_btn("btn_left_hover.png")
        self.btn_right = load_btn("btn_right.png")
        self.btn_right_hover = load_btn("btn_right_hover.png")

        # Lớp phủ đen mờ
        self.overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        self.overlay.set_alpha(150)
        self.overlay.fill((0, 0, 0))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Back Button
            if self.back_button_rect.collidepoint(mouse_pos):
                self.sound_manager.play_sfx("click")
                return False 
            
            # Click ra ngoài bảng -> Đóng popup
            elif not self.board_rect.collidepoint(mouse_pos):
                self.sound_manager.play_sfx("click")
                return False

            # --- Logic Âm lượng ---
            # SFX
            if self.sfx_dec_rect.collidepoint(mouse_pos):
                self.sound_manager.update_sfx_volume(-10)
                self.sound_manager.play_sfx("click")
            elif self.sfx_inc_rect.collidepoint(mouse_pos):
                self.sound_manager.update_sfx_volume(10)
                self.sound_manager.play_sfx("click")
                
            # MUSIC
            elif self.music_dec_rect.collidepoint(mouse_pos):
                self.sound_manager.update_music_volume(-10)
                self.sound_manager.play_sfx("click")
            elif self.music_inc_rect.collidepoint(mouse_pos):
                self.sound_manager.update_music_volume(10)
                self.sound_manager.play_sfx("click")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: return False

        return True 

    def _draw_button(self, rect, img_normal, img_hover):
        """Vẽ nút, nếu chuột đang trỏ vào thì vẽ ảnh hover"""
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img_hover, rect)
        else:
            self.screen.blit(img_normal, rect)

    def draw(self):
        # 1. Vẽ nền tối
        self.screen.blit(self.overlay, (0, 0))
        
        # 2. Vẽ bảng Setting
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))

        # 3. Vẽ các nút (Tự động đổi màu khi hover)
        self._draw_button(self.sfx_dec_rect, self.btn_left, self.btn_left_hover)
        self._draw_button(self.sfx_inc_rect, self.btn_right, self.btn_right_hover)
        
        self._draw_button(self.music_dec_rect, self.btn_left, self.btn_left_hover)
        self._draw_button(self.music_inc_rect, self.btn_right, self.btn_right_hover)

        # 4. Vẽ số Volume
        text_color = (0, 0, 0) # Màu đen
        
        # SFX Value
        sfx_txt = self.font_val.render(str(int(self.sound_manager.vol_sfx)), True, text_color)
        sfx_rect = sfx_txt.get_rect(center=self.sfx_val_center)
        self.screen.blit(sfx_txt, sfx_rect)

        # Music Value
        music_txt = self.font_val.render(str(int(self.sound_manager.vol_music)), True, text_color)
        music_rect = music_txt.get_rect(center=self.music_val_center)
        self.screen.blit(music_txt, music_rect)



    def _draw_debug(self):
        pygame.draw.rect(self.screen, (255, 0, 0), self.sfx_dec_rect, 2)
        pygame.draw.rect(self.screen, (255, 0, 0), self.sfx_inc_rect, 2)
        pygame.draw.rect(self.screen, (255, 0, 0), self.music_dec_rect, 2)
        pygame.draw.rect(self.screen, (255, 0, 0), self.music_inc_rect, 2)
        pygame.draw.circle(self.screen, (0, 255, 0), self.sfx_val_center, 5)
        pygame.draw.circle(self.screen, (0, 255, 0), self.music_val_center, 5)