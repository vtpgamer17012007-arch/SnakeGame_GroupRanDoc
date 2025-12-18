import random
import pygame
import numpy as np
from snake import settings as s

class SnakeEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        start_x = s.START_COL + (s.GRID_WIDTH // 2)
        start_y = s.START_ROW + (s.GRID_HEIGHT // 2)
        
        self.snake_pos = [(start_x, start_y)]
        self.direction = (0, -1)
        self.food_pos = None
        self.poops = []
        self.score = 0
        self.game_over = False
        self._spawn_food()
        self._spawn_poop()
        return self.get_state()

    def _spawn_food(self):
        while True:
            self.food_pos = (
                random.randint(s.START_COL, s.END_COL - 1),
                random.randint(s.START_ROW, s.END_ROW - 1)
            )   
            if self.food_pos not in self.snake_pos:
                break
    
    def _spawn_poop(self):
        while True:
            pos = (
                random.randint(s.START_COL, s.END_COL - 1),
                random.randint(s.START_ROW, s.END_ROW - 1)
            )
            existing_poops = [p['pos'] for p in self.poops]
            if (pos not in self.snake_pos and 
                pos != self.food_pos and 
                pos not in existing_poops):
                self.poops.append({'pos': pos, 'age': 0})
                break

    def step(self, action_direction):
        if self.game_over:
            return self.get_state(), 0, True, {}

        self.direction = action_direction
        head_x, head_y = self.snake_pos[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # 1. Kiểm tra va chạm tường/thân (Giữ nguyên)
        if (new_head in self.snake_pos or
            new_head[0] < s.START_COL or new_head[0] >= s.END_COL or
            new_head[1] < s.START_ROW or new_head[1] >= s.END_ROW):
            self.game_over = True
            return self.get_state(), -10, True, {}

        # Lưu lại chiều dài HIỆN TẠI trước khi thêm đầu mới
        current_length = len(self.snake_pos)
        self.snake_pos.insert(0, new_head) # Thêm đầu mới vào
        reward = 0

        # 2. Logic ăn mồi (Giữ nguyên: không pop để dài ra)
        if new_head == self.food_pos:
            self.score += 1
            reward = 10
            self._spawn_food()

        # 3. Logic dẫm phải "poop" (Thay đổi tại đây)
        elif any(p['pos'] == new_head for p in self.poops):
            if current_length == 1:
                # TRƯỜNG HỢP 1: Chỉ có duy nhất cái đầu -> CHẾT
                self.game_over = True
                reward = -10
            else:
                # TRƯỜNG HỢP 2: Có thân -> RÚT NGẮN THÂN
                # Xóa poop đã ăn
                for i, p in enumerate(self.poops):
                    if p['pos'] == new_head:
                        self.poops.pop(i)
                        break
                
                # Logic rút ngắn: 
                # pop lần 1: để bù lại phần đầu vừa thêm (giữ nguyên chiều dài)
                # pop lần 2: để thực sự làm con rắn ngắn đi 1 đốt
                self.snake_pos.pop() 
                if len(self.snake_pos) > 1: # Đảm bảo không pop mất cái đầu duy nhất
                    self.snake_pos.pop()
                
                self.score = max(0, self.score - 1)
                reward = -5 # Phạt vừa phải để AI biết đường né
                self._spawn_poop()

        # 4. Di chuyển bình thường
        else:
            self.snake_pos.pop() # Xóa đuôi để duy trì chiều dài
            reward = -0.1

        return self.get_state(), reward, self.game_over, {}
    

    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snake_pos[0]
        # Kiểm tra đâm tường dựa trên cấu hình settings.py
        if pt[0] < s.START_COL or pt[0] >= s.END_COL or \
        pt[1] < s.START_ROW or pt[1] >= s.END_ROW:
            return True
        # Kiểm tra đâm vào thân rắn
        if pt in self.snake_pos[1:]:
            return True
        # MỚI: Kiểm tra va chạm với poop
        if any(p['pos'] == pt for p in self.poops):
            return True
        return False

 

    def get_state_rl(self):
        head = self.snake_pos[0]
        
        # Tạo các điểm giả định xung quanh đầu để kiểm tra va chạm
        point_l = (head[0] - 1, head[1])
        point_r = (head[0] + 1, head[1])
        point_u = (head[0], head[1] - 1)
        point_d = (head[0], head[1] + 1)
        
        # Kiểm tra hướng hiện tại
        dir_l = self.direction == (-1, 0)
        dir_r = self.direction == (1, 0)
        dir_u = self.direction == (0, -1)
        dir_d = self.direction == (0, 1)

        state = [
            # 1. Nguy hiểm phía trước
            (dir_r and self.is_collision(point_r)) or 
            (dir_l and self.is_collision(point_l)) or 
            (dir_u and self.is_collision(point_u)) or 
            (dir_d and self.is_collision(point_d)),

            # 2. Nguy hiểm bên phải (theo hướng đi)
            (dir_u and self.is_collision(point_r)) or 
            (dir_d and self.is_collision(point_l)) or 
            (dir_l and self.is_collision(point_u)) or 
            (dir_r and self.is_collision(point_d)),

            # 3. Nguy hiểm bên trái (theo hướng đi)
            (dir_d and self.is_collision(point_r)) or 
            (dir_u and self.is_collision(point_l)) or 
            (dir_r and self.is_collision(point_u)) or 
            (dir_l and self.is_collision(point_d)),
            
            # 4. Hướng di chuyển
            dir_l, dir_r, dir_u, dir_d,

            # 5. Vị trí mồi
            self.food_pos[0] < head[0], # Food left
            self.food_pos[0] > head[0], # Food right
            self.food_pos[1] < head[1], # Food up
            self.food_pos[1] > head[1]  # Food down
        ]

        return np.array(state, dtype=int)

    def get_state(self):
        return {
            "snake_pos": self.snake_pos,
            "direction": self.direction,
            "food_pos": self.food_pos,
            "poops": self.poops,
            "score": self.score,
            "game_over": self.game_over
        }
    
    def set_state(self, state_dict):
        self.snake_pos = [tuple(pos) for pos in state_dict["snake_pos"]]
        self.direction = tuple(state_dict["direction"])
        self.food_pos = tuple(state_dict["food_pos"])
        self.poops = state_dict.get("poops", [])
        self.score = state_dict["score"]
        self.game_over = False
