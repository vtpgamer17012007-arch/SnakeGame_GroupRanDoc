import random
from collections import deque

class ReplayMemory:
    def __init__(self, capacity):
        # deque sẽ tự động xóa phần tử cũ nhất khi đầy bộ nhớ
        self.memory = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        # Lưu một bộ "trải nghiệm" vào kho
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        # Bốc ngẫu nhiên một nhóm trải nghiệm để học
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)