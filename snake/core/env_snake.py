import random
from snake import settings as s

class SnakeEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake_pos = [(s.GRID_WIDTH // 2, s.GRID_HEIGHT // 2)]
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
                random.randint(0, s.GRID_WIDTH - 1),
                random.randint(0, s.GRID_HEIGHT - 1)
            )
            if self.food_pos not in self.snake_pos:
                break
    
    def _spawn_poop(self):
        while True:
            pos = (
                random.randint(0, s.GRID_WIDTH - 1),
                random.randint(0, s.GRID_HEIGHT - 1)
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

        if (new_head in self.snake_pos or
            new_head[0] < 0 or new_head[0] >= s.GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= s.GRID_HEIGHT):
            self.game_over = True
            return self.get_state(), -10, True, {}

        self.snake_pos.insert(0, new_head)
        reward = 0

        if new_head == self.food_pos:
            self.score += 1
            reward = 10
            self._spawn_food()
            for p in self.poops:
                p['age'] += 1
            self.poops = [p for p in self.poops if p['age'] < 5]
            self._spawn_poop()

        elif any(p['pos'] == new_head for p in self.poops):
            self.poops = [p for p in self.poops if p['pos'] != new_head]
            self.snake_pos.pop() 
            if len(self.snake_pos) > 1:
                self.snake_pos.pop()
            self.score = max(0, self.score - 2)
            reward = -5
            
        else:
            self.snake_pos.pop()
            reward = -0.1

        return self.get_state(), reward, self.game_over, {}

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