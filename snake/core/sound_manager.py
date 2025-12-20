import pygame
from pathlib import Path

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        self.SOUND_PATH = Path(__file__).parent.parent / "assets/sounds"
        
        if self.initialized:
            return
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
            except Exception as e:
                print(f"SoundManager Init Error: {e}")
        
        self.sounds = {}
        self.music_playing = None
        
        # Mặc định volume 50
        self.vol_sfx = 50   
        self.vol_music = 50 

        self.SOUND_PATH = Path(__file__).parent.parent/ "assets/sounds"
        
        # Load Sound Effects
        self._load_sound("click", "click.wav")
        self._load_sound("die", "die.wav")
        self._load_sound("win", "win.wav")
        self._load_sound("eat", "eat.mp3")
        self._load_sound("poop", "poop.wav")
        self._load_sound("input", "input.ogg")
        
        # Load Nhạc nền
        self.music_files = {
            "menu": self.SOUND_PATH / "menu_music.mp3",
            "game": self.SOUND_PATH / "in_game.mp3",
            "battle": self.SOUND_PATH/ "battle.mp3"
        }
        
        self.apply_volume()
        self.initialized = True

    def _load_sound(self, name, filename):
        try:
            path = self.SOUND_PATH / filename
            if path.exists():
                self.sounds[name] = pygame.mixer.Sound(str(path))
            else:
                print(f"Warning: File {filename} not found!")
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    def apply_volume(self):
        # Pygame volume chạy từ 0.0 đến 1.0
        pygame.mixer.music.set_volume(self.vol_music / 100.0)
        for sound in self.sounds.values():
            sound.set_volume(self.vol_sfx / 100.0)

    def update_sfx_volume(self, amount):
        self.vol_sfx += amount
        self.vol_sfx = max(0, min(100, self.vol_sfx))
        self.apply_volume()

    def update_music_volume(self, amount):
        self.vol_music += amount
        self.vol_music = max(0, min(100, self.vol_music))
        self.apply_volume()

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()
    def stop_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].stop()
    def play_music(self, name, loop=-1):
        if self.music_playing == name and pygame.mixer.music.get_busy(): return
        
        if name in self.music_files and self.music_files[name].exists():
            try:
                pygame.mixer.music.load(str(self.music_files[name]))
                pygame.mixer.music.play(loop)
                self.music_playing = name
                self.apply_volume()
            except Exception as e:
                print(f"Error playing music {name}: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = None