# =====================================================
# CẤU HÌNH GAME SNAKE
# =====================================================

# Kích thước màn hình
GRID_SIZE = 20  # Kích thước một ô lưới (pixel)
GRID_WIDTH = 30  # Số ô ngang
GRID_HEIGHT = 25  # Số ô dọc

SCREEN_WIDTH = 1280 # 600 pixel
SCREEN_HEIGHT = 720  # 500 pixel

PLAY_AREA_LEFT = 70    
PLAY_AREA_TOP = 150     
PLAY_AREA_WIDTH = 1150  
PLAY_AREA_HEIGHT = 540

START_COL = PLAY_AREA_LEFT // GRID_SIZE   # Ví dụ: 100 // 20 = 5 (Cột thứ 5)
START_ROW = PLAY_AREA_TOP // GRID_SIZE    # Ví dụ: 150 // 20 = 7 (Hàng thứ 7)

# Tính số lượng ô trong vùng chơi
GRID_WIDTH = PLAY_AREA_WIDTH // GRID_SIZE
GRID_HEIGHT = PLAY_AREA_HEIGHT // GRID_SIZE

# Tính giới hạn dưới và phải (để check va chạm)
END_COL = START_COL + GRID_WIDTH
END_ROW = START_ROW + GRID_HEIGHT
# =====================================================
# CẤU HÌNH MÀU SẮC (giá trị RGB)
# =====================================================
COLOR_BACKGROUND = (0, 0, 0)  # Đen - nền game
COLOR_FOOD = (255, 0, 0)  # Đỏ - thức ăn
COLOR_GRID = (40, 40, 40)  # Xám tối - đường lưới
COLOR_TEXT = (255, 255, 255)  # Trắng - text

# =====================================================
# CẤU HÌNH AVATAR NGƯỜI CHƠI
# =====================================================
# Thêm vào cuối file settings.py
AVATAR_LIST = ["avatar1", "avatar2", "avatar3", "avatar4", "avatar5"]

# =====================================================
# CẤU HÌNH TRẠNG THÁI GAME
# =====================================================
# Tốc độ game (FPS)
BASE_SPEED = 8  # Tốc độ mặc định (8 frame mỗi bước rắn)
MAX_SPEED = 20  # Tốc độ tối đa
MIN_SPEED = 2  # Tốc độ tối thiểu

FPS = 60  # Khung hình trên giây
# Độ khó
DIFFICULTY_EASY = 10
DIFFICULTY_NORMAL = 12
DIFFICULTY_HARD = 18

# =====================================================
# CẤU HÌNH LƯUTRÒ CHƠI
# =====================================================
SAVE_DIR = "saves"  # Thư mục lưu trò chơi
SAVE_FILE_EXTENSION = ".json"  # Định dạng file lưu

# =====================================================
# CẤU HÌNH AI/DQN (nếu sử dụng)
# =====================================================
# Các giá trị này sử dụng cho agent DQN
LEARNING_RATE = 0.001
GAMMA = 0.99  # Discount factor
EPSILON = 1.0  # Exploration rate
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
BATCH_SIZE = 32
MEMORY_SIZE = 10000

# =====================================================
# CẤU HÌNH 2 PLAYER
# =====================================================
import pygame

# Player 1: Mũi tên (Arrows) - Rắn Xanh (Ăn Táo)
P2_CONTROLS = {
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT
}

# Player 2: WASD - Rắn Vàng/Nâu (Ăn Shit)
P1_CONTROLS = {
    "UP": pygame.K_w,
    "DOWN": pygame.K_s,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d
}