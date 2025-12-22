import pygame
import sys
from snake import settings as s
from snake.core.env_2p import SnakeEnv2P
from snake.scenes.board import Board 
from pathlib import Path
from snake.core.sound_manager import SoundManager

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class PlayTogether(Board):
    def __init__(self, screen, avatar1, avatar2, name1="Player 1", name2="Player 2"):
        
        self.name1 = name1
        self.name2 = name2
        self.avatar1 = avatar1
        self.avatar2 = avatar2
        
        super().__init__(screen, name1, difficulty=10)
        
        # Override Environment
        self.env = SnakeEnv2P()
        self.input_q1 = []
        self.input_q2 = []
        
        # Sprites riêng cho 2 rắn
        self.snake_sprites_p1 = {}
        self.snake_sprites_p2 = {}
        self._load_snake_sprites()
        
        self._load_background()

        self.sound_manager = SoundManager() 
        self.sound_manager.play_music("game") 
    def _load_snake_sprites(self):
        self._load_one_set(self.snake_sprites_p1, "snake_sprites")
        self._load_one_set(self.snake_sprites_p2, "snake_sprites2")

    def _load_one_set(self, sprite_dict, folder_name):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / f"assets/{folder_name}"
            sz = (s.GRID_SIZE, s.GRID_SIZE)
            def load_img(name): return pygame.transform.scale(pygame.image.load(SPRITE_PATH / name).convert_alpha(), sz)
            
            sprite_dict["head_down"] = load_img("head_down.png")
            sprite_dict["head_up"] = pygame.transform.rotate(sprite_dict["head_down"], 180)
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
            print(f"Lỗi load sprite: {folder_name}")
    
    def _load_background(self):
        self.bg_image = pygame.image.load(ASSETS_PATH / "play_together_board.png").convert_alpha()
        self.img_avartar_player1 = pygame.image.load(ASSETS_PATH / f"{self.avatar1}.png").convert_alpha()
        self.img_avartar_player2 = pygame.image.load(ASSETS_PATH / f"{self.avatar2}.png").convert_alpha()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    self.is_paused = not self.is_paused
                    self.sound_manager.play_sfx("click")
                played_sound = False
                
                # P1 Controls
                d1 = None
                if event.key == s.P1_CONTROLS["UP"]: d1 = (0, -1)
                elif event.key == s.P1_CONTROLS["DOWN"]: d1 = (0, 1)
                elif event.key == s.P1_CONTROLS["LEFT"]: d1 = (-1, 0)
                elif event.key == s.P1_CONTROLS["RIGHT"]: d1 = (1, 0)
                if d1: 
                    self.input_q1.append(d1)
                    if not played_sound:
                        self.sound_manager.play_sfx("input")
                        played_sound = True

                # P2 Controls
                d2 = None
                if event.key == s.P2_CONTROLS["UP"]: d2 = (0, -1)
                elif event.key == s.P2_CONTROLS["DOWN"]: d2 = (0, 1)
                elif event.key == s.P2_CONTROLS["LEFT"]: d2 = (-1, 0)
                elif event.key == s.P2_CONTROLS["RIGHT"]: d2 = (1, 0)
                if d2: 
                    self.input_q2.append(d2)
                    if not played_sound:
                        self.sound_manager.play_sfx("input")
                        played_sound = True

    def _get_next_move(self, queue, current_dir):
        if not queue: return current_dir
        next_dir = queue.pop(0)
        if (next_dir[0] + current_dir[0] == 0) and (next_dir[1] + current_dir[1] == 0): return current_dir
        return next_dir

    
    def _update_game(self):
        if self.env.game_over: return

        # Lấy move tiếp theo cho P1 và P2
        # Lưu điểm cũ để so sánh
        old_p1 = self.env.p1_score
        old_p2 = self.env.p2_score

        d1 = self._get_next_move(self.input_q1, self.env.p1_dir)
        d2 = self._get_next_move(self.input_q2, self.env.p2_dir)
        
        self.env.step(d1, d2)

        #  Logic âm thanh
        if self.env.p1_score > old_p1 or self.env.p2_score > old_p2:
            self.sound_manager.play_sfx("eat")
        elif self.env.p1_score < old_p1 or self.env.p2_score < old_p2:
            self.sound_manager.play_sfx("poop")

        if self.env.game_over:
            self.is_game_over = True
            self.sound_manager.stop_music()
            self.sound_manager.play_sfx("die")
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
        self.screen.blit(self.bg_image, (0, 0))
        
        if self.env.p1_alive: self._draw_one_snake(self.env.p1_pos, self.env.p1_dir, self.snake_sprites_p1)
        if self.env.p2_alive: self._draw_one_snake(self.env.p2_pos, self.env.p2_dir, self.snake_sprites_p2)

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

        self.screen.blit(self.img_avartar_player1, (55,31))
        self.screen.blit(self.img_avartar_player2, (1117,31))
        
    def get_game_state(self):
        return {
            "mode": "PLAY_TOGETHER",
            "name1": self.name1,
            "name2": self.name2,
            "avatar1": self.avatar1, 
            "avatar2": self.avatar2,
            "p1_score": self.env.p1_score,
            "p2_score": self.env.p2_score,
            "p1_pos": self.env.p1_pos,
            "p2_pos": self.env.p2_pos,
            "p1_dir": self.env.p1_dir,
            "p2_dir": self.env.p2_dir,
            "p1_alive": self.env.p1_alive,
            "p2_alive": self.env.p2_alive,
            "food_pos": self.env.food_pos,
            "poop_pos": self.env.poop_pos
        }

    def restore_game_state(self, data):
        if not data: return
        self.name1 = data.get("name1", "Player 1")
        self.name2 = data.get("name2", "Player 2")
        
        # Env restore
        self.env.p1_score = data.get("p1_score", 0)
        self.env.p2_score = data.get("p2_score", 0)
        self.env.p1_alive = data.get("p1_alive", True)
        self.env.p2_alive = data.get("p2_alive", True)
        
        # Lưu ý: JSON lưu tuple thành list, cần ép kiểu lại về tuple để so sánh không bị lỗi
        self.env.p1_pos = [tuple(p) for p in data.get("p1_pos", [])]
        self.env.p2_pos = [tuple(p) for p in data.get("p2_pos", [])]
        self.env.p1_dir = tuple(data.get("p1_dir", (0, 0)))
        self.env.p2_dir = tuple(data.get("p2_dir", (0, 0)))
        
        self.env.food_pos = tuple(data.get("food_pos")) if data.get("food_pos") else None
        self.env.poop_pos = tuple(data.get("poop_pos")) if data.get("poop_pos") else None