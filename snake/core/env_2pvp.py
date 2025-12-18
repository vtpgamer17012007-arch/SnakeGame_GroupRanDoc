import random
from snake import settings as s

class SnakeEnv2Pvp:
    def __init__(self):
        self.reset()

    def reset(self):
        mid_y = s.START_ROW + (s.GRID_HEIGHT // 2)
        # P1: Bên trái, hướng sang phải
        start_x1 = s.START_COL + 2
        self.p1_pos = [(start_x1, mid_y), (start_x1 - 1, mid_y)]
        self.p1_dir = (1, 0)
        self.p1_score = 0
        self.p1_alive = True

        # P2: Bên phải, hướng sang trái
        start_x2 = s.END_COL - 3
        self.p2_pos = [(start_x2, mid_y), (start_x2 + 1, mid_y)]
        self.p2_dir = (-1, 0)
        self.p2_score = 0
        self.p2_alive = True

        self.food_pos = None # Cho P1
        self.poop_pos = None # Cho P2
        self.game_over = False
        self.winner = None # 1, 2 hoặc "Draw"

        self._spawn_food()
        self._spawn_poop()
        return self.get_state()

    def _spawn_food(self):
        # Spawn táo (cho P1)
        while True:
            pos = (random.randint(s.START_COL, s.END_COL - 1), 
                random.randint(s.START_ROW, s.END_ROW - 1))
            obstacles = self.p1_pos + self.p2_pos
            if self.poop_pos: obstacles.append(self.poop_pos)
            
            if pos not in obstacles:
                self.food_pos = pos
                break

    def _spawn_poop(self):
        # Spawn shit (cho P2)
        while True:
            pos = (
                random.randint(s.START_COL, s.END_COL - 1), 
                random.randint(s.START_ROW, s.END_ROW - 1))
            obstacles = self.p1_pos + self.p2_pos
            if self.food_pos: obstacles.append(self.food_pos)

            if pos not in obstacles:
                self.poop_pos = pos
                break

    def step(self, dir1, dir2):
        if self.game_over: return self.get_state()

        # Update hướng
        if self.p1_alive and dir1: self.p1_dir = dir1
        if self.p2_alive and dir2: self.p2_dir = dir2

        # Di chuyển đầu
        if self.p1_alive:
            head1 = (self.p1_pos[0][0] + self.p1_dir[0], self.p1_pos[0][1] + self.p1_dir[1])
            self.p1_pos.insert(0, head1)
        
        if self.p2_alive:
            head2 = (self.p2_pos[0][0] + self.p2_dir[0], self.p2_pos[0][1] + self.p2_dir[1])
            self.p2_pos.insert(0, head2)

        # 1. Kiểm tra va chạm tường
        p1_hit_wall = self._check_wall(self.p1_pos[0]) if self.p1_alive else False
        p2_hit_wall = self._check_wall(self.p2_pos[0]) if self.p2_alive else False

        # 2. Kiểm tra va chạm thân (tự cắn hoặc cắn nhau)
        p1_body = self.p1_pos[1:] if self.p1_alive else []
        p2_body = self.p2_pos[1:] if self.p2_alive else []
        
        if self.p1_alive:
            h1 = self.p1_pos[0]
            if (h1 in p1_body) or (h1 in self.p2_pos): 
                p1_hit_wall = True 
        
        if self.p2_alive:
            h2 = self.p2_pos[0]
            if (h2 in p2_body) or (h2 in self.p1_pos): 
                p2_hit_wall = True

        # 3. Kiểm tra ăn uống (LOGIC MỚI Ở ĐÂY)
        if self.p1_alive and not p1_hit_wall:
            h1 = self.p1_pos[0]
            if h1 == self.food_pos: # P1 ăn Táo (Đúng)
                self.p1_score += 1
                self._spawn_food()
                # Không pop -> Dài ra
            elif h1 == self.poop_pos: # P1 ăn Shit (Sai)
                self.p1_score = max(0, self.p1_score - 2) # Trừ 2 điểm
                self._spawn_poop() # Tạo cục shit mới chỗ khác
                self.p1_pos.pop()  # Pop lần 1 (di chuyển bình thường)
                self.p1_pos.pop() 
                if len(self.p1_pos) < 1: 
                    p1_hit_wall = True
                    
            else:
                self.p1_pos.pop() # Đi bình thường

        if self.p2_alive and not p2_hit_wall:
            h2 = self.p2_pos[0]
            if h2 == self.food_pos: # P2 ăn Shit (Đúng)
                self.p2_score += 1
                self._spawn_food()
            elif h2 == self.poop_pos: # P2 ăn Táo (Sai)
                self.p2_score = max(0, self.p2_score - 2) # Trừ 2 điểm
                self._spawn_poop() # Tạo quả táo mới chỗ khác
                self.p2_pos.pop()
                self.p2_pos.pop() 
                if len(self.p2_pos) < 1:
                    p2_hit_wall = True
            else:
                self.p2_pos.pop()

        # Xử lý cái chết (chỉ chết nếu đâm tường hoặc đâm thân)
        if p1_hit_wall: self.p1_alive = False
        if p2_hit_wall: self.p2_alive = False

        if not self.p1_alive and not self.p2_alive:
            self.game_over = True
            self.winner = "Draw"
        elif not self.p1_alive or self.p2_score==50:
            self.game_over = True
            self.winner = "Player 2 Wins!"
        elif not self.p2_alive or self.p1_score==50:
            self.game_over = True
            self.winner = "Player 1 Wins!"

        return self.get_state()

    def _check_wall(self, head):
        x, y = head
        return x < s.START_COL or x >= s.END_COL or y < s.START_ROW or y >= s.END_ROW

    def get_state(self):
        return {
            "p1_pos": self.p1_pos, "p1_dir": self.p1_dir, "p1_score": self.p1_score, "p1_alive": self.p1_alive,
            "p2_pos": self.p2_pos, "p2_dir": self.p2_dir, "p2_score": self.p2_score, "p2_alive": self.p2_alive,
            "food_pos": self.food_pos, "poop_pos": self.poop_pos,
            "game_over": self.game_over, "winner": self.winner
        }