# Tạo file: snake/scenes/board_2p.py
import pygame
import sys
from snake import settings as s
from snake.core.env_2p import SnakeEnv2P
from snake.scenes.board import Board # Kế thừa để dùng lại hàm load ảnh
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"
FONT_PATH = Path(__file__).parent.parent / "assets/fonts"

class PlayTogether(Board):
    def __init__(self, screen, avatar1, avatar2, name1="Player 1", name2="Player 2"):
        # Khởi tạo cơ bản, không cần load state hay save
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.name1 = name1 # Lưu tên
        self.name2 = name2 # Lưu tên
        self.avatar1 = avatar1
        self.avatar2 = avatar2
        self.font = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 24)
        self.font_game_over = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 55)
        self.font_button = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 37)
        
        self.env = SnakeEnv2P()
        self.snake_sprites = {}
        self.snake_sprites_p1 = {}
        self.snake_sprites_p2 = {}
        self._load_snake_sprites(self.snake_sprites_p1, "snake_sprites")
        self._load_snake_sprites(self.snake_sprites_p2, "snake_sprites2")
        self._load_ui_assets()     # Dùng lại hàm của cha
        
        # Queue input cho 2 người chơi
        self.input_q1 = []
        self.input_q2 = []

        self._load_background() # Gọi hàm load nền
        self._load_ui_assets() 
        # Nút Play Again và Back
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.btn_back_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)
        # Pause related
        self.is_paused = False
        self.is_confirming_save = False
        self.is_renaming_save = False
        self.proposed_save_name = ""
        self.new_save_name = ""
        self.game_state_to_save = {}
        self.resume_rect = pygame.Rect(cx - 100, cy - 30, 200, 50)
        self.save_quit_rect = pygame.Rect(cx - 100, cy + 40, 200, 50)
        self.confirm_overwrite_rect = pygame.Rect(cx - 100, cy, 200, 50)
        self.confirm_new_save_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)
        self.rename_input_rect = pygame.Rect(cx - 150, cy, 300, 50)
        self.rename_save_button_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)

    def _load_background(self):
        self.bg_image = pygame.image.load(ASSETS_PATH/ "play_together_board.png").convert_alpha()

        self.img_avartar_player1 = pygame.image.load(ASSETS_PATH/ f"{self.avatar1}.png").convert_alpha()
        self.img_avartar_player2 = pygame.image.load(ASSETS_PATH/ f"{self.avatar2}.png").convert_alpha()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # toggle pause
                    self.is_paused = not self.is_paused

                # Input Player 1 (Mũi tên)
                d1 = None
                if event.key == s.P1_CONTROLS["UP"]: d1 = (0, -1)
                elif event.key == s.P1_CONTROLS["DOWN"]: d1 = (0, 1)
                elif event.key == s.P1_CONTROLS["LEFT"]: d1 = (-1, 0)
                elif event.key == s.P1_CONTROLS["RIGHT"]: d1 = (1, 0)
                if d1: self.input_q1.append(d1)

                # Input Player 2 (WASD)
                d2 = None
                if event.key == s.P2_CONTROLS["UP"]: d2 = (0, -1)
                elif event.key == s.P2_CONTROLS["DOWN"]: d2 = (0, 1)
                elif event.key == s.P2_CONTROLS["LEFT"]: d2 = (-1, 0)
                elif event.key == s.P2_CONTROLS["RIGHT"]: d2 = (1, 0)
                if d2: self.input_q2.append(d2)

    def _get_next_move(self, queue, current_dir):
        if not queue: return current_dir
        next_dir = queue.pop(0)
        # Chặn đi ngược chiều
        if (next_dir[0] + current_dir[0] == 0) and (next_dir[1] + current_dir[1] == 0):
            return current_dir
        return next_dir

    def _update_game(self):
        if self.env.game_over: return

        # Lấy move tiếp theo cho P1 và P2
        d1 = self._get_next_move(self.input_q1, self.env.p1_dir)
        d2 = self._get_next_move(self.input_q2, self.env.p2_dir)
        
        self.env.step(d1, d2)
    def _load_snake_sprites(self, sprite_dict, folder_name):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / f"assets/{folder_name}"
            sz = (s.GRID_SIZE, s.GRID_SIZE)
            
            # Helper load ảnh cho gọn
            def load_img(name):
                return pygame.transform.scale(pygame.image.load(SPRITE_PATH / name).convert_alpha(), sz)

            # Head
            h_down = load_img("head_down.png")
            sprite_dict["head_down"] = h_down
            sprite_dict["head_up"] = pygame.transform.rotate(h_down, 180)
            sprite_dict["head_left"] = load_img("head_left.png")
            sprite_dict["head_right"] = load_img("head_right.png")
            
            # Tail
            sprite_dict["tail_up"] = load_img("tail_up.png")
            sprite_dict["tail_down"] = load_img("tail_down.png")
            sprite_dict["tail_left"] = load_img("tail_left.png")
            sprite_dict["tail_right"] = load_img("tail_right.png")

            # Body & Turns
            sprite_dict["body_vertical"] = load_img("body_vertical.png")
            sprite_dict["body_horizontal"] = load_img("body_horizontal.png")
            sprite_dict["turn_UL"] = load_img("turn_UL.png")
            sprite_dict["turn_UR"] = load_img("turn_UR.png")
            sprite_dict["turn_DL"] = load_img("turn_DL.png")
            sprite_dict["turn_DR"] = load_img("turn_DR.png")
            
            # Items (Chỉ cần load 1 lần nhưng để đây cũng không sao)
            sprite_dict["food"] = load_img("food.png")
            sprite_dict["poop"] = load_img("poop.png")

        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy thư mục ảnh 'assets/{folder_name}'")
            sys.exit()

    def _draw_one_snake(self, snake_pos, direction, sprites):
        for index, pos in enumerate(snake_pos):
            rect = pygame.Rect(pos[0] * s.GRID_SIZE, pos[1] * s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE)
            sprite = None

            # 1. Vẽ Đầu
            if index == 0:
                if direction == (0, -1): sprite = sprites["head_up"]
                elif direction == (0, 1): sprite = sprites["head_down"]
                elif direction == (-1, 0): sprite = sprites["head_left"]
                elif direction == (1, 0): sprite = sprites["head_right"]

            # 2. Vẽ Đuôi
            elif index == len(snake_pos) - 1:
                prev_pos = snake_pos[index - 1]
                vec_tail = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])
                if vec_tail == (0, -1): sprite = sprites["tail_up"]
                elif vec_tail == (0, 1): sprite = sprites["tail_down"]
                elif vec_tail == (-1, 0): sprite = sprites["tail_left"]
                elif vec_tail == (1, 0): sprite = sprites["tail_right"]

            # 3. Vẽ Thân & Góc cua
            else:
                prev_pos = snake_pos[index - 1]
                next_pos = snake_pos[index + 1]
                vec_prev = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])   
                vec_next = (next_pos[0] - pos[0], next_pos[1] - pos[1])   

                if vec_prev == vec_next: # Đi thẳng
                    if vec_prev in ((1, 0), (-1, 0)):
                        sprite = sprites["body_horizontal"]
                    else:
                        sprite = sprites["body_vertical"]
                else: # Cua
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
        
        # Vẽ rắn P1
        if self.env.p1_alive:
            self._draw_one_snake(self.env.p1_pos, self.env.p1_dir, self.snake_sprites_p1)
            
        # Vẽ Rắn P2
        if self.env.p2_alive:
            self._draw_one_snake(self.env.p2_pos, self.env.p2_dir, self.snake_sprites_p2)

        # Vẽ Food (Táo)
        if self.env.food_pos:
            fx, fy = self.env.food_pos
            self.screen.blit(self.snake_sprites_p1["food"], (fx*s.GRID_SIZE, fy*s.GRID_SIZE))

        # Vẽ Poop (Shit)
        if self.env.poop_pos:
            px, py = self.env.poop_pos
            self.screen.blit(self.snake_sprites_p1["poop"], (px*s.GRID_SIZE, py*s.GRID_SIZE))

        # UI Score
        t1 = self.font.render(f"{self.name1}: {self.env.p1_score}", True, (255, 255, 255)) # Chữ trang
        t2 = self.font.render(f"{self.name2}: {self.env.p2_score}", True, (255, 255, 255)) # Chữ trang
        self.screen.blit(t1, (200, 50))
        self.screen.blit(t2, (s.SCREEN_WIDTH - 350, 50))

        # Vẽ avatar
        self.screen.blit(self.img_avartar_player1, (55,31))
        self.screen.blit(self.img_avartar_player2, (1117,31))

        # Game Over UI
        if self.env.game_over:
            overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            w_txt = self.font_big.render(self.env.winner, True, (255, 255, 255))
            self.screen.blit(w_txt, w_txt.get_rect(center=(s.SCREEN_WIDTH//2, s.SCREEN_HEIGHT//2 - 20)))

            # Play Again button
            try:
                self.screen.blit(self.img_play_again, self.play_again_rect)
            except AttributeError:
                self.screen.blit(self.img_main_menu, self.play_again_rect)
            t = self.font.render("Play Again", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.play_again_rect.center))

            # Main Menu button
            self.screen.blit(self.img_main_menu, self.btn_back_rect)
            t2 = self.font.render("Main Menu", True, (255, 255, 255))
            self.screen.blit(t2, t2.get_rect(center=self.btn_back_rect.center))

    def _draw_overlay(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def _draw_pause_ui(self):
        # Dark overlay + PAUSED title + Resume / Save & Quit
        self._draw_overlay()
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        t = self.font_big.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(t, t.get_rect(center=(cx, self.resume_rect.y - 50)))

        # Resume button
        try:
            self.screen.blit(self.img_resume, self.resume_rect)
        except AttributeError:
            self.screen.blit(self.img_main_menu, self.resume_rect)
        self.screen.blit(self.font_button.render("Resume", True, (255,255,255)),
                         self.font_button.render("Resume", True, (255,255,255)).get_rect(center=self.resume_rect.center))

        # Save & Quit button
        try:
            self.screen.blit(self.img_save_quit, self.save_quit_rect)
        except AttributeError:
            self.screen.blit(self.img_main_menu, self.save_quit_rect)
        self.screen.blit(self.font_button.render("Save & Quit", True, (255,255,255)),
                         self.font_button.render("Save & Quit", True, (255,255,255)).get_rect(center=self.save_quit_rect.center))

    def _handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_paused = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.resume_rect.collidepoint(event.pos):
                    self.is_paused = False
                if self.save_quit_rect.collidepoint(event.pos):
                    # For 2-player mode we simply quit to intro on Save & Quit
                    self.running = False

    def _handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_again_rect.collidepoint(event.pos):
                    # Restart the 2-player game
                    self.env.reset()
                    self.input_q1 = []
                    self.input_q2 = []
                elif self.btn_back_rect.collidepoint(event.pos):
                    self.running = False # Quay về Intro

    def run(self):
        while self.running:
            if self.is_paused:
                self._handle_pause_input()
            elif self.env.game_over:
                self._handle_game_over_input()
            else:
                self._handle_input()

            if not self.env.game_over and not self.is_paused:
                self._update_game()

            self._draw_elements()
            if self.is_paused:
                self._draw_pause_ui()

            pygame.display.update()
            self.clock.tick(10)
        return "INTRO"