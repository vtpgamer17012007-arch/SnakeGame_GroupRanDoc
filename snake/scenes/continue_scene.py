import pygame
import sys
from pathlib import Path
from snake import settings as s
from snake import save_manager
from snake.core.sound_manager import SoundManager
from snake.scenes.setting import SettingPopup

class ContinueScene:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.sound_manager = SoundManager()
        self.sound_manager.play_music("menu") 
        self.show_setting = False
        self.setting_popup = SettingPopup(self.screen)
        
        # Load nút setting
        self._load_setting_assets()
        # --- CẤU HÌNH DEBUG ---
        self.debug_mode = False
        
        self.font = pygame.font.SysFont('Arial', 22, bold=True)
        self.font_score = pygame.font.SysFont('Arial', 20)
        self.font_debug = pygame.font.SysFont('Arial', 12) 
   

        # --- 1. THIẾT LẬP ĐƯỜNG DẪN ---
        self.base_path = Path(__file__).resolve().parent.parent
        self.assets_dir = self.base_path / "assets"
        
        self.load_path = None
        if self.assets_dir.exists():
            for folder in self.assets_dir.iterdir():
                if folder.is_dir() and folder.name.lower() in ["load_asset", "load"]:
                    self.load_path = folder
                    break
        
        if not self.load_path: self.load_path = self.assets_dir

        # --- 2. THIẾT LẬP HITBOX ---
        self.selected_mode = "SOLO_LEVELING" 
        self._setup_layout()

        # --- 3. LOAD HÌNH ẢNH ---
        self._load_resources()

        # --- 4. LOAD DỮ LIỆU SAVE ---
        self.filtered_saves = [] 
        self._refresh_save_data()

    def _load_setting_assets(self):
        btn_w, btn_h = 120, 80
        self.setting_button_rect = pygame.Rect(s.SCREEN_WIDTH - 120 - 8, 10, btn_w, btn_h)
        try:
            raw_gear = pygame.image.load(ASSETS_PATH / "setting_button.png").convert_alpha()
            self.img_gear_normal = pygame.transform.smoothscale(raw_gear, (btn_w, btn_h))
            try:
                raw_hover = pygame.image.load(ASSETS_PATH / "setting_button_hover.png").convert_alpha()
                self.img_gear_hover = pygame.transform.smoothscale(raw_hover, (btn_w, btn_h))
            except FileNotFoundError:
                self.img_gear_hover = self.img_gear_normal
        except:
            self.img_gear_normal = pygame.Surface((btn_w, btn_h))
            self.img_gear_hover = self.img_gear_normal
    def _setup_layout(self):
        # 1. Nút Back
        self.back_rect = pygame.Rect(15, 15, 80, 60)

        # 2. Ba nút chuyển chế độ (Tabs)
        self.tabs = [
            {"mode": "SOLO_LEVELING", "rect": pygame.Rect(512, 108, 220, 70)}, 
            {"mode": "PLAY_TOGETHER", "rect": pygame.Rect(750, 108, 220, 70)},
            {"mode": "BATTLE_ROYALE", "rect": pygame.Rect(987, 108, 220, 70)}
        ]

        # 3. Năm ô Save (Slots)
        self.slots = []
        start_x = 537
        start_y = 235
        slot_width = 644
        slot_height = 71
        gap = 89
        
        for i in range(5):
            self.slots.append(pygame.Rect(start_x, start_y + i * gap, slot_width, slot_height))

    def _load_resources(self):
        try:
            self.bg_solo = self._load_img_bg("solo.png")
            self.bg_play2p = self._load_img_bg("play2P.png")
            self.bg_battle = self._load_img_bg("battle.png")
            
            path_highlight = self.load_path / "save_highlight.png"
            if path_highlight.exists():
                self.img_save_highlight = pygame.image.load(str(path_highlight)).convert_alpha()
            else:
                self.img_save_highlight = pygame.Surface((1,1))
            
            path_normal = self.assets_dir / "back_button.png"
            path_hover = self.assets_dir / "back_hover_button.png"

            if path_normal.exists() and path_hover.exists():
                raw_normal = pygame.image.load(str(path_normal)).convert_alpha()
                raw_hover = pygame.image.load(str(path_hover)).convert_alpha()
                w, h = self.back_rect.width, self.back_rect.height
                self.btn_back_normal = pygame.transform.smoothscale(raw_normal, (w, h))
                self.btn_back_hover = pygame.transform.smoothscale(raw_hover, (w, h))
            else:
                self.btn_back_normal = pygame.Surface((80, 50)); self.btn_back_normal.fill((0,0,255))
                self.btn_back_hover = pygame.Surface((80, 50)); self.btn_back_hover.fill((255,100,0))

            path_slot_frame = self.load_path / "save_highlight.png" 
            if path_slot_frame.exists():
                raw_frame = pygame.image.load(str(path_slot_frame)).convert_alpha()
                new_w = 680
                new_h = 100
                self.img_slot_frame = pygame.transform.smoothscale(raw_frame, (new_w, new_h))
            else:
                self.img_slot_frame = None

        except Exception as e:
            print(f"Lỗi load resources: {e}")
            sys.exit()

    def _load_img_bg(self, name):
        path = self.load_path / name
        if not path.exists(): 
            return pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        img = pygame.image.load(str(path)).convert()
        return pygame.transform.scale(img, (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))

    def _refresh_save_data(self):
        all_keys = save_manager.get_save_list()
        temp = []
        for key in all_keys:
            data = save_manager.load_game(key)
            if data and data.get("mode") == self.selected_mode:
                temp.append({"key": key, "data": data})
        self.filtered_saves = temp[::-1][:5]

    def _draw_debug_rects(self):
        if not self.debug_mode: return
        pygame.draw.rect(self.screen, (255, 0, 0), self.back_rect, 2)
        for tab in self.tabs:
            col = (0, 255, 0) if tab["mode"] == self.selected_mode else (255, 0, 0)
            pygame.draw.rect(self.screen, col, tab["rect"], 2)
        for rect in self.slots:
            pygame.draw.rect(self.screen, (0, 255, 255), rect, 2)
        mx, my = pygame.mouse.get_pos()
        coord_surf = self.font_debug.render(f"({mx}, {my})", True, (255, 255, 0), (0,0,0))
        self.screen.blit(coord_surf, (mx + 15, my + 15))

    def _draw(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.selected_mode == "SOLO_LEVELING": self.screen.blit(self.bg_solo, (0, 0))
        elif self.selected_mode == "PLAY_TOGETHER": self.screen.blit(self.bg_play2p, (0, 0))
        else: self.screen.blit(self.bg_battle, (0, 0))

        if self.back_rect.collidepoint(mouse_pos):
            self.screen.blit(self.btn_back_hover, self.back_rect)
        else:
            self.screen.blit(self.btn_back_normal, self.back_rect)

        for i, rect in enumerate(self.slots):
            slot_data = self.filtered_saves[i] if i < len(self.filtered_saves) else None
            
            if slot_data and self.img_slot_frame:
                # >>>> CHỈNH THÔNG SỐ TẠI ĐÂY <<<<
                static_off_x = 5  
                static_off_y = 0  
                
                # Lấy khung hình chữ nhật căn giữa
                static_rect = self.img_slot_frame.get_rect(center=rect.center)
                
                # Áp dụng độ lệch thủ công
                static_rect.x += static_off_x
                static_rect.y += static_off_y
                
                self.screen.blit(self.img_slot_frame, static_rect)
                
            if slot_data and rect.collidepoint(mouse_pos):
                # 1. CẤU HÌNH DỊCH CHUYỂN (Sửa số ở đây)
                manual_offset_x = 5  
                manual_offset_y = 0  

                # 2. Xử lý ảnh
                h_img = pygame.transform.scale(self.img_save_highlight, (680, 100))
                scaled = pygame.transform.scale(h_img, (int(680 * 1.03), int(100 * 1.05)))
                
                # 3. Lấy vị trí tâm chuẩn
                img_rect = scaled.get_rect(center=rect.center)
                
                # 4. Cộng thêm độ lệch thủ công
                img_rect.x += manual_offset_x
                img_rect.y += manual_offset_y
                
                self.screen.blit(scaled, img_rect)
            
            if slot_data:
                name_txt = self.font.render(f"{slot_data['key']}", True, (0, 0, 0))
                self.screen.blit(name_txt, (rect.x + 40, rect.y + 12))
                score_txt = self.font_score.render(f"Score: {slot_data['data'].get('score', 0)}", True, (0, 0, 0))
                self.screen.blit(score_txt, (rect.x + 40, rect.y + 36))
                mouse_pos = pygame.mouse.get_pos()
        if self.setting_button_rect.collidepoint(mouse_pos):
            self.screen.blit(self.img_gear_hover, self.setting_button_rect)
        else:
            self.screen.blit(self.img_gear_normal, self.setting_button_rect)

        if self.show_setting:
            self.setting_popup.draw()

        self._draw_debug_rects()

    def run(self):
        while self.running:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if self.show_setting:
                    if not self.setting_popup.handle_input(event):
                        self.show_setting = False
                    continue
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_rect.collidepoint(pos): 
                        self.sound_manager.play_sfx("click")
                        return "BACK", None
                    
                    for tab in self.tabs:
                        if tab["rect"].collidepoint(pos):
                            self.sound_manager.play_sfx("click")
                            if self.selected_mode != tab["mode"]: 
                                self.selected_mode = tab["mode"]
                                self._refresh_save_data()
                    
                    for i, rect in enumerate(self.slots):
                        if rect.collidepoint(pos) and i < len(self.filtered_saves):
                            return "LOAD_GAME", self.filtered_saves[i]["data"]

            self._draw()
            pygame.display.flip()
            self.clock.tick(60)