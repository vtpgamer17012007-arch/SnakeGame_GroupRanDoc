import pygame
import sys
from snake import settings as s
from snake import save_manager
from pathlib import Path
from snake.core.env_snake import SnakeEnv

ASSETS_PATH = Path(__file__).parent.parent / "assets"
FONT_PATH = Path(__file__).parent.parent / "assets/fonts"

class SnakeRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.snake_sprites = {}
        self._load_assets()
        self.font = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 24)
        self.font_game_over = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 55)
        self.font_button = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 37)
        
        self.nickname = "The most STUPID snake in the World!"
     

    def _load_assets(self):
        SPRITE_PATH = Path(__file__).parent.parent / "assets/snake_sprites"
        ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"
        sz = (s.GRID_SIZE, s.GRID_SIZE)

        self.img_avartar = pygame.image.load(ASSETS_PATH/ "avatar6.png").convert_alpha()
        self.font_file = ASSETS_PATH / "fonts/Ruso-Regular.ttf"
        
        self.img_solo_leveling_board = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "AI_board.png"), (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        # Head
        self.snake_sprites["head_down"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_down.png").convert_alpha(), sz)
        self.snake_sprites["head_up"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_up.png").convert_alpha(), sz)
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

        

    def draw(self, env):
        self.screen.blit(self.img_solo_leveling_board, (0, 0))
        self.screen.blit(self.img_avartar, (55,31))
        snake_pos = env.snake_pos
        direction = env.direction
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
                    if vec_prev in ((1, 0), (-1, 0)):
                        sprite = self.snake_sprites["body_horizontal"]
                    else:
                        sprite = self.snake_sprites["body_vertical"]
                else:
                    turn_map = {
                        ((0, 1), (-1, 0)): "turn_DL", # Dưới -> Trái
                        ((1, 0), (0, -1)): "turn_DL", # Phải -> Lên
                        ((0, 1), (1, 0)): "turn_DR",  # Dưới -> Phải
                        ((-1, 0), (0, -1)): "turn_DR",# Trái -> Lên
                        ((0, -1), (-1, 0)): "turn_UL",# Trên -> Trái
                        ((1, 0), (0, 1)): "turn_UL",  # Phải -> Xuống
                        ((0, -1), (1, 0)): "turn_UR", # Trên -> Phải
                        ((-1, 0), (0, 1)): "turn_UR", # Trái -> Xuống
                    }
                    sprite_key = turn_map.get((vec_prev, vec_next))
                    if sprite_key:
                        sprite = self.snake_sprites[sprite_key]

            if sprite: self.screen.blit(sprite, rect)

        # Items
        if env.food_pos:
            fp = env.food_pos
            self.screen.blit(self.snake_sprites["food"], 
                             pygame.Rect(fp[0]*s.GRID_SIZE, fp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))
        
        for p in env.poops:
            pp = p['pos']
            self.screen.blit(self.snake_sprites["poop"], 
                             pygame.Rect(pp[0]*s.GRID_SIZE, pp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))
            
        #info
        name_txt = self.font.render(f"{self.nickname}", True, (255, 255, 255))
        self.screen.blit(name_txt, (178, 59))
        score_txt = self.font.render(f"Score: {env.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (1106, 59))

        