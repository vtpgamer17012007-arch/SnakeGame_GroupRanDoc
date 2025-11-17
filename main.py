import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from snake.app import SnakeApp

if __name__ == "__main__":
    app = SnakeApp()
    app.run()