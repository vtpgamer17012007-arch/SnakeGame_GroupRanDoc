import pygame
import sys
import random
from snake import settings as s
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"


class Board:
    def __init__(self, screen, nickname, initial_state=None, save_name=None):
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
        
        # Thay đổi: Dùng danh sách thay vì biến đơn
        self.poops = [] 

        self.was_loaded_game = (initial_state is not None)
        self.save_name_if_loaded = save_name
        self.loaded_and_died_instantly = False
        self.first_frame = True

        self.snake_sprites = {}
        self._load_snake_sprites()

        center_x = s.SCREEN_WIDTH // 2
        center_y = s.SCREEN_HEIGHT // 2
        self.play_again_rect = pygame.Rect(center_x - 100, center_y + 20, 200, 50)
        self.menu_rect = pygame.Rect(center_x - 100, center_y + 90, 200, 50)
        self.resume_rect = pygame.Rect(center_x - 100, center_y - 30, 200, 50)
        self.save_quit_rect = pygame.Rect(center_x - 100, center_y + 40, 200, 50)
        self.confirm_overwrite_rect = pygame.Rect(center_x - 100, center_y, 200, 50)
        self.confirm_new_save_rect = pygame.Rect(center_x - 100, center_y + 70, 200, 50)
        self.rename_input_rect = pygame.Rect(center_x - 150, center_y, 300, 50)
        self.rename_save_button_rect = pygame.Rect(center_x - 100, center_y + 70, 200, 50)

        try:
            img_panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()
            img_btn_green = pygame.image.load(ASSETS_PATH / "green_button00.png").convert_alpha()
            img_btn_blue = pygame.image.load(ASSETS_PATH / "blue_button00.png").convert_alpha()
            img_btn_red = pygame.image.load(ASSETS_PATH / "red_button00.png").convert_alpha()
            img_btn_yellow = pygame.image.load(ASSETS_PATH / "yellow_button00.png").convert_alpha()

            self.img_play_again = pygame.transform.scale(img_btn_green, self.play_again_rect.size)
            self.img_main_menu = pygame.transform.scale(img_btn_red, self.menu_rect.size)
            self.img_resume = pygame.transform.scale(img_btn_green, self.resume_rect.size)
            self.img_save_quit = pygame.transform.scale(img_btn_blue, self.save_quit_rect.size)
            self.img_overwrite = pygame.transform.scale(img_btn_red, self.confirm_overwrite_rect.size)
            self.img_save_new = pygame.transform.scale(img_btn_yellow, self.confirm_new_save_rect.size)
            self.img_rename_bg = pygame.transform.scale(img_panel, self.rename_input_rect.size)
            self.img_rename_save = pygame.transform.scale(img_btn_green, self.rename_save_button_rect.size)
        except FileNotFoundError as e:
            print(f"Lỗi: Không tìm thấy file ảnh UI! {e}")
            pygame.quit()
            sys.exit()

        if initial_state:
            self.load_state(initial_state)
        else:
            self._reset_game()

    def _load_snake_sprites(self):
        """Tải và thay đổi kích thước các sprite của rắn (phiên bản directional)."""
        try:
            SPRITE_PATH = Path(__file__).parent.parent / "assets/snake_sprites"
            size = (s.GRID_SIZE, s.GRID_SIZE)

            head_down_img = pygame.image.load(SPRITE_PATH / "head_down.png").convert_alpha()
            self.snake_sprites["head_down"] = pygame.transform.scale(head_down_img, size)
            self.snake_sprites["head_up"] = pygame.transform.rotate(pygame.transform.scale(head_down_img, size), 180)
            self.snake_sprites["head_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_left.png").convert_alpha(), size)
            self.snake_sprites["head_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "head_right.png").convert_alpha(), size)

            self.snake_sprites["tail_up"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_up.png").convert_alpha(), size)
            self.snake_sprites["tail_down"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_down.png").convert_alpha(), size)
            self.snake_sprites["tail_left"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_left.png").convert_alpha(), size)
            self.snake_sprites["tail_right"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "tail_right.png").convert_alpha(), size)

            self.snake_sprites["body_vertical"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_vertical.png").convert_alpha(), size)
            self.snake_sprites["body_horizontal"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "body_horizontal.png").convert_alpha(), size)

            self.snake_sprites["turn_UL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UL.png").convert_alpha(), size)
            self.snake_sprites["turn_UR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_UR.png").convert_alpha(), size)
            self.snake_sprites["turn_DL"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DL.png").convert_alpha(), size)
            self.snake_sprites["turn_DR"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "turn_DR.png").convert_alpha(), size)

            self.snake_sprites["food"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "food.png").convert_alpha(), size)
            self.snake_sprites["poop"] = pygame.transform.scale(pygame.image.load(SPRITE_PATH / "poop.png").convert_alpha(), size)

        except FileNotFoundError as e:
            print(f"Lỗi: Không tìm thấy file ảnh rắn! {e}")
            print(f"Hãy chắc chắn thư mục assets nằm ở: {SPRITE_PATH} và bạn đã ĐỔI TÊN file.")
            pygame.quit()
            sys.exit()

    def load_state(self, game_state):
        """Tải trạng thái từ một dictionary (từ file save)."""
        self.snake_pos = [tuple(pos) for pos in game_state["snake_pos"]]
        self.direction = tuple(game_state["direction"])
        self.food_pos = tuple(game_state["food_pos"])
        self.score = game_state["score"]
        self.current_speed = game_state["speed"]
        self.nickname = game_state["nickname"]
        # Tải danh sách poop (mặc định là list rỗng nếu không có)
        self.poops = game_state.get("poops", [])

    def _reset_game(self):
        """Khởi tạo hoặc reset lại trạng thái game."""
        self.score = 0
        self.snake_pos = [(s.GRID_WIDTH // 2, s.GRID_HEIGHT // 2)]
        self.direction = (0, -1)
        self.current_speed = s.BASE_SPEED
        self.poops = [] # Reset danh sách
        self._spawn_food()
        self._spawn_poop()

    def _spawn_food(self):
        """Tạo mồi ở vị trí ngẫu nhiên không trùng với rắn."""
        while True:
            self.food_pos = (
                random.randint(0, s.GRID_WIDTH - 1),
                random.randint(0, s.GRID_HEIGHT - 1)
            )
            if self.food_pos not in self.snake_pos:
                break
    
    def _spawn_poop(self):
        """Tạo thêm 'Shit' vào danh sách (không trùng rắn/mồi/shit khác)."""
        # Tỉ lệ xuất hiện (ví dụ 100% để test)
        # if random.random() > 0.5: return

        while True:
            pos = (
                random.randint(0, s.GRID_WIDTH - 1),
                random.randint(0, s.GRID_HEIGHT - 1)
            )
            
            # Lấy danh sách vị trí các poop hiện tại
            existing_poops = [p['pos'] for p in self.poops]

            # Kiểm tra trùng
            if (pos not in self.snake_pos and 
                pos != self.food_pos and 
                pos not in existing_poops):
                
                # Thêm poop mới (age=0)
                self.poops.append({'pos': pos, 'age': 0})
                break

    def _handle_input(self):
        """Xử lý điều khiển của người chơi."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and self.direction != (0, 1):
                    self.direction = (0, -1)
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.direction != (0, -1):
                    self.direction = (0, 1)
                elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.direction != (1, 0):
                    self.direction = (-1, 0)
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.direction != (-1, 0):
                    self.direction = (1, 0)

    def _update_game(self):
        """Cập nhật logic game (di chuyển, va chạm)."""
        if not self.running:
            return

        head_x, head_y = self.snake_pos[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        if (
            new_head in self.snake_pos or
            new_head[0] < 0 or new_head[0] >= s.GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= s.GRID_HEIGHT
        ):
            self.is_game_over = True
            print(f"Game Over! Score: {self.score}")
            if self.was_loaded_game and self.first_frame and self.save_name_if_loaded:
                print(f"Save file {self.save_name_if_loaded} không hợp lệ. Đang xóa...")
                save_manager.delete_save(self.save_name_if_loaded)
                self.loaded_and_died_instantly = True
            return

        self.snake_pos.insert(0, new_head) # Chỉ insert 1 lần

        # Kiểm tra ăn Mồi
        if new_head == self.food_pos:
            self.score += 1
            self._spawn_food()
            
            # Tăng tuổi thọ poop và xóa poop già (>5 lượt)
            for p in self.poops:
                p['age'] += 1
            self.poops = [p for p in self.poops if p['age'] < 5]
            
            # Sinh poop mới
            self._spawn_poop()
            
        # Kiểm tra ăn Poop (so sánh với tất cả poop trong list)
        elif any(p['pos'] == new_head for p in self.poops):
            # Xóa cục poop bị ăn
            self.poops = [p for p in self.poops if p['pos'] != new_head]
            
            # Giảm độ dài rắn
            self.snake_pos.pop() 
            if len(self.snake_pos) > 1:
                self.snake_pos.pop()
            
            self.score = max(0, self.score - 2) 
            
        else:
            # Di chuyển bình thường
            self.snake_pos.pop()

    def _draw_elements(self):
        """Vẽ mọi thứ lên màn hình (phiên bản Sprite Directional CHÍNH XÁC)."""
        self.screen.fill(s.COLOR_BACKGROUND)

        for index, pos in enumerate(self.snake_pos):
            rect = pygame.Rect(pos[0] * s.GRID_SIZE, pos[1] * s.GRID_SIZE, s.GRID_SIZE, s.GRID_SIZE)
            sprite = None

            if index == 0:
                if self.direction == (0, -1): sprite = self.snake_sprites["head_up"]
                elif self.direction == (0, 1): sprite = self.snake_sprites["head_down"]
                elif self.direction == (-1, 0): sprite = self.snake_sprites["head_left"]
                elif self.direction == (1, 0): sprite = self.snake_sprites["head_right"]

            elif index == len(self.snake_pos) - 1:
                prev_pos = self.snake_pos[index - 1]
                vec_tail = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])

                if vec_tail == (0, -1): sprite = self.snake_sprites["tail_up"]
                elif vec_tail == (0, 1): sprite = self.snake_sprites["tail_down"]
                elif vec_tail == (-1, 0): sprite = self.snake_sprites["tail_left"]
                elif vec_tail == (1, 0): sprite = self.snake_sprites["tail_right"]

            else:
                prev_pos = self.snake_pos[index - 1]
                next_pos = self.snake_pos[index + 1]

                vec_prev = (pos[0] - prev_pos[0], pos[1] - prev_pos[1])   # hướng từ prev -> current (vào)
                vec_next = (next_pos[0] - pos[0], next_pos[1] - pos[1])   # hướng từ current -> next (ra)

                # nếu hai vector giống nhau => thẳng
                if vec_prev == vec_next:
                    if vec_prev in ((1, 0), (-1, 0)):
                        sprite = self.snake_sprites["body_horizontal"]
                    else:
                        sprite = self.snake_sprites["body_vertical"]

                else:
                    # DEBUG: bật True để in ra thông tin khi mapping không khớp
                    DEBUG_TURNS = False
                    # Giới hạn số dòng debug in ra để không spam console
                    if not hasattr(self, "_turn_debug_count"):
                        self._turn_debug_count = 0

                    # mapping có thứ tự: (vec_prev, vec_next) -> sprite_key
                    turn_map = {
                        # Dưới -> Trái ; Phải -> Lên
                        ((0, 1), (-1, 0)): "turn_DL",
                        ((1, 0), (0, -1)): "turn_DL",

                        # Dưới -> Phải ; Trái -> Lên
                        ((0, 1), (1, 0)): "turn_DR",
                        ((-1, 0), (0, -1)): "turn_DR",

                        # Trên -> Trái ; Phải -> Xuống
                        ((0, -1), (-1, 0)): "turn_UL",
                        ((1, 0), (0, 1)): "turn_UL",

                        # Trên -> Phải ; Trái -> Xuống
                        ((0, -1), (1, 0)): "turn_UR",
                        ((-1, 0), (0, 1)): "turn_UR",
                    }

                    sprite_key = turn_map.get((vec_prev, vec_next), None)

                    if sprite_key:
                        sprite = self.snake_sprites.get(sprite_key, None)
                    else:
                        # Nếu không khớp mapping (trường hợp bất ngờ), in debug một vài dòng để kiểm tra
                        sprite = self.snake_sprites.get("body_vertical", None)
                        if DEBUG_TURNS and self._turn_debug_count < 200:
                            print(f"[TURN DEBUG] idx={index} pos={pos} prev={prev_pos} next={next_pos} "
                                f"vec_prev={vec_prev} vec_next={vec_next} -> NO MATCH")
                            self._turn_debug_count += 1

            if sprite:
                self.screen.blit(sprite, rect)

        food_rect = pygame.Rect(
            self.food_pos[0] * s.GRID_SIZE,
            self.food_pos[1] * s.GRID_SIZE,
            s.GRID_SIZE,
            s.GRID_SIZE
        )
        self.screen.blit(self.snake_sprites["food"], food_rect)

        # Vẽ danh sách Poop
        for p in self.poops:
            pos = p['pos']
            poop_rect = pygame.Rect(
                pos[0] * s.GRID_SIZE,
                pos[1] * s.GRID_SIZE,
                s.GRID_SIZE,
                s.GRID_SIZE
            )
            self.screen.blit(self.snake_sprites["poop"], poop_rect)

        score_text = self.font.render(f"{self.nickname} Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (5, 5))

    def _draw_game_over_ui(self):
        """Vẽ UI 'Game Over' đè lên màn hình."""
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text_go = self.font_game_over.render("GAME OVER", True, (255, 0, 0))
        text_go_rect = text_go.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text_go, text_go_rect)

        if not self.loaded_and_died_instantly:
            self.screen.blit(self.img_play_again, self.play_again_rect)
            text_play = self.font_button.render("Play Again", True, (255, 255, 255))
            self.screen.blit(text_play, text_play.get_rect(center=self.play_again_rect.center))

        if self.loaded_and_died_instantly:
            menu_button_rect = self.play_again_rect
        else:
            menu_button_rect = self.menu_rect

        self.screen.blit(self.img_main_menu, menu_button_rect)
        text_menu = self.font_button.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(text_menu, text_menu.get_rect(center=menu_button_rect.center))

    def _handle_game_over_input(self):
        """Xử lý input khi màn hình Game Over đang hiển thị."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.loaded_and_died_instantly:
                    if self.play_again_rect.collidepoint(event.pos):
                        self._reset_game()
                        self.is_game_over = False

                if self.loaded_and_died_instantly:
                    menu_button_rect = self.play_again_rect
                else:
                    menu_button_rect = self.menu_rect

                if menu_button_rect.collidepoint(event.pos):
                    self.running = False

    def _draw_pause_ui(self):
        """Vẽ UI cho 3 trạng thái của menu Pause."""
        overlay = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        center_x = s.SCREEN_WIDTH // 2
        center_y = s.SCREEN_HEIGHT // 2

        if self.is_renaming_save:
            text_title = self.font_button.render("Enter New Save Name:", True, (255, 255, 255))
            self.screen.blit(text_title, text_title.get_rect(center=(center_x, center_y - 50)))
            self.screen.blit(self.img_rename_bg, self.rename_input_rect)
            text_input = self.font_button.render(self.new_save_name, True, (255, 255, 255))
            self.screen.blit(text_input, (self.rename_input_rect.x + 10, self.rename_input_rect.y + 10))
            self.screen.blit(self.img_rename_save, self.rename_save_button_rect)
            text_save = self.font_button.render("Save", True, (255, 255, 255))
            self.screen.blit(text_save, text_save.get_rect(center=self.rename_save_button_rect.center))

        elif self.is_confirming_save:
            text_title = self.font_button.render(f"File '{self.proposed_save_name}' already exists.", True, (255, 255, 0))
            self.screen.blit(text_title, text_title.get_rect(center=(center_x, center_y - 50)))
            self.screen.blit(self.img_overwrite, self.confirm_overwrite_rect)
            text_overwrite = self.font_button.render("Overwrite", True, (255, 255, 255))
            self.screen.blit(text_overwrite, text_overwrite.get_rect(center=self.confirm_overwrite_rect.center))
            self.screen.blit(self.img_save_new, self.confirm_new_save_rect)
            text_new = self.font_button.render("Save as New...", True, (255, 255, 255))
            self.screen.blit(text_new, text_new.get_rect(center=self.confirm_new_save_rect.center))

        else:
            text_paused = self.font_game_over.render("PAUSED", True, (255, 255, 0))
            self.screen.blit(text_paused, text_paused.get_rect(center=(center_x, center_y - 100)))
            self.screen.blit(self.img_resume, self.resume_rect)
            text_resume = self.font_button.render("Resume", True, (255, 255, 255))
            self.screen.blit(text_resume, text_resume.get_rect(center=self.resume_rect.center))
            self.screen.blit(self.img_save_quit, self.save_quit_rect)
            text_save_quit = self.font_button.render("Save & Quit", True, (255, 255, 255))
            self.screen.blit(text_save_quit, text_save_quit.get_rect(center=self.save_quit_rect.center))

    def _handle_pause_input(self):
        """Xử lý input cho 3 trạng thái của menu Pause."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_paused = False
                self.is_confirming_save = False
                self.is_renaming_save = False

            mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

            if self.is_renaming_save:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.new_save_name = self.new_save_name[:-1]
                    elif len(self.new_save_name) < 30:
                        self.new_save_name += event.unicode

                if mouse_clicked:
                    if self.rename_save_button_rect.collidepoint(event.pos) and self.new_save_name:
                        save_manager.save_game(self.new_save_name, self.game_state_to_save)
                        self.running = False

            elif self.is_confirming_save:
                if mouse_clicked:
                    if self.confirm_overwrite_rect.collidepoint(event.pos):
                        save_manager.save_game(self.proposed_save_name, self.game_state_to_save)
                        self.running = False

                    if self.confirm_new_save_rect.collidepoint(event.pos):
                        self.is_confirming_save = False
                        self.is_renaming_save = True
                        self.new_save_name = self.proposed_save_name

            else:
                if mouse_clicked:
                    if self.resume_rect.collidepoint(event.pos):
                        self.is_paused = False

                    if self.save_quit_rect.collidepoint(event.pos):
                        self.game_state_to_save = {
                            "snake_pos": self.snake_pos,
                            "direction": self.direction,
                            "food_pos": self.food_pos,
                            "poops": self.poops, # SỬA: Lưu cả danh sách poop
                            "score": self.score,
                            "speed": self.current_speed,
                            "nickname": self.nickname
                        }
                        self.proposed_save_name = f"{self.nickname} - Score {self.score}"

                        if save_manager.check_save_exists(self.proposed_save_name):
                            self.is_confirming_save = True
                        else:
                            save_manager.save_game(self.proposed_save_name, self.game_state_to_save)
                            self.running = False

    def run(self):
        """Vòng lặp game chính cho màn hình này."""
        while self.running:
            if self.is_paused:
                self._handle_pause_input()
            elif self.is_game_over:
                self._handle_game_over_input()
            else:
                self._handle_input()

            if not self.is_game_over and not self.is_paused:
                self._update_game()

            self._draw_elements()

            if self.is_game_over:
                self._draw_game_over_ui()

            if self.is_paused:
                self._draw_pause_ui()

            pygame.display.update()

            self.clock.tick(self.current_speed)

            self.first_frame = False

        return "INTRO"