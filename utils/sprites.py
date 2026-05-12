import os
import pygame
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT, DESERT, GENERIC

class SpriteLoader:
    _instance = None

    # Dicionário exclusivo para as imagens de Terrenos Hexagonais
    TERRAINS = {
        ROCK:    "ore.png",
        TREE:    "forest.png",
        LAMB:    "field.png",
        BRICK:   "clay.png",
        WHEAT:   "wheat.png",
        DESERT:  "desert.png"
    }

    # Dicionário exclusivo para as imagens de Portos Marítimos
    PORTS = {
        GENERIC: "harbour_any.png",
        ROCK:    "harbour_ore.png",
        TREE:    "harbour_forest.png",
        LAMB:    "harbour_field.png",
        BRICK:   "harbour_clay.png",
        WHEAT:   "harbour_wheat.png"
    }

    # Dicionário geral para estruturas, peças e interface

    UI_PIECES = {
        "settlement": "settlement.png",
        "city": "city.png",
        "road": "vertical.png",
        "bandit": "bandit.png",
        "full_border": "full_border.png"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpriteLoader, cls).__new__(cls)
            cls._instance._cache = {}
            cls._instance._base_dir = cls._instance._find_assets_dir()
        return cls._instance

    def _find_assets_dir(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        catan_dir = os.path.dirname(current_dir)
        return os.path.join(catan_dir, "assets", "images")

    def get_terrain_sprite(self, terrain_type, target_size=None):
        """Busca estritamente a textura hexagonal do terreno."""
        filename = self.TERRAINS.get(terrain_type)
        if not filename:
            return self._get_fallback_surface(target_size, (100, 100, 100))
        return self._load_and_scale(filename, target_size)

    def get_port_sprite(self, port_type, target_size=None):
        """Busca estritamente a textura da doca portuária."""
        filename = self.PORTS.get(port_type)
        if not filename:
            return self._get_fallback_surface(target_size, (50, 150, 200))
        return self._load_and_scale(filename, target_size)

    def get_sprite(self, key, target_size=None):
        """Busca arquivos genéricos pelo nome exato (ex: '8.png') ou peças mapeadas."""
        cache_key = (key, target_size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        filename = self.UI_PIECES.get(key, key)
        return self._load_and_scale(filename, target_size, cache_key)

    def _load_and_scale(self, filename, target_size, cache_key=None):
        if not cache_key:
            cache_key = (filename, target_size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        filepath = os.path.join(self._base_dir, filename)
        surface = None
        if os.path.exists(filepath):
            try:
                surface = pygame.image.load(filepath).convert_alpha()
            except pygame.error:
                pass

        if surface is None:
            surface = self._get_fallback_surface(target_size, (80, 80, 80))

        if target_size and surface.get_size() != target_size:
            surface = pygame.transform.smoothscale(surface, target_size)

        self._cache[cache_key] = surface
        return surface

    def _get_fallback_surface(self, target_size, color):
        w, h = target_size if target_size else (64, 64)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((*color, 80))
        return s

    def get_tinted_sprite(self, key, color, target_size=None):
        base = self.get_sprite(key, target_size).copy()
        tint = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        tint.fill((*color[:3], 255))
        base.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return base