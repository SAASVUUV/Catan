import json
import pygame
import os


class SoundManager:
    """Gerenciador centralizado de efeitos sonoros do jogo."""
    
    _instance = None
    _sounds = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.master_volume = 1.0
        self.music_volume = 0.4
        self.sfx_volume = 1.0
        self._config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

        self._load_settings()
        self._load_sounds()
        self._apply_volumes()
    
    def _load_sounds(self):
        """Carrega todos os sons da pasta assets/sfx."""
        sfx_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sfx')
        
        sound_files = {
            'invalid_action': 'invalid_action.mp3',
            'construction': 'construction.mp3',
            'dice_roll': 'dice_roll.mp3',
            'button_press': 'button_press.mp3',
            'confirm_trade': 'confirm_trade.mp3',
            'draw_card': 'draw_card.mp3',
            'road': 'road.mp3',
        }
        self._music_files = {
            'soundtrack': os.path.join(sfx_dir, 'soundtrack.mp3')
        }
        
        for key, filename in sound_files.items():
            filepath = os.path.join(sfx_dir, filename)
            try:
                if os.path.exists(filepath):
                    self._sounds[key] = pygame.mixer.Sound(filepath)
                else:
                    print(f"Aviso: Arquivo de som não encontrado: {filepath}")
            except Exception as e:
                print(f"Erro ao carregar som '{key}': {e}")
    
    def play(self, sound_name: str):
        """Toca um efeito sonoro."""
        if sound_name in self._sounds:
            try:
                self._sounds[sound_name].play()
            except Exception as e:
                print(f"Erro ao tocar som '{sound_name}': {e}")
        else:
            print(f"Som '{sound_name}' não encontrado")

    def play_music(self, music_name: str, loops: int = -1, volume: float = None):
        """Toca música de fundo usando pygame.mixer.music."""
        if music_name not in self._music_files:
            print(f"Música '{music_name}' não encontrada")
            return
        filepath = self._music_files[music_name]
        try:
            pygame.mixer.music.load(filepath)
            if volume is None:
                volume = self.master_volume * self.music_volume
            else:
                volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops)
        except Exception as e:
            print(f"Erro ao tocar música '{music_name}': {e}")
    
    def stop(self, sound_name: str = None):
        """Para um som específico ou todos."""
        if sound_name and sound_name in self._sounds:
            self._sounds[sound_name].stop()
        elif sound_name is None:
            pygame.mixer.stop()
    
    def set_volume(self, sound_name: str, volume: float):
        """Define o volume de um som (0.0 a 1.0)."""
        if sound_name in self._sounds:
            self._sounds[sound_name].set_volume(max(0.0, min(1.0, volume)))

    def set_master_volume(self, volume: float):
        self.master_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._apply_volumes()

    def _apply_volumes(self):
        for sound in self._sounds.values():
            sound.set_volume(self.master_volume * self.sfx_volume)
        pygame.mixer.music.set_volume(self.master_volume * self.music_volume)

    def save_settings(self):
        try:
            config = {
                'master_volume': self.master_volume,
                'music_volume': self.music_volume,
                'sfx_volume': self.sfx_volume,
            }
            with open(self._config_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações de áudio: {e}")

    def _load_settings(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                self.master_volume = float(config.get('master_volume', self.master_volume))
                self.music_volume = float(config.get('music_volume', self.music_volume))
                self.sfx_volume = float(config.get('sfx_volume', self.sfx_volume))
            except Exception as e:
                print(f"Erro ao carregar configurações de áudio: {e}")
        else:
            self.save_settings()

    def stop_music(self):
        pygame.mixer.music.stop()
