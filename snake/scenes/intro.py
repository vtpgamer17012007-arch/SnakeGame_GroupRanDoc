import pygame
import sys
from snake import settings as s
from snake import save_manager
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
        self._load_assets()

    def _define_layout(self):
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        self.input_rect = pygame.Rect(cx - 150, cy - 50, 300, 40)
        self.play_button_rect = pygame.Rect(cx - 150, cy + 20, 300, 50)
        self.ai_button_rect = pygame.Rect(cx - 150, cy + 90, 300, 50)
        self.load_button_rect = pygame.Rect(cx - 150, cy + 160, 300, 50)
        self.back_button_rect = pygame.Rect(20, s.SCREEN_HEIGHT - 60, 100, 40)
        self.next_page_rect = pygame.Rect(s.SCREEN_WIDTH - 60, cy - 25, 50, 50)
        self.prev_page_rect = pygame.Rect(10, cy - 25, 50, 50)

    def _load_assets(self):
        try:
            panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()
            green = pygame.image.load(ASSETS_PATH / "green_button00.png").convert_alpha()
            blue = pygame.image.load(ASSETS_PATH / "blue_button00.png").convert_alpha()
            red = pygame.image.load(ASSETS_PATH / "red_button00.png").convert_alpha()

            self.img_input_bg = pygame.transform.scale(panel, self.input_rect.size)
            self.img_play_btn = pygame.transform.scale(green, self.play_button_rect.size)
            self.img_ai_btn = pygame.transform.scale(green, self.ai_button_rect.size)
            self.img_load_btn = pygame.transform.scale(blue, self.load_button_rect.size)
            self.img_back_btn = pygame.transform.scale(red, self.back_button_rect.size)
            self.img_save_slot = pygame.transform.scale(panel, (400, 50))
            self.img_next_btn = pygame.transform.scale(blue, self.next_page_rect.size)
            self.img_prev_btn = pygame.transform.scale(blue, self.prev_page_rect.size)
        except FileNotFoundError:
            print("Lỗi load ảnh Intro")
            sys.exit()

    def _build_current_page(self):
        self.save_rects = []
        start = self.current_page * self.SAVES_PER_PAGE
        end = start + self.SAVES_PER_PAGE
        for i in range(len(self.save_list[start:end])):
            self.save_rects.append(pygame.Rect(s.SCREEN_WIDTH//2 - 200, 150 + i*60, 400, 50))

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected_mode = "QUIT"
            
            clicked = (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

            if not self.showing_load_menu:
                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE: self.nickname = self.nickname[:-1]
                        elif len(self.nickname) < 15: self.nickname += event.unicode
                
                if clicked:
                    self.input_active = self.input_rect.collidepoint(event.pos)
                    if self.nickname:
                        if self.play_button_rect.collidepoint(event.pos):
                            self.selected_mode = "PLAYER"; self.running = False
                        if self.ai_button_rect.collidepoint(event.pos):
                            self.selected_mode = "AI"; self.running = False
                    if self.load_button_rect.collidepoint(event.pos):
                        self.showing_load_menu = True
                        self.save_list = save_manager.get_save_list()
                        self.current_page = 0
                        self._build_current_page()
            else:
                if clicked:
                    if self.back_button_rect.collidepoint(event.pos): self.showing_load_menu = False
                    
                    total_pages = (len(self.save_list) + self.SAVES_PER_PAGE - 1) // self.SAVES_PER_PAGE
                    if self.next_page_rect.collidepoint(event.pos) and self.current_page < total_pages - 1:
                        self.current_page += 1; self._build_current_page()
                    if self.prev_page_rect.collidepoint(event.pos) and self.current_page > 0:
                        self.current_page -= 1; self._build_current_page()
                    
                    for i, rect in enumerate(self.save_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_mode = "LOAD"
                            idx = self.current_page * self.SAVES_PER_PAGE + i
                            self.selected_save = self.save_list[idx]
                            self.running = False

    def _draw_btn(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            w, h = int(rect.width * 1.05), int(rect.height * 1.05)
            scaled = pygame.transform.scale(img, (w, h))
            self.screen.blit(scaled, scaled.get_rect(center=rect.center))
        else:
            self.screen.blit(img, rect)

    def _draw_elements(self):
        self.screen.fill(s.COLOR_BACKGROUND)
        title = self.font_title.render("Snake Game", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(s.SCREEN_WIDTH//2, 80)))

        if not self.showing_load_menu:
            self.screen.blit(self.img_input_bg, self.input_rect)
            txt = self.font_input.render(self.nickname, True, (255, 255, 255))
            self.screen.blit(txt, (self.input_rect.x+15, self.input_rect.y+5))
            if not self.nickname and not self.input_active:
                ph = self.font_input.render("Enter Nickname...", True, (150, 150, 150))
                self.screen.blit(ph, (self.input_rect.x+15, self.input_rect.y+5))

            self._draw_btn(self.img_play_btn, self.play_button_rect)
            t = self.font_menu.render("Player Play", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.play_button_rect.center))

            self._draw_btn(self.img_ai_btn, self.ai_button_rect)
            t = self.font_menu.render("AI Play", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.ai_button_rect.center))

            self._draw_btn(self.img_load_btn, self.load_button_rect)
            t = self.font_menu.render("Load Game", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.load_button_rect.center))
        else:
            start = self.current_page * self.SAVES_PER_PAGE
            for i, rect in enumerate(self.save_rects):
                self._draw_btn(self.img_save_slot, rect)
                name = self.save_list[start+i]
                t = self.font_input.render(name, True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=rect.center))

            self._draw_btn(self.img_back_btn, self.back_button_rect)
            t = self.font_button.render("Back", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.back_button_rect.center))
            
            total = (len(self.save_list) + self.SAVES_PER_PAGE - 1) // self.SAVES_PER_PAGE
            if self.current_page < total - 1:
                self._draw_btn(self.img_next_btn, self.next_page_rect)
                t = self.font_menu.render(">", True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=self.next_page_rect.center))
            if self.current_page > 0:
                self._draw_btn(self.img_prev_btn, self.prev_page_rect)
                t = self.font_menu.render("<", True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=self.prev_page_rect.center))

        pygame.display.update()

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            self.clock.tick(30)
        return self.selected_mode, self.nickname, self.selected_save