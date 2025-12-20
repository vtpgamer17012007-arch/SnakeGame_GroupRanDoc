import pygame
import sys
from snake import settings as s
from snake.scenes.ai_mode import AIMode
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake.scenes.play_mode import PlayMode 
from snake.scenes.select_info import SelectInfo
from snake.scenes.rules import Rules
from snake.scenes.play_together import PlayTogether 
from snake.scenes.battle_royale import Battle
from snake.scenes.continue_scene import ContinueScene

class SnakeApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pygame.display.set_caption("Mấy con rắn độc")
        self.current_scene_name = "INTRO"
        self.current_scene_obj = None
        self.nickname_player1 = ""
        self.nickname_player2 = ""
        self.selected_mode = None
        self.rules = None
        self.difficulty = s.DIFFICULTY_NORMAL

    def run(self):
        while True:
            # -----------------------------------------------------------
            # 1. INTRO
            # -----------------------------------------------------------
            if self.current_scene_name == "INTRO":
                self.current_scene_obj = Intro(self.screen)
                mode, _ = self.current_scene_obj.run()

                if mode == "PLAY":
                    self.current_scene_name = "PLAY_MODE"
                    pygame.time.wait(150)
                    pygame.event.clear()
                
                # --- SỬA ĐOẠN NÀY ---
                elif mode == "CONTINUE": 
                    self.current_scene_name = "CONTINUE_SCENE" # Chuyển sang scene mới
                    pygame.time.wait(200)  # Chờ 0.2s để tránh bị click đúp
                    pygame.event.clear()

                elif mode == "AI":
                    self.current_scene_name = "AI_MODE"
                elif mode == "QUIT":
                    break
            
            # -----------------------------------------------------------
            # 2. KHỐI XỬ LÝ CONTINUE SCENE (MỚI)
            # -----------------------------------------------------------
            # Đảm bảo đoạn này nằm ngang hàng (cùng lề) với if self.current_scene_name == "INTRO"
            elif self.current_scene_name == "CONTINUE_SCENE":
                self.current_scene_obj = ContinueScene(self.screen)
                action, data = self.current_scene_obj.run()

                if action == "BACK":
                    self.current_scene_name = "INTRO"
                    pygame.time.wait(150)
                    pygame.event.clear()
                
                elif action == "LOAD_GAME" and data:
                    # --- GIẢI PHÁP CHỐNG XUNG ĐỘT DỮ LIỆU ---
                    
                    # 1. Đọc "Hộ chiếu" (Mode ID) từ file save
                    mode_to_load = data.get("mode") 
                    
                    print(f"Loading data for mode: {mode_to_load}") # Debug xem đang load cái gì

                    # 2. Phân luồng khởi tạo (Router)
                    # App tự động chuyển scene dựa trên dữ liệu, không quan tâm người dùng đang chọn tab nào
                    
                    # === TRƯỜNG HỢP 1: SOLO LEVELING ===
                    if mode_to_load == "SOLO_LEVELING":
                        # Lấy thông tin cần thiết để khởi tạo class
                        self.nickname_player1 = data.get("nickname", "Player")
                        self.difficulty = data.get("difficulty", s.BASE_SPEED)
                        
                        # Khởi tạo đúng Class Solo
                        self.current_scene_obj = SoloLeveling(self.screen, self.nickname_player1, self.difficulty)
                        # Đổ dữ liệu vào
                        self.current_scene_obj.restore_game_state(data)
                        # Chuyển scene
                        self.current_scene_name = "SOLO_LEVELING"

                    # === TRƯỜNG HỢP 2: PLAY TOGETHER ===
                    elif mode_to_load == "PLAY_TOGETHER":
                        name1 = data.get("name1", "Player 1")
                        name2 = data.get("name2", "Player 2")
                        
                        # Khởi tạo đúng Class PlayTogether
                        self.current_scene_obj = PlayTogether(self.screen, name1, name2)
                        # Đổ dữ liệu vào (Code hàm restore ở bước trước)
                        self.current_scene_obj.restore_game_state(data)
                        # Chuyển scene
                        self.current_scene_name = "PLAY_TOGETHER"

                    # === TRƯỜNG HỢP 3: BATTLE ROYALE ===
                    elif mode_to_load == "BATTLE_ROYALE":
                        name1 = data.get("name1", "Player 1")
                        name2 = data.get("name2", "Player 2")
                        
                        # Khởi tạo đúng Class Battle
                        self.current_scene_obj = Battle(self.screen, name1, name2)
                        # Đổ dữ liệu vào (Code hàm restore ở bước trước)
                        self.current_scene_obj.restore_game_state(data)
                        # Chuyển scene
                        self.current_scene_name = "BATTLE_ROYALE"
                    
                    else:
                        print(f"Lỗi: File save không hợp lệ hoặc thiếu mode id: {mode_to_load}")
                    
                    # Chờ một chút để tránh click đúp
                    pygame.time.wait(150)
                    pygame.event.clear()
            # -----------------------------------------------------------
            # 3. PLAY MODE
            # -----------------------------------------------------------
            elif self.current_scene_name == "PLAY_MODE":
                # Xóa sự kiện cũ trước khi vào scene mới để tránh click nhầm
                pygame.event.clear()
                
                self.current_scene_obj = PlayMode(self.screen)
                self.selected_mode = self.current_scene_obj.run()

                if self.selected_mode == "BACK":
                    self.current_scene_name = "INTRO"
                    # Thêm độ trễ nhỏ để ngắt thao tác click chuột của người chơi
                    pygame.time.wait(150)
                    pygame.event.clear()
                    
                # Chỉ chuyển sang SELECT_INFO nếu giá trị trả về đúng là tên các mode
                elif self.selected_mode in ["SOLO_LEVELING", "PLAY_TOGETHER", "BATTLE_ROYALE"]:
                    self.current_scene_name = "SELECT_INFO"
                    pygame.time.wait(150) # Tránh click dính sang màn hình chọn tên
                    pygame.event.clear()

            # -----------------------------------------------------------
            # 4. SELECT INFO
            # -----------------------------------------------------------
            elif self.current_scene_name == "SELECT_INFO":
                self.current_scene_obj = SelectInfo(self.screen, self.selected_mode)
                status, p1, p2, diff_str = self.current_scene_obj.run() 

                if status == "QUIT" or status == "BACK":
                     self.current_scene_name = "PLAY_MODE"
                     pygame.time.wait(150) # Thêm độ trễ chống click dính
                     pygame.event.clear()
                else:
                    self.nickname_player1 = p1
                    self.nickname_player2 = p2
                    
                    final_difficulty = 10 
                    if hasattr(s, str(diff_str)):
                        val = getattr(s, str(diff_str))
                        try: final_difficulty = int(val)
                        except ValueError: pass
                    elif str(diff_str).isdigit():
                        final_difficulty = int(diff_str)
                    
                    self.difficulty = final_difficulty
                    self.current_scene_name = "RULES"

            # -----------------------------------------------------------
            # 5. RULES
            # -----------------------------------------------------------
            elif self.current_scene_name == "RULES":
                self.rules = Rules(self.screen, self.selected_mode)
                action = self.rules.run()
                
                if action == "BACK" or action == "QUIT":
                    self.current_scene_name = "SELECT_INFO" 
                else:
                    if self.selected_mode == "SOLO_LEVELING":
                        self.current_scene_name = "SOLO_LEVELING"
                    elif self.selected_mode == "PLAY_TOGETHER":
                        self.current_scene_name = "PLAY_TOGETHER"
                    elif self.selected_mode == "BATTLE_ROYALE":
                        self.current_scene_name = "BATTLE_ROYALE"
                    else:
                        self.current_scene_name = "INTRO"

            # -----------------------------------------------------------
            # 6. GAME LOOP CHÍNH
            # -----------------------------------------------------------
            elif self.current_scene_name == "AI_MODE":
                self.current_scene_obj = AIMode(self.screen)
                next_scene = self.current_scene_obj.run()
                self.current_scene_name = next_scene

            elif self.current_scene_name == "SOLO_LEVELING":
                # Kiểm tra để tránh reset game liên tục mỗi frame
                if not isinstance(self.current_scene_obj, SoloLeveling):
                    self.current_scene_obj = SoloLeveling(self.screen, self.nickname_player1, self.difficulty)
                
                next_scene = self.current_scene_obj.run() 
                self.current_scene_name = next_scene

            elif self.current_scene_name == "PLAY_TOGETHER":
                if not isinstance(self.current_scene_obj, PlayTogether):
                    self.current_scene_obj = PlayTogether(self.screen, self.nickname_player1, self.nickname_player2)
                
                next_scene = self.current_scene_obj.run()
                self.current_scene_name = next_scene

            elif self.current_scene_name == "BATTLE_ROYALE":
                if not isinstance(self.current_scene_obj, Battle):
                    self.current_scene_obj = Battle(self.screen, self.nickname_player1, self.nickname_player2)
                
                next_scene = self.current_scene_obj.run()
                self.current_scene_name = next_scene
            
            self.clock = pygame.time.Clock()
            self.clock.tick(60)
        sys.exit()