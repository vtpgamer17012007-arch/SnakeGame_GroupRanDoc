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
        
        self.difficulty = s.DIFFICULTY_EASY
        

        self.SAVES_PER_PAGE = 5
        self.current_page = 0

        self._define_layout()
        self._load_assets()

    def _load_assets(self):
        try:
            self.img_background = pygame.image.load(ASSETS_PATH / "intro_background.png").convert_alpha()
            self.img_play_button = pygame.image.load(ASSETS_PATH / "play_button.png").convert_alpha()
            self.img_continue_button = pygame.image.load(ASSETS_PATH / "continue_button.png").convert_alpha()
            self.img_ai_button = pygame.image.load(ASSETS_PATH / "ai_button.png").convert_alpha()
            self.img_credit_button = pygame.image.load(ASSETS_PATH / "credit_button.png").convert_alpha()
            

            panel = pygame.image.load(ASSETS_PATH / "grey_panel.png").convert_alpha()
            green = pygame.image.load(ASSETS_PATH / "green_button00.png").convert_alpha()
            blue = pygame.image.load(ASSETS_PATH / "blue_button00.png").convert_alpha()
            red = pygame.image.load(ASSETS_PATH / "red_button00.png").convert_alpha()

            
            

            self.img_diff_selected = pygame.transform.scale(green, (90, 40))
            self.img_diff_unselected = pygame.transform.scale(blue, (90, 40))
            self.img_input_bg = pygame.transform.scale(panel, self.input_rect.size)
            self.img_back_btn = pygame.transform.scale(red, self.back_button_rect.size)
            self.img_save_slot = pygame.transform.scale(panel, (400, 50))
            self.img_next_btn = pygame.transform.scale(blue, self.next_page_rect.size)
            self.img_prev_btn = pygame.transform.scale(blue, self.prev_page_rect.size)
        except FileNotFoundError:
            print("Lỗi load ảnh Intro")
            sys.exit()

    def _define_layout(self):
        cx, cy = s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2
        # Tính toán vị trí để căn giữa 3 nút nhỏ
        

        self.input_rect = pygame.Rect(cx - 150, cy - 50, 300, 40)
        
        self.play_button_rect = pygame.Rect(157, 319, 277, 70)
        self.continue_button_rect = pygame.Rect(224, 406, 277, 70)
        self.ai_button_rect = pygame.Rect(157, 492, 277, 70)
        self.credit_button_rect = pygame.Rect(224, 578, 277, 70)


        
        #self.ai_button_rect = pygame.Rect(cx - 150, cy + 90, 300, 50)
        self.load_button_rect = pygame.Rect(cx - 150, cy + 160, 300, 50)


        self.back_button_rect = pygame.Rect(20, s.SCREEN_HEIGHT - 60, 100, 40)
        self.next_page_rect = pygame.Rect(s.SCREEN_WIDTH - 60, cy - 25, 50, 50)
        self.prev_page_rect = pygame.Rect(10, cy - 25, 50, 50)      

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
                
                
                if clicked:
                    self.input_active = self.input_rect.collidepoint(event.pos)
                    
                    if self.play_button_rect.collidepoint(event.pos):
                            self.selected_mode = "PLAY"; self.running = False
                    if self.ai_button_rect.collidepoint(event.pos):
                            self.selected_mode = "AI"; self.running = False
                    if self.continue_button_rect.collidepoint(event.pos):
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

    def HoverEffect(self, img, rect):
            if rect.collidepoint(pygame.mouse.get_pos()):
                w, h = int(rect.width * 1.05), int(rect.height * 1.05)
                scaled = pygame.transform.scale(img, (w, h))
                self.screen.blit(scaled, scaled.get_rect(center=rect.center))
            else:
                self.screen.blit(img, rect)

    

    def Hover(self, img, rect):
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(img,(0,0))

    def _draw_elements(self):
        self.screen.blit(self.img_background, (0, 0))
       

        if not self.showing_load_menu:

            self.Hover(self.img_play_button, self.play_button_rect)
            self.Hover(self.img_continue_button, self.continue_button_rect)
            self.Hover(self.img_ai_button, self.ai_button_rect) 
            self.Hover(self.img_credit_button, self.credit_button_rect)
            

        else:
            start = self.current_page * self.SAVES_PER_PAGE
            for i, rect in enumerate(self.save_rects):
                self.HoverEffect(self.img_save_slot, rect)
                name = self.save_list[start+i]
                t = self.font_input.render(name, True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=rect.center))

            self.HoverEffect(self.img_back_btn, self.back_button_rect)
            t = self.font_button.render("Back", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=self.back_button_rect.center))
            
            total = (len(self.save_list) + self.SAVES_PER_PAGE - 1) // self.SAVES_PER_PAGE
            if self.current_page < total - 1:
                self.HoverEffect(self.img_next_btn, self.next_page_rect)
                t = self.font_menu.render(">", True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=self.next_page_rect.center))
            if self.current_page > 0:
                self.HoverEffect(self.img_prev_btn, self.prev_page_rect)
                t = self.font_menu.render("<", True, (255, 255, 255))
                self.screen.blit(t, t.get_rect(center=self.prev_page_rect.center))

        

    def run(self):
        while self.running:
            self._handle_input()
            self._draw_elements()
            pygame.display.flip()
            self.clock.tick(s.FPS)
        return self.selected_mode, self.selected_save
