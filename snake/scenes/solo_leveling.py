import pygame
from snake.scenes.board import Board 
from snake import settings as s
from pathlib import Path

ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"

class SoloLeveling(Board):
    def __init__(self, screen, nickname, difficulty):
        super().__init__(screen, nickname, difficulty)
        # --- QUAN TRỌNG: ĐẶT TÊN CHẾ ĐỘ ---
        self.mode_id = "SOLO_LEVELING" 
        # ----------------------------------
        self._load_background()

    def _load_background(self):
        try:
            bg_path = ONE_PLAYER_ASSETS_PATH / "solo_leveling_board.png"
            self.bg_image = pygame.image.load(bg_path)
            self.bg_image = pygame.transform.scale(self.bg_image, (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        except FileNotFoundError:
            self.bg_image = None

    # --- HÀM TRẢ VỀ DỮ LIỆU ĐỂ LƯU ---
    def get_game_state(self):
        # Hàm này được Board gọi khi bấm Save
        return {
            "mode": self.mode_id,
            "nickname": self.nickname,
            "difficulty": self.current_speed,
            "score": self.env.score,
            "snake_pos": self.env.snake_pos,
            "direction": self.env.direction,
            "food_pos": self.env.food_pos,
            "poops": self.env.poops
        }

    # --- HÀM NẠP DỮ LIỆU KHI LOAD ---
    def restore_game_state(self, data):
        if not data: return
        # Khôi phục thông số
        self.nickname = data.get("nickname", "Player")
        self.current_speed = data.get("difficulty", s.BASE_SPEED)
        self.env.score = data.get("score", 0)
        
        # Khôi phục vị trí
        self.env.snake_pos = data.get("snake_pos", [(10,10), (10,11), (10,12)])
        d = data.get("direction", (0, -1))
        self.env.direction = (d[0], d[1])
        
        f = data.get("food_pos")
        if f: self.env.food_pos = (f[0], f[1])
        self.env.poops = data.get("poops", [])