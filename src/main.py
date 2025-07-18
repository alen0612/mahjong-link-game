import pygame
import sys
from board import Board

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
    
    board_pixel_width = BOARD_WIDTH * TILE_SIZE
    board_pixel_height = BOARD_HEIGHT * TILE_SIZE
    offset_x = (WINDOW_WIDTH - board_pixel_width) // 2
    offset_y = (WINDOW_HEIGHT - board_pixel_height) // 2
    
    board = Board(BOARD_WIDTH, BOARD_HEIGHT, TILE_SIZE, offset_x, offset_y)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.handle_click(event.pos)
        
        screen.fill(BACKGROUND_COLOR)
        board.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()