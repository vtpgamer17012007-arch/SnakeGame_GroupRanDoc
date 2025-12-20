import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
import random
from snake.rl.dqn_model import Linear_QNet
from snake.rl.memory import ReplayMemory
class DQNAgent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # Tham số kiểm soát tính khám phá
        self.gamma = 0.9 # Hệ số chiết khấu (Discount factor)
        self.memory = ReplayMemory(100_000)
        self.model = Linear_QNet(16, 256, 4)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss() # Hàm tính sai số

        
    def get_action(self, state, training=True): # Thêm tham số training
        # Chiến thuật Epsilon-Greedy: Răng càng chơi nhiều càng bớt đi lung tung
        if training:
            self.epsilon = max(10, 700 - self.n_games)
        else:
            self.epsilon = -1 # Khi xem kết quả, tắt hoàn toàn ngẫu nhiên
        final_move = 0
        if random.randint(0, 1000) < self.epsilon:
            final_move = random.randint(0, 3)
        else:
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            final_move = torch.argmax(prediction).item()
        return final_move
    # HÀM SỬA LỖI 1: Huấn luyện ngay lập tức sau mỗi bước đi
    def train_short_memory(self, state, action, reward, next_state, done):
        self.train_step(state, action, reward, next_state, done)

    # HÀM SỬA LỖI 2: Huấn luyện từ một nhóm ký ức ngẫu nhiên (Batch)
    def train_long_memory(self):
        if len(self.memory) > 1000:
            mini_batch = self.memory.sample(1000)
        else:
            mini_batch = list(self.memory.memory)

        states, actions, rewards, next_states, dones = zip(*mini_batch)
        self.train_step(states, actions, rewards, next_states, list(dones))

    def train_step(self, state, action, reward, next_state, done):
        # Chuyển dữ liệu sang Tensor để PyTorch tính toán
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        # Công thức Bellman: Q_new = Reward + gamma * max(next_Q)
        pred = self.model(state)
        target = pred.clone()
        
        Q_new = reward
        if not done:
            Q_new = reward + self.gamma * torch.max(self.model(next_state))
        
        # Cập nhật giá trị Q cho hành động đã thực hiện
        # Lưu ý: action ở đây là index (0-3)
        if state.ndimension() == 1: # Xử lý cho train_short_memory
             target[action] = Q_new
        else: # Xử lý cho train_long_memory (Batch)
             for idx in range(len(done)):
                 target[idx][action[idx]] = reward[idx]
                 if not done[idx]:
                     target[idx][action[idx]] = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward() # Lan truyền ngược
        self.optimizer.step()