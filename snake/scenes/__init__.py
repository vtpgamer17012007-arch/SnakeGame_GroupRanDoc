import pygame
import sys
import random
from snake import settings as s


class Board:
    def __init__(self, screen):
            self.screen = screen
            self.clock = pygame.time.Clock()
            
            # Fonts
            self.font_title = pygame.font.SysFont('Arial', 60, bold=True)
            self.font_menu = pygame.font.SysFont('Arial', 40)
            self.font_input = pygame.font.SysFont('Arial', 30)
            
            # Trạng thái của màn hình intro
            self.running = True
            self.nickname = ""
            self.input_active = False 
            
            # Trạng thái menu load (ĐÂY LÀ PHẦN BỊ THIẾU)
            self.showing_load_menu = False 
            self.save_list = []
            self.save_rects = []
            
            # Giá trị trả về
            self.selected_mode = None
            self.selected_save = None 
            
            self._define_layout()

    def load_state(self, game_state):
        """Tải trạng thái từ một dictionary (từ file save)."""
        # Chuyển đổi list (từ JSON) về tuple (cho Pygame)
        self.snake_pos = [tuple(pos) for pos in game_state["snake_pos"]]
        self.direction = tuple(game_state["direction"])
        self.food_pos = tuple(game_state["food_pos"])
        self.score = game_state["score"]
        self.current_speed = game_state["speed"]
        self.nickname = game_state["nickname"]

    def _reset_game(self):
        """Khởi tạo hoặc reset lại trạng thái game."""
        self.score = 0
        self.snake_pos = [(s.GRID_WIDTH // 2, s.GRID_HEIGHT // 2)]
        self.direction = (0, -1)
        self.current_speed = s.BASE_SPEED # <-- Dùng tốc độ mới
        self._spawn_food()