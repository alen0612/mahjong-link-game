import pygame
import sys

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
TILE_SIZE = 80
BOARD_WIDTH = 12
BOARD_HEIGHT = 6
BACKGROUND_COLOR = (0, 0, 0)

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mahjong Link Game")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(BACKGROUND_COLOR)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()