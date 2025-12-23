import pygame
import sys
from snake import settings as s
from snake.scenes.ai_mode import AIMode
from snake.scenes.solo_leveling import SoloLeveling
from snake.scenes.intro import Intro
from snake.scenes.play_mode import PlayMode 
from snake.scenes.select_info import SelectInfo
from snake.scenes.rules import Rules
from snake import save_manager
from snake.scenes.play_together import PlayTogether
from snake.scenes.battle_royale import BattleRoyal
from snake.scenes.credit import Credit
from snake.scenes.continue_scene import ContinueScene
from snake.core.sound_manager import SoundManager
from snake.scenes.setting import SettingPopup

class SnakeApp:
    def __init__(self):
        try:
            pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=1024)
        except Exception as e:
            print(f"Lỗi cài đặt âm thanh: {e}")
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pygame.display.set_caption("Mấy con rắn độc")
        self.current_scene_name = "INTRO"
        self.current_scene_obj = None
        self.nickname_player1 = ""
        self.nickname_player2 = ""
        
        self.avatar_player1 = "avatar1" 
        self.avatar_player2 = "avatar2"
        
        self.selected_mode = None 
        self.rules = None
        self.difficulty = s.DIFFICULTY_NORMAL

    def run(self):
        while True:
            # ==========================================
            # 1. INTRO
            # ==========================================
            if self.current_scene_name == "INTRO":
                self.current_scene_obj = Intro(self.screen)
                mode, save_name = self.current_scene_obj.run() 

                if mode == "PLAY":
                    self.current_scene_name = "PLAY_MODE"
                    
                elif mode == "CONTINUE": 
                    self.current_scene_name = "CONTINUE_SCENE"
                    pygame.time.wait(200)
                    pygame.event.clear()
                    
                elif mode == "AI":
                    self.current_scene_name = "AI_MODE"
                elif mode == "CREDIT":
                    self.current_scene_name = "CREDIT"
                elif mode == "QUIT":
                    break
            
            # ==========================================
            # 2. CONTINUE (LOAD GAME)
            # ==========================================
            elif self.current_scene_name == "CONTINUE_SCENE":
                self.current_scene_obj = ContinueScene(self.screen)
                action, data = self.current_scene_obj.run() 

                if action == "BACK":
                    self.current_scene_name = "INTRO"
                    pygame.time.wait(150); pygame.event.clear()
                
                elif action == "LOAD_GAME" and data:
                    mode_id = data.get("mode")
                    
                    
                    if mode_id == "SOLO_LEVELING":
                        nick = data.get("nickname", "Player")
                        diff = data.get("difficulty", 10)
                        avt = data.get("avatar", "avatar1") 
                        self.current_scene_obj = SoloLeveling(self.screen, nick, avt, diff)
                        self.current_scene_obj.restore_game_state(data)
                        self.current_scene_name = "SOLO_LEVELING"

                    elif mode_id == "PLAY_TOGETHER":
                        n1 = data.get("name1", "P1")
                        n2 = data.get("name2", "P2")
                        avt1 = data.get("avatar1", "avatar1")
                        avt2 = data.get("avatar2", "avatar2")
                        
                        self.current_scene_obj = PlayTogether(self.screen, avt1, avt2, n1, n2)
                        self.current_scene_obj.restore_game_state(data)
                        self.current_scene_name = "PLAY_TOGETHER"

                    elif mode_id == "BATTLE_ROYALE":
                        n1 = data.get("name1", "P1")
                        n2 = data.get("name2", "P2")
                        avt1 = data.get("avatar1", "avatar1")
                        avt2 = data.get("avatar2", "avatar2")

                        self.current_scene_obj = BattleRoyal(self.screen, avt1, avt2, n1, n2)
                        self.current_scene_obj.restore_game_state(data)
                        self.current_scene_name = "BATTLE_ROYALE"
                    
                    pygame.time.wait(150)
                    pygame.event.clear()
            
            # ==========================================
            # 3. CHỌN MODE
            # ==========================================
            elif self.current_scene_name == "PLAY_MODE":
                self.current_scene_obj = PlayMode(self.screen)
                self.selected_mode = self.current_scene_obj.run() 

                if self.selected_mode in ["SOLO_LEVELING", "PLAY_TOGETHER", "BATTLE_ROYALE"]:
                    self.current_scene_name = "SELECT_INFO" 
                elif self.selected_mode == "QUIT":
                    self.current_scene_name = "INTRO" 
                else:
                    self.current_scene_name = "INTRO" 
            # ==========================================
            # 4. NHẬP INFO
            # ==========================================
            elif self.current_scene_name == "SELECT_INFO":
                self.current_scene_obj = SelectInfo(self.screen, self.selected_mode)
                self.selected_mode, self.nickname_player1, self.nickname_player2, self.avatar_player1, self.avatar_player2, self.difficulty = self.current_scene_obj.run()
                
                if self.selected_mode in ["SOLO_LEVELING", "PLAY_TOGETHER", "BATTLE_ROYALE"]:
                    self.current_scene_name = "RULES"
                elif self.selected_mode == "QUIT":
                     self.current_scene_name = "PLAY_MODE"
                else:
                    self.current_scene_name = "INTRO"

            # ==========================================
            # 4. RULES
            # ==========================================
            elif self.current_scene_name == "RULES":
                self.current_scene_obj = Rules(self.screen, self.selected_mode)
                rules_action = self.current_scene_obj.run()
                if rules_action == "QUIT":
                    self.current_scene_name = "SELECT_INFO" 
                else:
                    self.current_scene_obj = None 
                    
                    if self.selected_mode == "SOLO_LEVELING":
                        self.current_scene_name = "SOLO_LEVELING"
                    elif self.selected_mode == "PLAY_TOGETHER":
                        self.current_scene_name = "PLAY_TOGETHER"
                    elif self.selected_mode == "BATTLE_ROYALE":
                        self.current_scene_name = "BATTLE_ROYALE"

            # ==========================================
            # 5. IN GAME 
            # ==========================================
            elif self.current_scene_name == "SOLO_LEVELING":
                if not isinstance(self.current_scene_obj, SoloLeveling):
                    self.current_scene_obj = SoloLeveling(
                        self.screen, self.nickname_player1, self.avatar_player1, self.difficulty
                    )
                self.current_scene_name = result 
            elif self.current_scene_name == "PLAY_TOGETHER":
                if not isinstance(self.current_scene_obj, PlayTogether):
                    self.current_scene_obj = PlayTogether(
                        self.screen, self.avatar_player1, self.avatar_player2, self.nickname_player1, self.nickname_player2
                    )
                result = self.current_scene_obj.run()
                self.current_scene_name = result
            elif self.current_scene_name == "BATTLE_ROYALE":
                if not isinstance(self.current_scene_obj, BattleRoyal):
                    self.current_scene_obj = BattleRoyal(
                        self.screen, self.avatar_player1, self.avatar_player2, self.nickname_player1, self.nickname_player2
                    )
                result = self.current_scene_obj.run()
                self.current_scene_name = result          
            # ==========================================
            # 6. OTHER MODES
            # ==========================================
            elif self.current_scene_name == "AI_MODE":
                self.current_scene_obj = AIMode(self.screen)
                next_scene = self.current_scene_obj.run()
                self.current_scene_name = next_scene

            elif self.current_scene_name == "CREDIT":
                self.current_scene_obj = Credit(self.screen)
                next_scene = self.current_scene_obj.run()
                self.current_scene_name = next_scene
            
            else:
                self.current_scene_name = "INTRO"


        pygame.quit()
        sys.exit()