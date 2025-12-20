import pygame
import sys
from snake import settings as s
from pathlib import Path
from snake.core.env_2p import SnakeEnv2P
from snake.scenes.board import Board 
#---------------------------------------
import snake.core.save_manager as save_manager
#---------------------------------------

ASSETS_PATH = Path(__file__).parent.parent / "assets"

#---------------------------------------
class PlayTogether(Board):
    def __init__(self, screen, name1="Player 1", name2="Player 2"):
        # Khởi tạo cơ bản
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.name1 = name1 
        self.name2 = name2 
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_game_over = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_button = pygame.font.SysFont('Arial', 30)
        
        self.mode_id = "PLAY_TOGETHER"
        
        self.is_save_input_active = False
        self.input_text = ""
        self.cursor_visible = True        # Trạng thái con trỏ
        self.cursor_timer = 0             # Hẹn giờ nhấp nháy
        self.save_prefix = "Save_2P_"

        self.env = SnakeEnv2P()
        self.snake_sprites_p1 = {}
        self.snake_sprites_p2 = {}
        self._load_snake_sprites(self.snake_sprites_p1, "snake_sprites")
        self._load_snake_sprites(self.snake_sprites_p2, "snake_sprites2")
        self._load_ui_assets()

        self.current_speed = s.BASE_SPEED
        self.input_q1 = []
        self.input_q2 = []

        self._load_background() 
        
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.btn_back_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)
        
        # UI Pause & Save
        self.is_paused = False
        self.is_game_over = False
        
        self.resume_rect = pygame.Rect(cx - 100, cy - 60, 200, 50)
        self.save_quit_rect = pygame.Rect(cx - 100, cy + 10, 200, 50)
        self.quit_rect = pygame.Rect(cx - 100, cy + 80, 200, 50)
        
        self.first_frame = True
#---------------------------------------

    def _load_ui_assets(self):
        try:
            self.img_play_again = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_main_menu = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "red_button00.png"), (200, 50))
            self.img_resume = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_quit_blue = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "blue_button00.png"), (200, 50))
            self.img_save = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
        except FileNotFoundError:
            print("Lỗi load ảnh UI")
            sys.exit()

    def _load_background(self):
        try:
            bg_path = Path(__file__).parent.parent / "assets/play_together_board.png"
            self.bg_image = pygame.image.load(bg_path)
            self.bg_image = pygame.transform.scale(self.bg_image, (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused
#--------------------------------------
                    self.is_save_input_active = False
                    self.input_text = ""
                    pygame.key.set_repeat(0) # Tắt lặp phím khi pause
#---------------------------------------

                # Player 1
                d1 = None
                if event.key == s.P1_CONTROLS["UP"]: d1 = (0, -1)
                elif event.key == s.P1_CONTROLS["DOWN"]: d1 = (0, 1)
                elif event.key == s.P1_CONTROLS["LEFT"]: d1 = (-1, 0)
                elif event.key == s.P1_CONTROLS["RIGHT"]: d1 = (1, 0)
                if d1: self.input_q1.append(d1)

                # Player 2
                d2 = None
                if event.key == s.P2_CONTROLS["UP"]: d2 = (0, -1)
                elif event.key == s.P2_CONTROLS["DOWN"]: d2 = (0, 1)
                elif event.key == s.P2_CONTROLS["LEFT"]: d2 = (-1, 0)
                elif event.key == s.P2_CONTROLS["RIGHT"]: d2 = (1, 0)
                if d2: self.input_q2.append(d2)

#---------------------------------------
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
        # Render chữ prefix ra trước để đo kích thước
        prefix_surf = self.font.render(self.save_prefix, True, (255, 255, 0)) # Màu vàng cho nổi
        
        # Tính toán vị trí:
        # Tổng chiều rộng = Width(Prefix) + 10px (khoảng cách) + 300px (Input Box)
        # Để căn giữa cả cụm này
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
                        # Chỉ lưu nếu người dùng đã nhập gì đó (hoặc cho phép rỗng nếu muốn Save_PvP_ không)
                        # Ở đây ta cho phép rỗng, tên file sẽ là "Save_PvP_"
                        
                        # GHÉP TIỀN TỐ + INPUT
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
                        # Giới hạn độ dài nhập vào (ngắn hơn chút vì đã có prefix)
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

    def _handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_again_rect.collidepoint(event.pos):
                    self.env.reset()
                    self.input_q1 = []
                    self.input_q2 = []
                    self.is_game_over = False
                elif self.btn_back_rect.collidepoint(event.pos):
                    self.running = False

    def _get_next_move(self, queue, current_dir):
        if not queue: return current_dir
        next_dir = queue.pop(0)
        if (next_dir[0] + current_dir[0] == 0) and (next_dir[1] + current_dir[1] == 0):
            return current_dir
        return next_dir

    def _update_game(self):
        d1 = self._get_next_move(self.input_q1, self.env.p1_dir)
        d2 = self._get_next_move(self.input_q2, self.env.p2_dir)
        self.env.step(d1, d2)
        if self.env.game_over:
            self.is_game_over = True

    def _load_snake_sprites(self, sprite_dict, folder_name):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / f"assets/{folder_name}"
            sz = (s.GRID_SIZE, s.GRID_SIZE)
            def load_img(name):
                return pygame.transform.scale(pygame.image.load(SPRITE_PATH / name).convert_alpha(), sz)
            
            h_down = load_img("head_down.png")
            sprite_dict["head_down"] = h_down
            sprite_dict["head_up"] = pygame.transform.rotate(h_down, 180)
            sprite_dict["head_left"] = load_img("head_left.png")
            sprite_dict["head_right"] = load_img("head_right.png")
            sprite_dict["tail_up"] = load_img("tail_up.png")
            sprite_dict["tail_down"] = load_img("tail_down.png")
            sprite_dict["tail_left"] = load_img("tail_left.png")
            sprite_dict["tail_right"] = load_img("tail_right.png")
            sprite_dict["body_vertical"] = load_img("body_vertical.png")
            sprite_dict["body_horizontal"] = load_img("body_horizontal.png")
            sprite_dict["turn_UL"] = load_img("turn_UL.png")
            sprite_dict["turn_UR"] = load_img("turn_UR.png")
            sprite_dict["turn_DL"] = load_img("turn_DL.png")
            sprite_dict["turn_DR"] = load_img("turn_DR.png")
            sprite_dict["food"] = load_img("food.png")
            sprite_dict["poop"] = load_img("poop.png")
        except FileNotFoundError:
            sys.exit()

    def _draw_one_snake(self, snake_pos, direction, sprites):
        for index, pos in enumerate(snake_pos):
            rect = pygame.Rect(pos[0] * s.GRID_SIZE, pos[1] * s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE)
            sprite = None
            if index == 0:
                if direction == (0, -1): sprite = sprites["head_up"]
                elif direction == (0, 1): sprite = sprites["head_down"]
                elif direction == (-1, 0): sprite = sprites["head_left"]
                elif direction == (1, 0): sprite = sprites["head_right"]
            elif index == len(snake_pos) - 1:
                prev_pos = snake_pos[index - 1]
                vec_tail = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])
                if vec_tail == (0, -1): sprite = sprites["tail_up"]
                elif vec_tail == (0, 1): sprite = sprites["tail_down"]
                elif vec_tail == (-1, 0): sprite = sprites["tail_left"]
                elif vec_tail == (1, 0): sprite = sprites["tail_right"]
            else:
                prev_pos = snake_pos[index - 1]
                next_pos = snake_pos[index + 1]
                vec_prev = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])   
                vec_next = (next_pos[0] - pos[0], next_pos[1] - pos[1])   
                if vec_prev == vec_next:
                    if vec_prev in ((1, 0), (-1, 0)): sprite = sprites["body_horizontal"]
                    else: sprite = sprites["body_vertical"]
                else:
                    turn_map = {
                        ((0, 1), (-1, 0)): "turn_DL", ((1, 0), (0, -1)): "turn_DL",
                        ((0, 1), (1, 0)): "turn_DR",  ((-1, 0), (0, -1)): "turn_DR",
                        ((0, -1), (-1, 0)): "turn_UL", ((1, 0), (0, 1)): "turn_UL",
                        ((0, -1), (1, 0)): "turn_UR", ((-1, 0), (0, 1)): "turn_UR",
                    }
                    sprite_key = turn_map.get((vec_prev, vec_next))
                    if sprite_key: sprite = sprites[sprite_key]
            if sprite: self.screen.blit(sprite, rect)

    def _draw_elements(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(s.COLOR_BACKGROUND)
        
        if self.env.p1_alive:
            self._draw_one_snake(self.env.p1_pos, self.env.p1_dir, self.snake_sprites_p1)
        if self.env.p2_alive:
            self._draw_one_snake(self.env.p2_pos, self.env.p2_dir, self.snake_sprites_p2)

        if self.env.food_pos:
            fx, fy = self.env.food_pos
            self.screen.blit(self.snake_sprites_p1["food"], (fx*s.GRID_SIZE, fy*s.GRID_SIZE))
        
        if self.env.poop_pos:
            px, py = self.env.poop_pos
            self.screen.blit(self.snake_sprites_p1["poop"], (px*s.GRID_SIZE, py*s.GRID_SIZE))

        t1 = self.font.render(f"{self.name1}: {self.env.p1_score}", True, (255, 255, 255))
        t2 = self.font.render(f"{self.name2}: {self.env.p2_score}", True, (255, 255, 255))
        self.screen.blit(t1, (200, 50))
        self.screen.blit(t2, (s.SCREEN_WIDTH - 350, 50))

    def _draw_game_over_ui(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        w_txt = self.font_game_over.render(self.env.winner, True, (255, 255, 255))
        self.screen.blit(w_txt, w_txt.get_rect(center=(s.SCREEN_WIDTH//2, s.SCREEN_HEIGHT//2 - 20)))

        try:
            self.screen.blit(self.img_play_again, self.play_again_rect)
        except AttributeError:
            self.screen.blit(self.img_main_menu, self.play_again_rect)
        t = self.font.render("Play Again", True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=self.play_again_rect.center))

        self.screen.blit(self.img_main_menu, self.btn_back_rect)
        t2 = self.font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(t2, t2.get_rect(center=self.btn_back_rect.center))
    
#---------------------------------------
    # --- CÁC HÀM SAVE/LOAD ---
    def get_game_state(self):
        return {
            "mode": self.mode_id,
            "name1": self.name1,
            "name2": self.name2,
            "p1_score": self.env.p1_score,
            "p2_score": self.env.p2_score,
            "p1_pos": self.env.p1_pos,
            "p2_pos": self.env.p2_pos,
            "p1_dir": self.env.p1_dir,
            "p2_dir": self.env.p2_dir,
            "food_pos": self.env.food_pos,
            "poop_pos": self.env.poop_pos,
            "difficulty": self.current_speed 
        }

    def restore_game_state(self, data):
        if not data: return
        self.name1 = data.get("name1", "Player 1")
        self.name2 = data.get("name2", "Player 2")
        self.current_speed = data.get("difficulty", s.BASE_SPEED)
        self.env.p1_score = data.get("p1_score", 0)
        self.env.p2_score = data.get("p2_score", 0)
        self.env.p1_pos = data.get("p1_pos", [(10,10)])
        self.env.p2_pos = data.get("p2_pos", [(20,20)])
        d1 = data.get("p1_dir", (0, 0))
        d2 = data.get("p2_dir", (0, 0))
        self.env.p1_dir = (d1[0], d1[1])
        self.env.p2_dir = (d2[0], d2[1])
        f = data.get("food_pos")
        if f: self.env.food_pos = (f[0], f[1])
        p = data.get("poop_pos")
        if p: self.env.poop_pos = (p[0], p[1])
#---------------------------------------