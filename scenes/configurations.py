import pygame
import os
import math
import pygame
from .base_scene import BaseScene
import settings
from constants import colors as C
from components.selection_icons import PlayerSlot
from components import Slider, Label, Checkbox
from components.back_button import BackButton
from utils.sound import SoundManager

class Configurations(BaseScene):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT

        self._init()

    def _init(self):
        W = self.screen_width
        H = self.screen_height
        w0 = W * 0.1
        w1 = W * 0.5
        h0 = H * 0.1
        bar_w = W*0.45
        bar_h = 12
        gap_h = 120
        font_size = 80

        self.slider_master_sound_label = Label("Volume Master", w0, h0-bar_h*2, font_size)
        self.slider_master_sound = Slider(w1, h0, bar_w, bar_h)

        self.slider_music_sound_label = Label("Volume Música", w0, h0-bar_h*2 + gap_h, font_size)
        self.slider_music_sound = Slider(w1, h0 + gap_h, bar_w, bar_h)

        self.slider_sfx_sound_label = Label("Volume SFX", w0, h0-bar_h*2 + 2*gap_h, font_size)
        self.slider_sfx_sound = Slider(w1, h0 + 2 * gap_h, bar_w, bar_h)

        self._load_volume_settings()

        self.aracno_label = Label("Modo Aracnofobia", w0, h0 + 3 * gap_h, font_size)
        self.aracno_button = Checkbox(w1, h0 + 3 * gap_h + 10, 60)

        self.btn_back = BackButton(20, 20)
 
    def handle_event(self, event):
        self.slider_master_sound.handle_event(event)
        self.slider_music_sound.handle_event(event)
        self.slider_sfx_sound.handle_event(event)
        self.aracno_button.handle_event(event)
        if self.btn_back.handle_event(event):
            self._save_volume_settings()
            from scenes.main_menu import MainMenu
            self.manager.replace(MainMenu(self.manager))
 
    def update(self, dt):
        self.slider_master_sound.update()
        self.slider_music_sound.update()
        self.slider_sfx_sound.update()
        self._apply_volume_settings()
        self.aracno_button.update()
        self.btn_back.update()

    def render(self, surface):
        surface.fill(C.BACKGROUND)

        self.slider_master_sound_label.render(surface)
        self.slider_master_sound.render(surface)

        self.slider_music_sound_label.render(surface)
        self.slider_music_sound.render(surface)

        self.slider_sfx_sound_label.render(surface)
        self.slider_sfx_sound.render(surface)

        self.aracno_label.render(surface)
        self.aracno_button.render(surface)
        self.btn_back.render(surface)

    def _load_volume_settings(self):
        manager = SoundManager()
        self.slider_master_sound.set_value(manager.master_volume)
        self.slider_music_sound.set_value(manager.music_volume)
        self.slider_sfx_sound.set_value(manager.sfx_volume)

    def _apply_volume_settings(self):
        manager = SoundManager()
        manager.set_master_volume(self.slider_master_sound.get_value())
        manager.set_music_volume(self.slider_music_sound.get_value())
        manager.set_sfx_volume(self.slider_sfx_sound.get_value())

    def _save_volume_settings(self):
        self._apply_volume_settings()
        SoundManager().save_settings()
