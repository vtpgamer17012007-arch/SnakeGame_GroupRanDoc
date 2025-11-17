import pygame
import sys
from snake import settings as s
from snake.scenes.board import Board
from snake.scenes.intro import Intro



def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
    pygame.display.set_caption("Game Rắn Săn Mồi")

    current_scene_name = "INTRO"
    current_scene_obj = None
    nickname = ""

    while True:
        if current_scene_name == "INTRO":
            current_scene_obj = Intro(screen)
            mode, nickname, save_name = current_scene_obj.run()

            if mode == "PLAYER":
                current_scene_obj = Board(screen, nickname, initial_state=None, save_name=None)
                current_scene_name = "BOARD"

            elif mode == "LOAD":
                game_state = save_manager.load_game(save_name)
                if game_state:
                    current_scene_obj = Board(
                        screen,
                        game_state["nickname"],
                        initial_state=game_state,
                        save_name=save_name
                    )
                    current_scene_name = "BOARD"
                else:
                    print(f"Lỗi: Không thể tải file {save_name}")
                    current_scene_name = "INTRO"

            elif mode == "AI":
                print(f"Chế độ AI được chọn bởi {nickname}. Chưa được lập trình!")
                current_scene_name = "INTRO"

            elif mode == "QUIT":
                break

        elif current_scene_name == "BOARD":
            next_scene = current_scene_obj.run()

            if next_scene == "INTRO":
                current_scene_name = "INTRO"
            else:
                break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

