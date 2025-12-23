import pygame
import torch
import numpy as np
import sys
import os
import json
from snake.core.env_snake import SnakeEnv
from snake.core.snake_render import SnakeRenderer
from snake.rl.agent_dqn import DQNAgent
from snake.rl.train_graph import plot
from snake import settings as s

def train():
    pygame.init()
    screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
    pygame.display.set_caption("AI Training Mode - Group Ran Doc")
    clock = pygame.time.Clock()

    # 2. Khởi tạo các thành phần logic
    env = SnakeEnv()
    agent = DQNAgent()
    renderer = SnakeRenderer(screen) 

    # Các biến theo dõi tiến trình
    plot_scores = []
    plot_mean_scores = []
    total_score = 0

    # 1. Tải trạng thái cũ từ JSON
    n_games_old, record_old = load_stats()
    
    # 2. Cập nhật cho Agent để tính Epsilon chính xác
    # Công thức: epsilon = 700 - n_games
    agent.n_games = n_games_old 
    record = record_old
    # 3. Tải mô hình cũ nếu có
    agent.model.load('model.pth')
    
    # Biến điều khiển hiển thị (Bật để xem AI chơi, tắt để train siêu tốc)
    VISUALIZE = True

    print("--- Bắt đầu huấn luyện Rắn Độc ---")

    while True:
        # Kiểm tra sự kiện thoát cửa sổ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # A. QUY TRÌNH TƯƠNG TÁC (RL LOOP)
        
        # 1. Nhìn: Lấy trạng thái 16 chiều
        state_old = env.get_state_rl()

        # 2. Quyết định: Agent chọn hành động (0-3)
        action_idx = agent.get_action(state_old, True)

        # 3. Hành động: Chuyển đổi index sang vector di chuyển
        # Tháp hướng: 0: Lên, 1: Xuống, 2: Trái, 3: Phải
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        move = directions[action_idx]
        current_dir = env.direction
       
        if (move[0] + current_dir[0] == 0) and (move[1] + current_dir[1] == 0):
            move = current_dir # Nếu AI ra lệnh quay đầu, bắt nó tiếp tục đi thẳng

        # 4. Phản hồi: Thực hiện bước đi và nhận thưởng
        # Reward: +20 ăn mồi, -10 ăn phân, -150 đâm tường/thân, -0.3 xa mồi, +0.3 gần mồi
        _, reward, done, _ = env.step(move)
        state_new = env.get_state_rl()

        # 5. Học ngắn: Huấn luyện ngay lập tức sau bước đi
        agent.train_short_memory(state_old, action_idx, reward, state_new, done)

        # 6. Ghi nhớ: Lưu vào Replay Memory
        agent.memory.push(state_old, action_idx, reward, state_new, done)

        # B. HIỂN THỊ ĐỒ HỌA
        if VISUALIZE:
            renderer.draw(env) 
            pygame.display.update()
            clock.tick(60) 

        # C. XỬ LÝ KHI KẾT THÚC MỘT TRẬN (EPISODE)
        if done:
            final_score = env.score      # 1. Lưu điểm trận vừa xong trước khi reset
            env.reset()                  # 2. Reset môi trường
            agent.n_games += 1           # 3. Tăng số trận
            
            # Học sâu từ bộ nhớ (Long memory)
            agent.train_long_memory()    #

            # LƯU MODEL TỐT NHẤT (BEST MODEL)
            if final_score > record:     #
                record = final_score
                agent.model.save(file_name='best_model.pth')

            # LƯU CHECKPOINT MỖI 100 TRẬN ---
            if agent.n_games % 100 == 0: 
                agent.model.save(episode=agent.n_games) 

            save_stats(agent.n_games, record)
            # Cập nhật đồ thị huấn luyện
            plot_scores.append(final_score)
            total_score += final_score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores) 

            print(f'Trận: {agent.n_games} | Điểm: {final_score} | Kỷ lục: {record} | Epsilon: {agent.epsilon:.2f}')

def save_stats(n_games, record):
    """Lưu số trận và kỷ lục vào file JSON."""
    stats = {
        "n_games": n_games,
        "record": record
    }
    with open("stats.json", "w") as f:
        json.dump(stats, f)
   

def load_stats():
    """Tải số trận và kỷ lục từ file JSON nếu tồn tại."""
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f:
            stats = json.load(f)
            return stats.get("n_games", 0), stats.get("record", 0)
    return 0, 0 
if __name__ == '__main__':
    train()