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
# TÙY CHỈNH MÀU RẮN
# =====================================================
# Danh sách các màu rắn có sẵn
SNAKE_COLORS = {
    "green": (0, 255, 0),       # Xanh lá (mặc định)
    "red": (255, 0, 0),         # Đỏ
    "blue": (0, 0, 255),        # Xanh dương
    "yellow": (255, 255, 0),    # Vàng
    "cyan": (0, 255, 255),      # Xanh ngọc
    "magenta": (255, 0, 255),   # Tím
    "orange": (255, 165, 0),    # Cam
    "white": (255, 255, 255),   # Trắng
}

# Màu rắn được chọn (thay đổi giá trị này để đổi màu)
SELECTED_SNAKE_COLOR = "green"
COLOR_SNAKE = SNAKE_COLORS[SELECTED_SNAKE_COLOR]

# =====================================================
# PHONG CẢNH BUTTON MENU (Themes)
# =====================================================
# Theme bao gồm: normal, hover, pressed, text
BUTTON_THEMES = {
    "light": {
        "normal": (200, 200, 200),    # Xám sáng
        "hover": (230, 230, 230),     # Xám nhạt hơn
        "pressed": (150, 150, 150),   # Xám đậm
        "text": (0, 0, 0),            # Chữ đen
    },
    "dark": {
        "normal": (50, 50, 50),       # Xám tối
        "hover": (80, 80, 80),        # Xám sáng hơn
        "pressed": (30, 30, 30),      # Xám rất tối
        "text": (255, 255, 255),      # Chữ trắng
    },
    "neon": {
        "normal": (0, 255, 255),      # Xanh ngọc
        "hover": (0, 200, 255),       # Xanh ngọc sáng
        "pressed": (0, 150, 200),     # Xanh ngọc đậm
        "text": (0, 0, 0),            # Chữ đen
    },
    "fire": {
        "normal": (255, 100, 0),      # Cam đỏ
        "hover": (255, 150, 0),       # Cam sáng
        "pressed": (200, 50, 0),      # Cam tối
        "text": (255, 255, 255),      # Chữ trắng
    },
    "purple": {
        "normal": (138, 43, 226),     # Tím xanh
        "hover": (160, 80, 240),      # Tím sáng
        "pressed": (100, 20, 200),    # Tím tối
        "text": (255, 255, 255),      # Chữ trắng
    },
}

# Theme được chọn (thay đổi giá trị này để đổi phong cách button)
SELECTED_BUTTON_THEME = "dark"
CURRENT_BUTTON_THEME = BUTTON_THEMES[SELECTED_BUTTON_THEME]

COLOR_BUTTON_NORMAL = CURRENT_BUTTON_THEME["normal"]
COLOR_BUTTON_HOVER = CURRENT_BUTTON_THEME["hover"]
COLOR_BUTTON_PRESSED = CURRENT_BUTTON_THEME["pressed"]
COLOR_BUTTON_TEXT = CURRENT_BUTTON_THEME["text"]

# =====================================================
# CẤU HÌNH TRẠNG THÁI GAME
# =====================================================
# Tốc độ game (FPS)
BASE_SPEED = 8  # Tốc độ mặc định (8 frame mỗi bước rắn)
MAX_SPEED = 20  # Tốc độ tối đa
MIN_SPEED = 2  # Tốc độ tối thiểu

FPS = 60  # Khung hình trên giây
# Độ khó
DIFFICULTY_EASY = 8
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