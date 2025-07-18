import pygame
import sys
from board import Board
from scrolling_background import ScrollingBackground

# Game states
START_SCREEN = 0
PLAYING = 1
END_SCREEN = 2

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
    game_state = START_SCREEN
    
    # Initialize scrolling background
    scrolling_bg = ScrollingBackground(current_width, current_height)
    
    # Start screen button
    start_button = pygame.Rect(0, 0, 200, 60)
    start_button.center = (current_width // 2, current_height // 2 + 100)
    
    def calculate_board_position():
        offset_x = (current_width - board_pixel_width) // 2
        offset_y = (current_height - board_pixel_height) // 2
        return offset_x, offset_y
    
    offset_x, offset_y = calculate_board_position()
    board = None
    
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
                if board:
                    board.update_position(offset_x, offset_y)
                scrolling_bg = ScrollingBackground(current_width, current_height)
                start_button.center = (current_width // 2, current_height // 2 + 100)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == START_SCREEN:
                    if start_button.collidepoint(event.pos):
                        game_state = PLAYING
                        board = Board(BOARD_WIDTH, BOARD_HEIGHT, TILE_WIDTH, TILE_HEIGHT, offset_x, offset_y)
                elif game_state == PLAYING:
                    if board:
                        board.handle_click(event.pos)
                        # Check if game is completed
                        if board.game_completed:
                            game_state = END_SCREEN
                elif game_state == END_SCREEN:
                    if board:
                        board.handle_click(event.pos)
        
        # Update
        if game_state == START_SCREEN:
            scrolling_bg.update()
        elif game_state == PLAYING and board:
            board.update()
            if board.game_completed:
                game_state = END_SCREEN
        elif game_state == END_SCREEN and board:
            board.update()
        
        # Draw
        screen.fill(BACKGROUND_COLOR)
        
        if game_state == START_SCREEN:
            # Draw scrolling background
            scrolling_bg.draw(screen)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Draw title with shadow effect
            try:
                font_title = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", 96)
            except:
                font_title = pygame.font.Font(None, 96)
                
            # Draw shadow
            text_shadow = font_title.render("麻將連連看", True, (50, 30, 0))
            shadow_rect = text_shadow.get_rect(center=(current_width // 2 + 3, current_height // 2 - 100 + 3))
            screen.blit(text_shadow, shadow_rect)
            
            # Draw main text
            text_title = font_title.render("麻將連連看", True, (255, 215, 0))
            title_rect = text_title.get_rect(center=(current_width // 2, current_height // 2 - 100))
            screen.blit(text_title, title_rect)
            
            # Draw start button
            pygame.draw.rect(screen, (0, 100, 0), start_button)
            pygame.draw.rect(screen, (0, 200, 0), start_button, 3)
            
            try:
                font_button = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", 36)
            except:
                font_button = pygame.font.Font(None, 36)
                
            text_start = font_button.render("開始遊戲", True, (255, 255, 255))
            text_rect = text_start.get_rect(center=start_button.center)
            screen.blit(text_start, text_rect)
            
        elif game_state == PLAYING and board:
            board.draw(screen)
            
        elif game_state == END_SCREEN and board:
            board.draw(screen)
            # End screen is handled in board.draw()
            
            # If player clicks play again, the board will restart itself
            # Check if game restarted
            if not board.game_completed:
                game_state = PLAYING
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()