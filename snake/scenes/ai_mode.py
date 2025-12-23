import pygame
import torch
import numpy as np
from pathlib import Path
from snake import settings as s
from snake.core.env_snake import SnakeEnv
from snake.core.snake_render import SnakeRenderer
from snake.rl.agent_dqn import DQNAgent
from snake.core.sound_manager import SoundManager

FONT_PATH = Path(__file__).parent.parent / "assets/fonts"
ASSETS_PATH = Path(__file__).parent.parent / "assets"

class AIMode:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        
        self.env = SnakeEnv()
        self.agent = DQNAgent() 
        self.renderer = SnakeRenderer(screen)

        self.sound_manager = SoundManager()
        self.sound_manager.play_music("game")


        model_path = Path(__file__).parent.parent.parent / "models/model_ep5000.pth"
        
        try:
            self.agent.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.agent.model.eval()
            print("Đã nạp bộ não AI thành công!")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file model tại {model_path}")
        
        # Tắt tính ngẫu nhiên để AI chơi thông minh nhất
        self.agent.epsilon = -1 
        

    def _handle_ai_input(self):
        state = self.env.get_state_rl() 
        
        # AI chọn action (0, 1, 2, hoặc 3)
        action_idx = self.agent.get_action(state, False)
        

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        move = directions[action_idx]
        
        # Chặn quay đầu 180 độ 
        current_dir = self.env.direction
        if (move[0] + current_dir[0] == 0) and (move[1] + current_dir[1] == 0):
            move = current_dir
            
        self.env.direction = move

        


    def _update_game(self):
        self._handle_ai_input() 
        old_score = self.env.score
        state, reward, done, info = self.env.step(self.env.direction)
        if self.env.score > old_score: 
            self.sound_manager.play_sfx("eat")
        elif self.env.score < old_score and not done:
            self.sound_manager.play_sfx("poop")
        if done:
            self.sound_manager.play_sfx("die")
            pygame.time.delay(500) 
            self.env.reset()
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: 
                        self.sound_manager.play_sfx("click")
                        self.running = False

            self._update_game()
            self.renderer.draw(self.env) 
            
            pygame.display.update()
            self.clock.tick(60)
        return "INTRO"