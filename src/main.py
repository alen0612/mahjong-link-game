import sys

import pygame

from board import Board
from scrolling_background import ScrollingBackground
from font_utils import get_chinese_font

# Game states
START_SCREEN = 0
PLAYING = 1
END_SCREEN = 2

INITIAL_WIDTH = 1200
INITIAL_HEIGHT = 800
INITIAL_TILE_WIDTH = 60
INITIAL_TILE_HEIGHT = 80  # 3:4 aspect ratio
BOARD_WIDTH = 14
BOARD_HEIGHT = 7
BACKGROUND_COLOR = (40, 40, 40)
MARGIN = 80  # Minimum margin around board

def main():
    pygame.init()
    
    # Initialize background music
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("assets/audio/background_music.mp3")
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # -1 means infinite loop
    except pygame.error:
        print("Could not load background music")
    
    screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mahjong Link Game")
    
    current_width, current_height = INITIAL_WIDTH, INITIAL_HEIGHT
    
    def calculate_tile_size():
        # Calculate tile size based on window size with margins
        available_width = current_width - 2 * MARGIN
        available_height = current_height - 2 * MARGIN
        
        # Calculate maximum tile size that fits
        tile_width_from_width = available_width // BOARD_WIDTH
        tile_height_from_width = int(tile_width_from_width * 4 / 3)  # Maintain 3:4 aspect ratio
        
        tile_height_from_height = available_height // BOARD_HEIGHT
        tile_width_from_height = int(tile_height_from_height * 3 / 4)  # Maintain 3:4 aspect ratio
        
        # Use the smaller size to ensure it fits
        if tile_width_from_width * BOARD_WIDTH <= available_width and tile_height_from_width * BOARD_HEIGHT <= available_height:
            tile_width = tile_width_from_width
            tile_height = tile_height_from_width
        else:
            tile_width = tile_width_from_height
            tile_height = tile_height_from_height
            
        # Apply minimum and maximum limits
        tile_width = max(30, min(tile_width, INITIAL_TILE_WIDTH * 2))  # Min 30, max 2x original
        tile_height = int(tile_width * 4 / 3)  # Maintain aspect ratio
        
        return tile_width, tile_height
    
    tile_width, tile_height = calculate_tile_size()
    board_pixel_width = BOARD_WIDTH * tile_width
    board_pixel_height = BOARD_HEIGHT * tile_height
    game_state = START_SCREEN
    
    # Initialize scrolling background
    scrolling_bg = ScrollingBackground(current_width, current_height)
    
    # Start screen button (scale with window)
    scale_factor = min(current_width / INITIAL_WIDTH, current_height / INITIAL_HEIGHT)
    button_width = int(200 * scale_factor)
    button_height = int(60 * scale_factor)
    start_button = pygame.Rect(0, 0, button_width, button_height)
    start_button.center = (current_width // 2, current_height // 2 + int(100 * scale_factor))
    
    def calculate_board_position(tile_w, tile_h):
        board_w = BOARD_WIDTH * tile_w
        board_h = BOARD_HEIGHT * tile_h
        offset_x = (current_width - board_w) // 2
        offset_y = (current_height - board_h) // 2
        return offset_x, offset_y
    
    offset_x, offset_y = calculate_board_position(tile_width, tile_height)
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
                
                # Recalculate tile size
                tile_width, tile_height = calculate_tile_size()
                board_pixel_width = BOARD_WIDTH * tile_width
                board_pixel_height = BOARD_HEIGHT * tile_height
                offset_x, offset_y = calculate_board_position(tile_width, tile_height)
                
                if board:
                    board.update_size_and_position(tile_width, tile_height, offset_x, offset_y)
                scrolling_bg = ScrollingBackground(current_width, current_height)
                
                # Update button size and position on resize
                scale_factor = min(current_width / INITIAL_WIDTH, current_height / INITIAL_HEIGHT)
                button_width = int(200 * scale_factor)
                button_height = int(60 * scale_factor)
                start_button.width = button_width
                start_button.height = button_height
                start_button.center = (current_width // 2, current_height // 2 + int(100 * scale_factor))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == START_SCREEN:
                    if start_button.collidepoint(event.pos):
                        game_state = PLAYING
                        board = Board(BOARD_WIDTH, BOARD_HEIGHT, tile_width, tile_height, offset_x, offset_y)
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
            # Scale font size based on window size
            title_font_size = int(96 * min(current_width / INITIAL_WIDTH, current_height / INITIAL_HEIGHT))
            title_font_size = max(title_font_size, 48)  # Minimum font size
            font_title = get_chinese_font(title_font_size)
                
            # Draw shadow
            text_shadow = font_title.render("麻將連連看", True, (50, 30, 0))
            shadow_rect = text_shadow.get_rect(
                center=(current_width // 2 + 3, current_height // 2 - 100 + 3)
            )
            screen.blit(text_shadow, shadow_rect)
            
            # Draw main text
            text_title = font_title.render("麻將連連看", True, (255, 215, 0))
            title_rect = text_title.get_rect(
                center=(current_width // 2, current_height // 2 - 100)
            )
            screen.blit(text_title, title_rect)
            
            # Draw start button
            pygame.draw.rect(screen, (0, 100, 0), start_button)
            pygame.draw.rect(screen, (0, 200, 0), start_button, 3)
            
            # Scale button font size
            button_font_size = int(36 * min(current_width / INITIAL_WIDTH, current_height / INITIAL_HEIGHT))
            button_font_size = max(button_font_size, 20)  # Minimum font size
            font_button = get_chinese_font(button_font_size)
                
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
    
    # Stop music before quitting
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()