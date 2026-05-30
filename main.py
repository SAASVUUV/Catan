import sys
import pygame
from core.scene_manager import SceneManager
from scenes.main_menu import MainMenu
from utils.sound import SoundManager
import settings
 
 
def run():
    pygame.init()
    pygame.mixer.init()
    SoundManager()  # Pré-carrega os sons e carrega configurações salvas
    SoundManager().play_music('soundtrack', loops=-1)
    if settings.FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()
 
    manager = SceneManager()
    manager.push(MainMenu(manager))
 
    running = True
    while running and manager.stack:
        dt = clock.tick(settings.FPS) / 1000.0
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.current.handle_event(event)
    
        manager.current.update(dt)
        manager.current.render(screen)
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    run()