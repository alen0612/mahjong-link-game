import pygame
import sys
from board import Board

INITIAL_WIDTH = 1200
INITIAL_HEIGHT = 800
TILE_WIDTH = 60
TILE_HEIGHT = 80  # 3:4 aspect ratio
BOARD_WIDTH = 12
BOARD_HEIGHT = 6
BACKGROUND_COLOR = (40, 40, 40)
MARGIN = 80

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mahjong Link Game")
    
    board_pixel_width = BOARD_WIDTH * TILE_WIDTH
    board_pixel_height = BOARD_HEIGHT * TILE_HEIGHT
    
    current_width, current_height = INITIAL_WIDTH, INITIAL_HEIGHT
    
    def calculate_board_position():
        offset_x = (current_width - board_pixel_width) // 2
        offset_y = (current_height - board_pixel_height) // 2
        return offset_x, offset_y
    
    offset_x, offset_y = calculate_board_position()
    board = Board(BOARD_WIDTH, BOARD_HEIGHT, TILE_WIDTH, TILE_HEIGHT, offset_x, offset_y)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                current_width, current_height = event.w, event.h
                screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                offset_x, offset_y = calculate_board_position()
                board.update_position(offset_x, offset_y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.handle_click(event.pos)
        
        board.update()
        
        screen.fill(BACKGROUND_COLOR)
        board.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()