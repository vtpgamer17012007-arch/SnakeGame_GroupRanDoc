import pygame
import sys
from snake import settings as s
from snake import save_manager
from pathlib import Path
from snake.core.env_snake import SnakeEnv

ASSETS_PATH = Path(__file__).parent.parent / "assets"
ONE_PLAYER_ASSETS_PATH = Path(__file__).parent.parent / "assets/1_player_asset"
class SoloLeveling:
    def __init__(self, screen, nickname, difficulty, initial_state=None, save_name=None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_game_over = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_button = pygame.font.SysFont('Arial', 30)
        
        self.nickname = nickname
        self.is_game_over = False
        self.is_paused = False
        self.is_confirming_save = False 
        self.is_renaming_save = False   
        self.proposed_save_name = ""
        self.new_save_name = ""
        self.game_state_to_save = {}

        self.env = SnakeEnv()

        self.was_loaded_game = (initial_state is not None)
        self.save_name_if_loaded = save_name
        self.loaded_and_died_instantly = False
        self.first_frame = True 

        self.current_speed = difficulty

        self.input_queue = []
        self.snake_sprites = {}
        self._load_snake_sprites()
        self._load_ui_assets()
        
       
        

        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.menu_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)
        self.resume_rect = pygame.Rect(cx - 100, cy - 30, 200, 50)
        self.save_quit_rect = pygame.Rect(cx - 100, cy + 40, 200, 50)
        self.confirm_overwrite_rect = pygame.Rect(cx - 100, cy, 200, 50)
        self.confirm_new_save_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)
        self.rename_input_rect = pygame.Rect(cx - 150, cy, 300, 50)
        self.rename_save_button_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)

    def _load_snake_sprites(self):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / "assets/snake_sprites"
            sz = (s.GRID_SIZE, s.GRID_SIZE)
            
            # Head
            self.snake_sprites["head_down"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_down.png").convert_alpha(), sz)
            self.snake_sprites["head_up"] = pygame.transform.rotate(pygame.image.load(SPRITE_PATH / "head_up.png").convert_alpha(), sz)
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
            self.img_solo_leveling_board = pygame.transform.scale(pygame.image.load(ONE_PLAYER_ASSETS_PATH / "solo_leveling_board.png"), (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
            self.img_play_again = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_main_menu = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "red_button00.png"), (200, 50))
            self.img_resume = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
            self.img_save_quit = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "blue_button00.png"), (200, 50))
            self.img_overwrite = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "red_button00.png"), (200, 50))
            self.img_save_new = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "yellow_button00.png"), (200, 50))
            self.img_rename_bg = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "grey_panel.png"), (300, 50))
            self.img_rename_save = pygame.transform.scale(pygame.image.load(ASSETS_PATH / "green_button00.png"), (200, 50))
        except FileNotFoundError:
            print("Lỗi load ảnh UI")
            sys.exit()

    def _handle_input(self):
        """Xử lý điều khiển: Đưa lệnh vào hàng đợi (Input Buffer)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused
                
                # Xác định hướng
                target_dir = None
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    target_dir = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    target_dir = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    target_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    target_dir = (1, 0)
                
                if target_dir:
                    if self.input_queue:
                        last_dir = self.input_queue[-1]
                    else:
                        last_dir = self.env.direction
                    
                    is_opposite = (last_dir[0] + target_dir[0] == 0) and (last_dir[1] + target_dir[1] == 0)
                    is_same = (last_dir == target_dir)

                    if not is_opposite and not is_same:
                        # Giới hạn hàng đợi để tránh lag
                        if len(self.input_queue) < 2:
                            self.input_queue.append(target_dir)

    def _update_game(self):
        if not self.running: return 

        if self.input_queue:
            next_move = self.input_queue.pop(0)
            self.env.direction = next_move

        state, reward, done, info = self.env.step(self.env.direction)

        if done:
            self.is_game_over = True
            if self.was_loaded_game and self.first_frame and self.save_name_if_loaded:
                save_manager.delete_save(self.save_name_if_loaded)
                self.loaded_and_died_instantly = True

    def _draw_elements(self):
        
        self.screen.blit(self.img_solo_leveling_board, (0, 0))
        
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
                
                # vec_prev: hướng từ prev -> current (vào)
                vec_prev = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])   
                # vec_next: hướng từ current -> next (ra)
                vec_next = (next_pos[0] - pos[0], next_pos[1] - pos[1])   

                if vec_prev == vec_next:
                    if vec_prev in ((1, 0), (-1, 0)):
                        sprite = self.snake_sprites["body_horizontal"]
                    else:
                        sprite = self.snake_sprites["body_vertical"]
                else:
                    # Mapping
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
        if self.env.food_pos:
            fp = self.env.food_pos
            self.screen.blit(self.snake_sprites["food"], 
                             pygame.Rect(fp[0]*s.GRID_SIZE, fp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))
        
        for p in self.env.poops:
            pp = p['pos']
            self.screen.blit(self.snake_sprites["poop"], 
                             pygame.Rect(pp[0]*s.GRID_SIZE, pp[1]*s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE))

        score_txt = self.font.render(f"{self.nickname}'s Score: {self.env.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (200, 60))

    def _draw_game_over_ui(self):
        self._draw_overlay()
        text = self.font_game_over.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(text, text.get_rect(center=(s.SCREEN_WIDTH//2, s.SCREEN_HEIGHT//2 - 50)))
        
        if not self.loaded_and_died_instantly:
            self.screen.blit(self.img_play_again, self.play_again_rect)
            t = self.font_button.render("Play Again", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.play_again_rect.center))

        menu_r = self.play_again_rect if self.loaded_and_died_instantly else self.menu_rect
        self.screen.blit(self.img_main_menu, menu_r)
        t = self.font_button.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(t, t.get_rect(center=menu_r.center))

    def _draw_pause_ui(self):
        self._draw_overlay()
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        
        if self.is_renaming_save:
            t = self.font_button.render("New Save Name:", True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=(cx, self.rename_input_rect.y - 30)))
            self.screen.blit(self.img_rename_bg, self.rename_input_rect)
            self.screen.blit(self.font_button.render(self.new_save_name, True, (255,255,255)), 
                             (self.rename_input_rect.x+10, self.rename_input_rect.y+10))
            self.screen.blit(self.img_rename_save, self.rename_save_button_rect)
            t = self.font_button.render("Save", True, (255,255,255))
            self.screen.blit(t, t.get_rect(center=self.rename_save_button_rect.center))
        elif self.is_confirming_save:
            t = self.font_button.render("File Exists!", True, (255,255,0))
            self.screen.blit(t, t.get_rect(center=(cx, self.confirm_overwrite_rect.y - 30)))
            self.screen.blit(self.img_overwrite, self.confirm_overwrite_rect)
            self.screen.blit(self.font_button.render("Overwrite", True, (255,255,255)), 
                             self.font_button.render("Overwrite", True, (255,255,255)).get_rect(center=self.confirm_overwrite_rect.center))
            self.screen.blit(self.img_save_new, self.confirm_new_save_rect)
            self.screen.blit(self.font_button.render("Save New", True, (255,255,255)), 
                             self.font_button.render("Save New", True, (255,255,255)).get_rect(center=self.confirm_new_save_rect.center))
        else:
            t = self.font_game_over.render("PAUSED", True, (255,255,0))
            self.screen.blit(t, t.get_rect(center=(cx, self.resume_rect.y - 50)))
            self.screen.blit(self.img_resume, self.resume_rect)
            self.screen.blit(self.font_button.render("Resume", True, (255,255,255)), 
                             self.font_button.render("Resume", True, (255,255,255)).get_rect(center=self.resume_rect.center))
            self.screen.blit(self.img_save_quit, self.save_quit_rect)
            self.screen.blit(self.font_button.render("Save & Quit", True, (255,255,255)), 
                             self.font_button.render("Save & Quit", True, (255,255,255)).get_rect(center=self.save_quit_rect.center))

    def _draw_overlay(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def _handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.loaded_and_died_instantly and self.play_again_rect.collidepoint(event.pos):
                    self.env.reset(); self.is_game_over = False
                menu_rect = self.play_again_rect if self.loaded_and_died_instantly else self.menu_rect
                if menu_rect.collidepoint(event.pos): self.running = False

    def _handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_paused = False; self.is_confirming_save = False; self.is_renaming_save = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_renaming_save:
                    if self.rename_save_button_rect.collidepoint(event.pos) and self.new_save_name:
                        save_manager.save_game(self.new_save_name, self.game_state_to_save); self.running = False
                elif self.is_confirming_save:
                    if self.confirm_overwrite_rect.collidepoint(event.pos):
                        save_manager.save_game(self.proposed_save_name, self.game_state_to_save); self.running = False
                    if self.confirm_new_save_rect.collidepoint(event.pos):
                        self.is_confirming_save = False; self.is_renaming_save = True; self.new_save_name = self.proposed_save_name
                else:
                    if self.resume_rect.collidepoint(event.pos): self.is_paused = False
                    if self.save_quit_rect.collidepoint(event.pos):
                        self.game_state_to_save = {
                            "snake_pos": self.env.snake_pos, "direction": self.env.direction,
                            "food_pos": self.env.food_pos, "poops": self.env.poops,
                            "score": self.env.score, "speed": self.current_speed, "nickname": self.nickname
                        }
                        self.proposed_save_name = f"{self.nickname} - Score {self.env.score}"
                        if save_manager.check_save_exists(self.proposed_save_name): self.is_confirming_save = True
                        else:
                            save_manager.save_game(self.proposed_save_name, self.game_state_to_save); self.running = False
        
        if self.is_renaming_save:
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_BACKSPACE: self.new_save_name = self.new_save_name[:-1]
                elif len(self.new_save_name) < 20: self.new_save_name += event.unicode

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