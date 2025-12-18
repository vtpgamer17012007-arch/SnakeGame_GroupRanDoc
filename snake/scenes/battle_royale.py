# Tạo file: snake/scenes/board_2p.py
import pygame
import sys
from snake import settings as s
from snake.core.env_2pvp import SnakeEnv2Pvp
from snake.scenes.board import Board # Kế thừa để dùng lại hàm load ảnh
from pathlib import Path

class Battle(Board):
    def __init__(self, screen, name1="Player 1", name2="Player 2"):
        # Khởi tạo cơ bản, không cần load state hay save
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.name1 = name1 # Lưu tên
        self.name2 = name2 # Lưu tên
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_big = pygame.font.SysFont('Arial', 50, bold=True)
        
        self.env = SnakeEnv2Pvp()
        self.snake_sprites = {}
        self._load_snake_sprites() # Dùng lại hàm của cha
        self._load_ui_assets()     # Dùng lại hàm của cha
        
        # Queue input cho 2 người chơi
        self.input_q1 = []
        self.input_q2 = []

        self._load_background() # Gọi hàm load nền
        self._load_snake_sprites()
        self._load_ui_assets() 
        # Nút Play Again và Back
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.btn_back_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)

    def _load_background(self):
        try:
            bg_path = Path(__file__).parent.parent / "assets/play_together_board.png"
            self.bg_image = pygame.image.load(bg_path)
            self.bg_image = pygame.transform.scale(self.bg_image, (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.env.game_over:
                if self.play_again_rect.collidepoint(event.pos):
                    # Restart the battle game
                    self.env.reset()
                    self.input_q1 = []
                    self.input_q2 = []
                elif self.btn_back_rect.collidepoint(event.pos):
                    self.running = False # Quay về Intro
            
            if event.type == pygame.KEYDOWN:
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

    def _draw_snake(self, positions, direction, is_p2=False):
        
        # Nếu là P2, ta sẽ vẽ đè màu lên sprite để phân biệt
        for idx, pos in enumerate(positions):
            rect = pygame.Rect(pos[0]*s.GRID_SIZE, pos[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE)
            
            sprite = self.snake_sprites["body_vertical"] # Mặc định để test
            
            color = (0, 255, 0) if not is_p2 else (255, 200, 0) # P1 Xanh, P2 Vàng
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0,0,0), rect, 1)

    def _draw_elements(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(s.COLOR_BACKGROUND)
        
        # Vẽ rắn
        if self.env.p1_alive: self._draw_snake(self.env.p1_pos, self.env.p1_dir, is_p2=False)
        if self.env.p2_alive: self._draw_snake(self.env.p2_pos, self.env.p2_dir, is_p2=True)

        # Vẽ Food (Táo)
        if self.env.food_pos:
            fx, fy = self.env.food_pos
            self.screen.blit(self.snake_sprites["food"], (fx*s.GRID_SIZE, fy*s.GRID_SIZE))

        # Vẽ Poop (Shit)
        if self.env.poop_pos:
            px, py = self.env.poop_pos
            self.screen.blit(self.snake_sprites["poop"], (px*s.GRID_SIZE, py*s.GRID_SIZE))

        # UI Score
        t1 = self.font.render(f"{self.name1}: {self.env.p1_score}", True, (255, 255, 255)) # Chữ trang
        t2 = self.font.render(f"{self.name2}: {self.env.p2_score}", True, (255, 255, 255)) # Chữ trang
        self.screen.blit(t1, (200, 50))
        self.screen.blit(t2, (s.SCREEN_WIDTH - 250, 50))

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

    def run(self):
        while self.running:
            self._handle_input()
            self._update_game()
            self._draw_elements()
            pygame.display.update()
            self.clock.tick(10) 
        return "INTRO"