import pygame
import sys
from snake import settings as s
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"


class Intro:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont('Arial', 60, bold=True)
        self.font_menu = pygame.font.SysFont('Arial', 40)
        self.font_input = pygame.font.SysFont('Arial', 30)
        self.font_button = pygame.font.SysFont('Arial', 30)

        self.running = True
        self.nickname = ""
        self.input_active = False
        self.showing_load_menu = False
        self.save_list = []
        self.save_rects = []

        self.selected_mode = None
        self.selected_save = None

        self.SAVES_PER_PAGE = 5
        self.current_page = 0

        self._define_layout()

        try:
            img_panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()
            img_btn_green = pygame.image.load(ASSETS_PATH / "green_button00.png").convert_alpha()
            img_btn_blue = pygame.image.load(ASSETS_PATH / "blue_button00.png").convert_alpha()
            img_btn_red = pygame.image.load(ASSETS_PATH / "red_button00.png").convert_alpha()

            self.img_input_bg = pygame.transform.scale(img_panel, self.input_rect.size)
            self.img_play_btn = pygame.transform.scale(img_btn_green, self.play_button_rect.size)
            self.img_ai_btn = pygame.transform.scale(img_btn_green, self.ai_button_rect.size)
            self.img_load_btn = pygame.transform.scale(img_btn_blue, self.load_button_rect.size)
            self.img_back_btn = pygame.transform.scale(img_btn_red, self.back_button_rect.size)
            self.img_save_slot = pygame.transform.scale(img_panel, (400, 50))
            self.img_next_btn = pygame.transform.scale(img_btn_blue, self.next_page_rect.size)
            self.img_prev_btn = pygame.transform.scale(img_btn_blue, self.prev_page_rect.size)

        except FileNotFoundError as e:
            print(f"Lỗi: Không tìm thấy file ảnh! {e}")
            print(f"Hãy chắc chắn thư mục assets nằm ở: {ASSETS_PATH}")
            # Tạo ảnh dự phòng (fallback) nếu không tìm thấy file
            self.img_input_bg = pygame.Surface(self.input_rect.size); self.img_input_bg.fill((50, 50, 50))
            self.img_play_btn = pygame.Surface(self.play_button_rect.size); self.img_play_btn.fill((0, 150, 0))
            self.img_ai_btn = pygame.Surface(self.ai_button_rect.size); self.img_ai_btn.fill((0, 0, 150))
            self.img_load_btn = pygame.Surface(self.load_button_rect.size); self.img_load_btn.fill((150, 75, 0))
            self.img_back_btn = pygame.Surface(self.back_button_rect.size); self.img_back_btn.fill((100, 100, 100))
            self.img_save_slot = pygame.Surface((400, 50)); self.img_save_slot.fill((50, 50, 50))
            self.img_next_btn = pygame.Surface(self.next_page_rect.size); self.img_next_btn.fill((0, 0, 150))
            self.img_prev_btn = pygame.Surface(self.prev_page_rect.size); self.img_prev_btn.fill((0, 0, 150))

    def _define_layout(self):
        """Định nghĩa vị trí các thành phần UI."""
        center_x = s.SCREEN_WIDTH // 2
        center_y = s.SCREEN_HEIGHT // 2

        self.input_rect = pygame.Rect(center_x - 150, center_y - 50, 300, 40)
        self.play_button_rect = pygame.Rect(center_x - 150, center_y + 20, 300, 50)
        self.ai_button_rect = pygame.Rect(center_x - 150, center_y + 90, 300, 50)
        self.load_button_rect = pygame.Rect(center_x - 150, center_y + 160, 300, 50)
        self.back_button_rect = pygame.Rect(20, s.SCREEN_HEIGHT - 60, 100, 40)
        self.next_page_rect = pygame.Rect(s.SCREEN_WIDTH - 60, center_y - 25, 50, 50)
        self.prev_page_rect = pygame.Rect(10, center_y - 25, 50, 50)

    def _build_current_page(self):
        """Tạo danh sách Rects cho các save game trên trang hiện tại."""
        self.save_rects = []
        start_index = self.current_page * self.SAVES_PER_PAGE
        end_index = start_index + self.SAVES_PER_PAGE
        current_page_saves = self.save_list[start_index:end_index]

        for i, save_name in enumerate(current_page_saves):
            rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 200, 150 + i * 60, 400, 50)
            self.save_rects.append(rect)

    def _handle_input(self):
        """Xử lý sự kiện (chuột, bàn phím)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"

            mouse_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

            if not self.showing_load_menu:
                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.nickname = self.nickname[:-1]
                        elif len(self.nickname) < 15:
                            self.nickname += event.unicode

                if mouse_clicked:
                    self.input_active = self.input_rect.collidepoint(event.pos)

                    if self.play_button_rect.collidepoint(event.pos) and self.nickname:
                        self.selected_mode = "PLAYER"
                        self.running = False

                    if self.ai_button_rect.collidepoint(event.pos) and self.nickname:
                        self.selected_mode = "AI"
                        self.running = False

                    if self.load_button_rect.collidepoint(event.pos):
                        self.showing_load_menu = True
                        self.save_list = save_manager.get_save_list()
                        self.current_page = 0
                        self._build_current_page()

            else:
                if mouse_clicked:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.showing_load_menu = False

                    total_pages = (len(self.save_list) + self.SAVES_PER_PAGE - 1) // self.SAVES_PER_PAGE
                    if self.next_page_rect.collidepoint(event.pos) and self.current_page < total_pages - 1:
                        self.current_page += 1
                        self._build_current_page()

                    if self.prev_page_rect.collidepoint(event.pos) and self.current_page > 0:
                        self.current_page -= 1
                        self._build_current_page()

                    for i, rect in enumerate(self.save_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_mode = "LOAD"
                            save_index = self.current_page * self.SAVES_PER_PAGE + i
                            self.selected_save = self.save_list[save_index]
                            self.running = False

    def _draw_elements(self):
        """Vẽ các thành phần lên màn hình."""
        self.screen.fill(s.COLOR_BACKGROUND)

        title_text = self.font_title.render("Snake Game", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(s.SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        if not self.showing_load_menu:
            self.screen.blit(self.img_input_bg, self.input_rect)
            input_surface = self.font_input.render(self.nickname, True, (255, 255, 255))
            self.screen.blit(input_surface, (self.input_rect.x + 15, self.input_rect.y + (self.input_rect.height - self.font_input.get_height()) // 2))
            if not self.nickname and not self.input_active:
                placeholder = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(placeholder, (self.input_rect.x + 15, self.input_rect.y + (self.input_rect.height - self.font_input.get_height()) // 2))

            self.screen.blit(self.img_play_btn, self.play_button_rect)
            play_text = self.font_menu.render("Player Play", True, (255, 255, 255))
            self.screen.blit(play_text, play_text.get_rect(center=self.play_button_rect.center))

            self.screen.blit(self.img_ai_btn, self.ai_button_rect)
            ai_text = self.font_menu.render("AI Play", True, (255, 255, 255))
            self.screen.blit(ai_text, ai_text.get_rect(center=self.ai_button_rect.center))

            self.screen.blit(self.img_load_btn, self.load_button_rect)
            load_text = self.font_menu.render("Load Game", True, (255, 255, 255))
            self.screen.blit(load_text, load_text.get_rect(center=self.load_button_rect.center))

        else:
            start_index = self.current_page * self.SAVES_PER_PAGE
            for i, rect in enumerate(self.save_rects):
                self.screen.blit(self.img_save_slot, rect)
                save_name = self.save_list[start_index + i]
                save_text = self.font_input.render(save_name, True, (255, 255, 255))
                self.screen.blit(save_text, save_text.get_rect(center=rect.center))

            self.screen.blit(self.img_back_btn, self.back_button_rect)
            back_text = self.font_button.render("Back", True, (255, 255, 255))
            self.screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))

            total_pages = (len(self.save_list) + self.SAVES_PER_PAGE - 1) // self.SAVES_PER_PAGE

            if self.current_page < total_pages - 1:
                self.screen.blit(self.img_next_btn, self.next_page_rect)
                next_text = self.font_menu.render(">", True, (255, 255, 255))
                self.screen.blit(next_text, next_text.get_rect(center=self.next_page_rect.center))

            if self.current_page > 0:
                self.screen.blit(self.img_prev_btn, self.prev_page_rect)
                prev_text = self.font_menu.render("<", True, (255, 255, 255))
                self.screen.blit(prev_text, prev_text.get_rect(center=self.prev_page_rect.center))

        pygame.display.update()

    def run(self):
        """Vòng lặp chính của màn hình intro."""
        while self.running:
            self._handle_input()
            self._draw_elements()
            self.clock.tick(30)

        return self.selected_mode, self.nickname, self.selected_save