import pygame
import sys
from snake import settings as s
from snake import save_manager
from pathlib import Path
from snake.core.env_snake import SnakeEnv
from snake.scenes.board import Board
from snake.core.sound_manager import SoundManager
from snake.scenes.setting import SettingPopup

ASSETS_PATH = Path(__file__).parent.parent / "assets"
ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"

class SoloLeveling(Board):
    def __init__(self, screen, nickname, avatar, difficulty, initial_state=None, save_name=None):
        
        self.avatar = avatar
        self.save_name_if_loaded = save_name
        
        super().__init__(screen, nickname, difficulty)

        self.sound_manager = SoundManager() 
        self.sound_manager.play_music("game")
  
        # Load assets riêng cho Solo
        self._load_solo_assets()
        self._load_snake_sprites()

        # Nếu là game load lại, set state
        if initial_state:
            self.env.set_state(initial_state)
            self.current_speed = initial_state.get("speed", difficulty)

    def _load_solo_assets(self):
        try:
            self.img_solo_leveling_board = pygame.transform.scale(pygame.image.load(ONE_PLAYER_ASSETS_PATH / "solo_leveling_board.png"), (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            self.img_avartar = pygame.image.load(ASSETS_PATH / f"{self.avatar}.png").convert_alpha()
        except FileNotFoundError:
            print("Lỗi load ảnh nền/avatar Solo")
            sys.exit()

    def _update_game(self):
        if not self.running: return 

        if self.input_queue:
            next_move = self.input_queue.pop(0)
            self.env.direction = next_move


        old_score = self.env.score

        state, reward, done, info = self.env.step(self.env.direction)


        if self.env.score > old_score:
            self.sound_manager.play_sfx("eat")
        elif self.env.score < old_score: 
            self.sound_manager.play_sfx("poop")

        if done:
            self.is_game_over = True
            self.sound_manager.play_sfx("die") 
            self.sound_manager.stop_music()
            if self.save_name_if_loaded:
                save_manager.delete_save(self.save_name_if_loaded)
                
    def _draw_elements(self):
        self.screen.blit(self.img_solo_leveling_board, (0, 0))
        self.screen.blit(self.img_avartar, (55, 31))

        # Vẽ rắn (Dùng lại logic vẽ cơ bản nếu cần, hoặc viết lại như dưới đây để tùy biến sprite)
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

        # Vẽ Items
        if self.env.food_pos:
            fp = self.env.food_pos
            self.screen.blit(self.snake_sprites["food"], (fp[0]*s.GRID_SIZE, fp[1]*s.GRID_SIZE))
        for p in self.env.poops:
            pp = p['pos']
            self.screen.blit(self.snake_sprites["poop"], (pp[0]*s.GRID_SIZE, pp[1]*s.GRID_SIZE))

        # UI Text
        name_txt = self.font.render(f"{self.nickname}", True, (255, 255, 255))
        self.screen.blit(name_txt, (178, 59))
        score_txt = self.font.render(f"Score: {self.env.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (1106, 59))
        
    def get_game_state(self):
        """Đóng gói dữ liệu để lưu"""
        return {
            "mode": "SOLO_LEVELING", 
            "nickname": self.nickname,
            "avatar": self.avatar,
            "difficulty": self.current_speed,
            "score": self.env.score,
            "snake_pos": self.env.snake_pos,
            "direction": self.env.direction,
            "food_pos": self.env.food_pos,
            "poops": self.env.poops
        }

    def restore_game_state(self, data):
        """Nạp dữ liệu từ file save vào game"""
        if not data: return
        
        # 1. Khôi phục thông số cơ bản
        self.nickname = data.get("nickname", "Player")
        self.current_speed = data.get("difficulty", 10)
        
        # 2. Khôi phục môi trường (Env)
        self.env.score = data.get("score", 0)
        self.env.snake_pos = [tuple(p) for p in data.get("snake_pos", [])] # Chuyển về tuple
        self.env.direction = tuple(data.get("direction", (1, 0)))
        self.env.food_pos = tuple(data.get("food_pos")) if data.get("food_pos") else None
        self.env.poops = data.get("poops", [])