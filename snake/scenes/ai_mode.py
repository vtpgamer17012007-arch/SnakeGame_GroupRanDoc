import pygame
import torch
import numpy as np
from pathlib import Path
from snake import settings as s
from snake.core.env_snake import SnakeEnv
from snake.core.snake_render import SnakeRenderer # Cần Renderer để vẽ
from snake.rl.agent_dqn import DQNAgent

FONT_PATH = Path(__file__).parent.parent / "assets/fonts"
ASSETS_PATH = Path(__file__).parent.parent / "assets"

class AIMode:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        
        self.env = SnakeEnv()
        self.agent = DQNAgent() 
        self.renderer = SnakeRenderer(screen) # Khởi tạo renderer

        # 1. Sửa đường dẫn nạp model chính xác
        # model_ep1000.pth hoặc best_model.pth tùy bạn đặt tên
        model_path = Path(__file__).parent.parent.parent / "models/model_ep5000.pth"
        
        try:
            # map_location giúp chạy được trên cả máy không có GPU
            self.agent.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.agent.model.eval()
            print("Đã nạp bộ não AI thành công!")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file model tại {model_path}")
        
        # 2. Quan trọng: Tắt tính ngẫu nhiên để AI chơi thông minh nhất
        self.agent.epsilon = -1 
        

    def _handle_ai_input(self):
        # 3. AI phải LẤY TRẠNG THÁI RL (11 chiều) trước khi chọn hướng
        state = self.env.get_state_rl() 
        
        # AI chọn action (0, 1, 2, hoặc 3)
        action_idx = self.agent.get_action(state, False)
        
        # Chuyển đổi action_idx sang vector hướng (phải khớp với lúc train)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] # Lên, Xuống, Trái, Phải
        move = directions[action_idx]
        
        # Chặn quay đầu 180 độ đột ngột gây chết oan
        current_dir = self.env.direction
        if (move[0] + current_dir[0] == 0) and (move[1] + current_dir[1] == 0):
            move = current_dir
            
        self.env.direction = move

        


    def _update_game(self):
        self._handle_ai_input() # Gọi hàm xử lý AI
        
        state, reward, done, info = self.env.step(self.env.direction)

        if done:
            pygame.time.delay(500) # Đợi một chút rồi chơi lại
            self.env.reset()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False

            self._update_game()
            
            # 4. Phải gọi hàm vẽ thì mới thấy con rắn di chuyển
            self.renderer.draw(self.env) 
            
            pygame.display.update()
            self.clock.tick(60)
        return "INTRO"