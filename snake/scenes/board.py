import pygame
import sys
from snake import settings as s
from pathlib import Path
from snake.core.env_snake import SnakeEnv
#---------------------------------------
import snake.core.save_manager as save_manager 
#---------------------------------------

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class Board:
    def __init__(self, screen, nickname, difficulty=s.BASE_SPEED):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_game_over = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_button = pygame.font.SysFont('Arial', 30)

        self.nickname = nickname
        self.is_game_over = False
        self.is_paused = False
        
#---------------------------------------
        self.is_save_input_active = False 
        self.input_text = ""              
        self.cursor_visible = True        # Trạng thái hiện/ẩn con trỏ
        self.cursor_timer = 0             # Bộ đếm thời gian cho con trỏ
        self.save_prefix = "Save_Solo_"
#---------------------------------------

        self.env = SnakeEnv()
        self.current_speed = difficulty
        self.first_frame = True 
        self.input_queue = []
        self.bg_image = None 
        
        self.snake_sprites = {}
        self._load_snake_sprites()
        self._load_ui_assets()
        
        # --- CẤU HÌNH UI RECT ---
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.menu_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)
        
        self.resume_rect = pygame.Rect(cx - 100, cy - 60, 200, 50)    
        self.save_quit_rect = pygame.Rect(cx - 100, cy + 10, 200, 50) 
        self.quit_rect = pygame.Rect(cx - 100, cy + 80, 200, 50)

    def _load_snake_sprites(self):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / "assets/snake_sprites"
            sz = (s.GRID_SIZE, s.GRID_SIZE)
            
            # Head
            h_down = pygame.image.load(SPRITE_PATH / "head_down.png").convert_alpha()
            self.snake_sprites["head_down"] = pygame.transform.scale(h_down, sz)
            self.snake_sprites["head_up"] = pygame.transform.rotate(pygame.transform.scale(h_down, sz), 180)
            self.snake_sprites["head_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_left.png").convert_alpha(), sz)
            self.snake_sprites["head_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_right.png").convert_alpha(), sz)
            
            # Tail
            self.snake_sprites["tail_up"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_up.png").convert_alpha(), sz)
            self.snake_sprites["tail_down"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_down.png").convert_alpha(), sz)
            self.snake_sprites["tail_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_left.png").convert_alpha(), sz)
            self.snake_sprites["tail_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_right.png").convert_alpha(), sz)
            
            # Body & Turns
            self.snake_sprites["body_vertical"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_vertical.png").convert_alpha(), sz)
            self.snake_sprites["body_horizontal"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_horizontal.png").convert_alpha(), sz)
            
            self.snake_sprites["turn_UL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UL.png").convert_alpha(), sz)
            self.snake_sprites["turn_UR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UR.png").convert_alpha(), sz)
            self.snake_sprites["turn_DL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DL.png").convert_alpha(), sz)
            self.snake_sprites["turn_DR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DR.png").convert_alpha(), sz)
            
            # Items
            self.snake_sprites["food"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "food.png").convert_alpha(), sz)
            self.snake_sprites["poop"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "poop.png").convert_alpha(), sz)
        
        except FileNotFoundError:
            print("Lỗi load ảnh rắn")
            sys.exit()

    def _load_ui_assets(self):
        try:
            self.img_play_again = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_main_menu = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "red_button00.png"), (200, 50))
            self.img_resume = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_quit_blue = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "blue_button00.png"), (200, 50))
#---------------------------------------
            self.img_save = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
#---------------------------------------
        except FileNotFoundError:
            print("Lỗi load ảnh UI")
            sys.exit()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused
#---------------------------------------
                    self.is_save_input_active = False
                    self.input_text = ""
#---------------------------------------
                
                target_dir = None
                if event.key == pygame.K_UP or event.key == pygame.K_w: target_dir = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: target_dir = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a: target_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: target_dir = (1, 0)
                
                if target_dir:
                    if self.input_queue: last_dir = self.input_queue[-1]
                    else: last_dir = self.env.direction
                    
                    is_opposite = (last_dir[0] + target_dir[0] == 0) and (last_dir[1] + target_dir[1] == 0)
                    is_same = (last_dir == target_dir)

                    if not is_opposite and not is_same:
                        if len(self.input_queue) < 2: self.input_queue.append(target_dir)

    def _update_game(self):
        if not self.running: return 
        if self.input_queue:
            next_move = self.input_queue.pop(0)
            self.env.direction = next_move

        state, reward, done, info = self.env.step(self.env.direction)
        if done: self.is_game_over = True

    def _draw_elements(self):
        if self.bg_image: self.screen.blit(self.bg_image, (0, 0))
        else: self.screen.fill(s.COLOR_BACKGROUND)

        snake_pos = self.env.snake_pos
        direction = self.env.direction

        for index, pos in enumerate(snake_pos):
            rect = pygame.Rect(pos[0] * s.GRID_SIZE, pos[1] * s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE)
            sprite = None
            if index == 0:
                if direction == (0, -1): sprite = self.snake_sprites["head_up"]
                elif direction == (0, 1): sprite = self.snake_sprites["head_down"]
                elif direction == (-1, 0): sprite = self.snake_sprites["head_left"]
                elif direction == (1, 0): sprite = self.snake_sprites["head_right"]
            elif index == len(snake_pos) - 1:
                prev_pos = snake_pos[index - 1]
                vec_tail = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])
                if vec_tail == (0, -1): sprite = self.snake_sprites["tail_up"]
                elif vec_tail == (0, 1): sprite = self.snake_sprites["tail_down"]
                elif vec_tail == (-1, 0): sprite = self.snake_sprites["tail_left"]
                elif vec_tail == (1, 0): sprite = self.snake_sprites["tail_right"]
            else:
                prev_pos = snake_pos[index - 1]
                next_pos = snake_pos[index + 1]
                vec_prev = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])   
                vec_next = (next_pos[0] - pos[0], next_pos[1] - pos[1])   
                if vec_prev == vec_next:
                    if vec_prev in ((1, 0), (-1, 0)): sprite = self.snake_sprites["body_horizontal"]
                    else: sprite = self.snake_sprites["body_vertical"]
                else:
                    turn_map = {
                        ((0, 1), (-1, 0)): "turn_DL", ((1, 0), (0, -1)): "turn_DL",
                        ((0, 1), (1, 0)): "turn_DR",  ((-1, 0), (0, -1)): "turn_DR",
                        ((0, -1), (-1, 0)): "turn_UL", ((1, 0), (0, 1)): "turn_UL",
                        ((0, -1), (1, 0)): "turn_UR", ((-1, 0), (0, 1)): "turn_UR",
                    }
                    sprite_key = turn_map.get((vec_prev, vec_next))
                    if sprite_key: sprite = self.snake_sprites[sprite_key]
            if sprite: self.screen.blit(sprite, rect)

        if self.env.food_pos:
            fp = self.env.food_pos
            self.screen.blit(self.snake_sprites["food"], pygame.Rect(fp[0]*s.GRID_SIZE, fp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))
        
        for p in self.env.poops:
            pp = p['pos']
            self.screen.blit(self.snake_sprites["poop"], pygame.Rect(pp[0]*s.GRID_SIZE, pp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))

        score_txt = self.font.render(f"{self.nickname} Score: {self.env.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (5, 5))

    def _draw_game_over_ui(self):
        self._draw_overlay()
        text = self.font_game_over.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(text, text.get_rect(center=(s.SCREEN_WIDTH//2, s.SCREEN_HEIGHT//2 - 50)))
        
        self.screen.blit(self.img_play_again, self.play_again_rect)
        t = self.font_button.render("Play Again", True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=self.play_again_rect.center))

        self.screen.blit(self.img_main_menu, self.menu_rect)
        t = self.font_button.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=self.menu_rect.center))

#---------------------------------------
    def _draw_pause_ui(self):
        self._draw_overlay()
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        
        # Tiêu đề PAUSED
        t = self.font_game_over.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(t, t.get_rect(center=(cx, self.resume_rect.y - 50)))
        
        # 1. Nút Resume
        self.screen.blit(self.img_resume, self.resume_rect)
        t_res = self.font_button.render("Resume", True, (255, 255, 255))
        self.screen.blit(t_res, t_res.get_rect(center=self.resume_rect.center))
        
        # 2. Nút Save & Quit (Mới)
        self.screen.blit(self.img_save, self.save_quit_rect)
        t_save = self.font_button.render("Save & Quit", True, (255, 255, 255))
        self.screen.blit(t_save, t_save.get_rect(center=self.save_quit_rect.center))

        # 3. Nút Main Menu (Quit)
        self.screen.blit(self.img_quit_blue, self.quit_rect)
        t_quit = self.font_button.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(t_quit, t_quit.get_rect(center=self.quit_rect.center))

        # Nếu đang bật hộp thoại nhập tên thì vẽ đè lên
        if self.is_save_input_active:
            self._draw_save_input_box()

    def _draw_save_input_box(self):
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        
        # 1. VẼ NỀN CHE PHỦ
        overlay_rect = pygame.Rect(cx - 250, cy - 70, 500, 250) # Rộng hơn chút để chứa prefix
        pygame.draw.rect(self.screen, (30, 35, 45), overlay_rect) 
        pygame.draw.rect(self.screen, (255, 255, 255), overlay_rect, 2)
        
        # 2. TIÊU ĐỀ
        msg = self.font.render("Enter Filename:", True, (200, 200, 200))
        self.screen.blit(msg, msg.get_rect(center=(cx, cy - 40)))
        
        # 3. VẼ TIỀN TỐ (PREFIX) BÊN NGOÀI
        prefix_surf = self.font.render(self.save_prefix, True, (255, 255, 0)) # Màu vàng cho nổi
        
        # Tính toán vị trí:
        total_w = prefix_surf.get_width() + 10 + 300
        start_x = cx - total_w // 2
        
        # Vẽ Prefix
        self.screen.blit(prefix_surf, (start_x, cy - 10 + (50 - prefix_surf.get_height())//2))
        
        # 4. VẼ Ô NHẬP LIỆU (Nằm ngay sau Prefix)
        input_bg_rect = pygame.Rect(start_x + prefix_surf.get_width() + 10, cy - 10, 300, 50)
        pygame.draw.rect(self.screen, (250, 250, 250), input_bg_rect)
        pygame.draw.rect(self.screen, (0, 100, 255), input_bg_rect, 2)
        
        # 5. TEXT NGƯỜI DÙNG NHẬP
        txt_surf = self.font.render(self.input_text, True, (0, 0, 0))
        text_x = input_bg_rect.x + 10
        text_y = input_bg_rect.y + (input_bg_rect.height - txt_surf.get_height()) // 2
        self.screen.blit(txt_surf, (text_x, text_y))
        
        # 6. CON TRỎ NHẤP NHÁY
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
            
        if self.cursor_visible:
            cursor_x = text_x + txt_surf.get_width() + 2
            cursor_h = txt_surf.get_height()
            pygame.draw.line(self.screen, (0, 0, 0), (cursor_x, text_y), (cursor_x, text_y + cursor_h), 2)
        
        # 7. HƯỚNG DẪN
        hint = self.font_button.render("[ENTER] Save   [ESC] Cancel", True, (150, 150, 150))
        hint = pygame.transform.scale(hint, (int(hint.get_width()*0.7), int(hint.get_height()*0.7)))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 60)))
        
    def _handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            # --- XỬ LÝ HỘP THOẠI SAVE ---
            if self.is_save_input_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_save_input_active = False 
                        pygame.key.set_repeat(0)
                        
                    elif event.key == pygame.K_RETURN:
                        final_filename = self.save_prefix + self.input_text
                        
                        if hasattr(self, 'get_game_state'):
                            data = self.get_game_state()
                            save_manager.save_game(final_filename, data)
                            print(f"Đã lưu: {final_filename}")
                            self.running = False 
                            pygame.key.set_repeat(0)
                        else:
                            self.is_save_input_active = False
                                
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 15 and (event.unicode.isalnum() or event.unicode in "_- "):
                            self.input_text += event.unicode
                return 

            # Xử lý MENU PAUSE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_paused = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.resume_rect.collidepoint(event.pos):
                    self.is_paused = False
                    
                elif self.save_quit_rect.collidepoint(event.pos):
                    # Kích hoạt nhập tên
                    self.is_save_input_active = True
                    # Reset text về rỗng để người dùng nhập mới
                    self.input_text = "" 
                    pygame.key.set_repeat(400, 50)
                    
                elif self.quit_rect.collidepoint(event.pos):
                    self.running = False
#---------------------------------------

    def _draw_overlay(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def _handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_again_rect.collidepoint(event.pos):
                    self.env.reset(); self.is_game_over = False
                if self.menu_rect.collidepoint(event.pos): self.running = False

    def run(self):
        while self.running:
            if self.is_paused: self._handle_pause_input()
            elif self.is_game_over: self._handle_game_over_input()
            else: self._handle_input()

            if not self.is_game_over and not self.is_paused: self._update_game()

            self._draw_elements()
            if self.is_game_over: self._draw_game_over_ui()
            if self.is_paused: self._draw_pause_ui()

            pygame.display.update()
            self.clock.tick(self.current_speed)
            self.first_frame = False
        return "INTRO"