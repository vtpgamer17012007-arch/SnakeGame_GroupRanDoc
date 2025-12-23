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
        old_dist = abs(self.snake_pos[0][0] - self.food_pos[0]) + \
               abs(self.snake_pos[0][1] - self.food_pos[1])
        self.direction = action_direction
        head_x, head_y = self.snake_pos[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # 1. Kiểm tra va chạm tường/thân (Giữ nguyên)
        if (new_head in self.snake_pos or
            new_head[0] < s.START_COL or new_head[0] >= s.END_COL or
            new_head[1] < s.START_ROW or new_head[1] >= s.END_ROW):
            self.game_over = True
            return self.get_state(), -150, True, {}

        current_length = len(self.snake_pos)
        self.snake_pos.insert(0, new_head) 
        reward = 0

        # 2. Logic ăn mồi (Giữ nguyên: không pop để dài ra)
        if new_head == self.food_pos:
            self.score += 1
            reward = 20
            self._spawn_food()

        # 3. Logic dẫm phải "poop" (Thay đổi tại đây)
        elif any(p['pos'] == new_head for p in self.poops):
            if current_length == 1:
                self.game_over = True
                reward = -100
            else:
                for i, p in enumerate(self.poops):
                    if p['pos'] == new_head:
                        self.poops.pop(i)
                        break
                
                self.snake_pos.pop() 
                if len(self.snake_pos) > 1: 
                    self.snake_pos.pop()        
                self.score = max(0, self.score - 1)
                reward = -10 
                self._spawn_poop()
        
        else:
            self.snake_pos.pop()
            new_dist = abs(new_head[0] - self.food_pos[0]) + \
                   abs(new_head[1] - self.food_pos[1])
        
            if new_dist < old_dist:
                reward = 0.3  # Thưởng vì tiến lại gần mồi (giúp đi thẳng)
            else:
                reward = -0.3 # Phạt vì đi xa mồi hoặc đi zizac thừa

        return self.get_state(), reward, self.game_over, {}
    

    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snake_pos[0]
        if pt[0] < s.START_COL or pt[0] >= s.END_COL or \
        pt[1] < s.START_ROW or pt[1] >= s.END_ROW:
            return True
        if pt in self.snake_pos[1:]:
            return True
        if any(p['pos'] == pt for p in self.poops):
            return True
        return False

 

    def get_state_rl(self):
        head = self.snake_pos[0]
        
        # Hàm phụ để quét theo một hướng bất kỳ cho đến khi chạm vật cản
        def ray_cast(direction):
            dist = 0
            # Tính toán ô tiếp theo dựa trên hướng quét
            current = (head[0] + direction[0], head[1] + direction[1])
            
            # Tiếp tục quét nếu ô hiện tại nằm trong bảng và không đâm vào thân mình
            while (s.START_COL <= current[0] < s.END_COL and 
                   s.START_ROW <= current[1] < s.END_ROW and 
                   current not in self.snake_pos):
                dist += 1
                current = (current[0] + direction[0], current[1] + direction[1])
            
            # Trả về giá trị chuẩn hóa: 1/(khoảng cách + 1)
            # Giá trị gần 1 nghĩa là vật cản rất gần, gần 0 là vật cản rất xa
            return 1.0 / (dist + 1)
    
        # 1. Tầm nhìn 8 hướng (8 chiều)
        # Bao gồm: Lên, Xuống, Trái, Phải và 4 hướng chéo
        look_dirs = [(0,-1), (0,1), (-1,0), (1,0), (-1,-1), (1,-1), (-1,1), (1,1)]
        vision = [ray_cast(d) for d in look_dirs]
    
        # 2. Vị trí mồi tương đối (4 chiều - Giữ nguyên logic cũ)
        food_dir = [
            self.food_pos[0] < head[0], # Thức ăn bên trái
            self.food_pos[0] > head[0], # Thức ăn bên phải
            self.food_pos[1] < head[1], # Thức ăn phía trên
            self.food_pos[1] > head[1]  # Thức ăn phía dưới
        ]
    
        # 3. Hướng di chuyển hiện tại (4 chiều - Giữ nguyên logic cũ)
        cur_dir = [
            self.direction == (-1, 0), # Đang đi trái
            self.direction == (1, 0),  # Đang đi phải
            self.direction == (0, -1), # Đang đi lên
            self.direction == (0, 1)   # Đang đi xuống
        ]
    
        # Tổng cộng: 8 (Tầm nhìn) + 4 (Mồi) + 4 (Hướng) = 16 chiều
        return np.array(vision + food_dir + cur_dir, dtype=float)

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
