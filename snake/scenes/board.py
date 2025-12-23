import pygame
import sys
from snake import settings as s
from snake import save_manager
from pathlib import Path
from snake.core.env_snake import SnakeEnv
from snake.core.sound_manager import SoundManager

ASSETS_PATH = Path(__file__).parent.parent / "assets"
FONT_PATH = Path(__file__).parent.parent / "assets/fonts"

class Board:
    def __init__(self, screen, nickname, difficulty=s.BASE_SPEED):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 24)
        self.font_game_over = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 55)
        self.font_button = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 37)

        self.nickname = nickname
        self.current_speed = difficulty
        self.is_game_over = False

        self.show_save_dialog = False     
        self.save_input_text = ""         
        self.input_placeholder = "Enter Save name..."
        self.game_state_to_save = {}
        self.is_paused = False
        self.font_input = pygame.font.Font(FONT_PATH / "more-sugar.thin.ttf", 30)
        

        self.env = SnakeEnv()
        self.input_queue = []
        self.snake_sprites = {}

        self.sound_manager = SoundManager() 
        self.sound_manager.play_music("game")
        
   
        self._load_ui_assets()
        self._define_layout()

    def _define_layout(self):
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(cx - 100, cy + 20, 200, 50)
        self.menu_rect = pygame.Rect(cx - 100, cy + 90, 200, 50)
        
        self.resume_rect = pygame.Rect(cx - 100, cy - 30, 200, 50)
        self.save_quit_rect = pygame.Rect(cx - 100, cy + 40, 200, 50)
        self.main_menu_pause_rect = pygame.Rect(cx - 100, cy + 110, 200, 50)
        
        self.confirm_overwrite_rect = pygame.Rect(cx - 100, cy, 200, 50)
        self.confirm_new_save_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)
        self.rename_input_rect = pygame.Rect(cx - 150, cy, 300, 50)
        self.rename_save_button_rect = pygame.Rect(cx - 100, cy + 70, 200, 50)
        
        self.input_box_rect = pygame.Rect(cx - 150, cy - 25, 300, 50)

    def _load_snake_sprites(self):
        try:
            SPRITE_PATH = Path(__file__).parent.parent / "assets/snake_sprites"
            sz = (s.GRID_SIZE, s.GRID_SIZE)

            h_down = pygame.image.load(SPRITE_PATH / "head_down.png").convert_alpha()
            self.snake_sprites["head_down"] = pygame.transform.scale(h_down, sz)
            self.snake_sprites["head_up"] = pygame.transform.rotate(self.snake_sprites["head_down"], 180)
            self.snake_sprites["head_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_left.png").convert_alpha(), sz)
            self.snake_sprites["head_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_right.png").convert_alpha(), sz)
            
            self.snake_sprites["tail_up"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_up.png").convert_alpha(), sz)
            self.snake_sprites["tail_down"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_down.png").convert_alpha(), sz)
            self.snake_sprites["tail_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_left.png").convert_alpha(), sz)
            self.snake_sprites["tail_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_right.png").convert_alpha(), sz)

            self.snake_sprites["body_vertical"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_vertical.png").convert_alpha(), sz)
            self.snake_sprites["body_horizontal"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_horizontal.png").convert_alpha(), sz)
            
            self.snake_sprites["turn_UL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UL.png").convert_alpha(), sz)
            self.snake_sprites["turn_UR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UR.png").convert_alpha(), sz)
            self.snake_sprites["turn_DL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DL.png").convert_alpha(), sz)
            self.snake_sprites["turn_DR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DR.png").convert_alpha(), sz)
            
            self.snake_sprites["food"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "food.png").convert_alpha(), sz)
            self.snake_sprites["poop"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "poop.png").convert_alpha(), sz)
        except FileNotFoundError:
            print("Lỗi load ảnh rắn Board")
            sys.exit()

    def _load_ui_assets(self):
        try:
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sound_manager.play_sfx("click")
                    self.is_paused = not self.is_paused
                
                target_dir = None
                if event.key == pygame.K_UP or event.key == pygame.K_w: target_dir = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: target_dir = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a: target_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: target_dir = (1, 0)
                
                if target_dir:
                    self.sound_manager.play_sfx("input")
                    if self.input_queue: last_dir = self.input_queue[-1]
                    else: last_dir = self.env.direction
                    
                    is_opposite = (last_dir[0] + target_dir[0] == 0) and (last_dir[1] + target_dir[1] == 0)
                    is_same = (last_dir == target_dir)

                    if not is_opposite and not is_same and len(self.input_queue) < 2:
                        self.input_queue.append(target_dir)

    def _update_game(self):
        
        if not self.running: return 

        if self.input_queue:
            next_move = self.input_queue.pop(0)
            self.env.direction = next_move

        state, reward, done, info = self.env.step(self.env.direction)
        if reward == 10: 
            self.sound_manager.play_sfx("eat")
        elif reward == -5:
            self.sound_manager.play_sfx("poop")

        if done:
            self.is_game_over = True
            self.sound_manager.play_sfx("die") 
            self.sound_manager.stop_music()
            if self.was_loaded_game and self.first_frame and self.save_name_if_loaded:
                save_manager.delete_save(self.save_name_if_loaded)
                self.loaded_and_died_instantly = True

    def get_game_state(self):
        return {}

    def _handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False

            if self.show_save_dialog:
                if event.type == pygame.KEYDOWN:
                    self.sound_manager.play_sfx("input")
                    if event.key == pygame.K_ESCAPE:
                        self.show_save_dialog = False
                        self.save_input_text = ""
                    
                    elif event.key == pygame.K_RETURN:
                        final_name = self.save_input_text.strip()
                        if not final_name: final_name = "Untitled" 
                        
                        save_manager.save_game(final_name, self.game_state_to_save)
                        self.running = False
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.save_input_text = self.save_input_text[:-1]
                    
                    else:
                        if len(self.save_input_text) < 15:
                            self.save_input_text += event.unicode

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.is_paused = False 
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.sound_manager.play_sfx("click")
                    if self.resume_rect.collidepoint(event.pos): 
                        self.is_paused = False
                    
                    elif self.main_menu_pause_rect.collidepoint(event.pos):
                        self.running = False
                    
                    elif self.save_quit_rect.collidepoint(event.pos):
                        
                        self.game_state_to_save = self.get_game_state()
                        self.show_save_dialog = True
                        self.save_input_text = "" 

    def _handle_game_over_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.play_again_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.sound_manager.play_music("game")   
                    self.sound_manager.stop_sfx("die")
                    self.sound_manager.stop_sfx("win")
                    self.env.reset()
                    self.is_game_over = False
                    self.input_queue = [] 
                if self.menu_rect.collidepoint(event.pos):
                    self.sound_manager.play_sfx("click")
                    self.sound_manager.stop_sfx("die")
                    self.sound_manager.stop_sfx("win")
                    self.running = False

    def _draw_overlay(self):
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def _draw_pause_ui(self):
        self._draw_overlay()
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
  
        if self.show_save_dialog:
            pygame.draw.rect(self.screen, (50, 50, 50), self.input_box_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.input_box_rect, 2)

            if self.save_input_text == "":
                txt_surf = self.font_button.render(self.input_placeholder, True, (150, 150, 150)) # Dùng font_button cho to rõ
            else:
                txt_surf = self.font_button.render(self.save_input_text, True, (255, 255, 255))
            
            self.screen.blit(txt_surf, txt_surf.get_rect(center=self.input_box_rect.center))
            
            hint = self.font.render("[ENTER] Save   [ESC] Cancel", True, (200, 200, 200))
            self.screen.blit(hint, hint.get_rect(center=(cx, self.input_box_rect.y + 70)))
        else:
            t = self.font_game_over.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(t, t.get_rect(center=(cx, self.resume_rect.y - 60)))
            
            self.screen.blit(self.img_resume, self.resume_rect)
            t_res = self.font_button.render("Resume", True, (255, 255, 255))
            self.screen.blit(t_res, t_res.get_rect(center=self.resume_rect.center))

            self.screen.blit(self.img_save_quit, self.save_quit_rect)
            t_save = self.font_button.render("Save & Quit", True, (255, 255, 255))
            self.screen.blit(t_save, t_save.get_rect(center=self.save_quit_rect.center))
            
            self.screen.blit(self.img_main_menu, self.main_menu_pause_rect)
            t_menu = self.font_button.render("Main Menu", True, (255, 255, 255))
            self.screen.blit(t_menu, t_menu.get_rect(center=self.main_menu_pause_rect.center))
            
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
        return "INTRO"