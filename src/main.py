import sys
import os

import pygame

from board import Board
from scrolling_background import ScrollingBackground
from utils import resource_path

# Game states
START_SCREEN = 0
PLAYING = 1
END_SCREEN = 2

INITIAL_WIDTH = 720
INITIAL_HEIGHT = 480
BOARD_WIDTH = 14  # 改為 14
BOARD_HEIGHT = 7  # 改為 7
# Margin for better appearance - increased to prevent line clipping
MARGIN_X = 80
MARGIN_Y = 80
# Initial tile size (will be recalculated when window resizes)
TILE_WIDTH = (INITIAL_WIDTH - 2 * MARGIN_X) // BOARD_WIDTH
TILE_HEIGHT = (INITIAL_HEIGHT - 2 * MARGIN_Y) // BOARD_HEIGHT
BACKGROUND_COLOR = (40, 40, 40)

def main():
    pygame.init()
    
    # Initialize background music
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(resource_path(os.path.join("assets", "audio", "background_music.mp3")))
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
        pygame.mixer.music.play(-1)  # -1 means infinite loop
    except pygame.error:
        print("Could not load background music")
    
    screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mahjong Link Game")
    
    current_width, current_height = INITIAL_WIDTH, INITIAL_HEIGHT
    game_state = START_SCREEN
    
    # Initialize scrolling background
    scrolling_bg = ScrollingBackground(current_width, current_height)
    
    # Start screen button
    start_button = pygame.Rect(0, 0, 120, 40)
    start_button.center = (current_width // 2, current_height // 2 + 60)
    
    def calculate_tile_size():
        """Calculate tile size based on current window size with aspect ratio preservation"""
        available_width = current_width - 2 * MARGIN_X
        available_height = current_height - 2 * MARGIN_Y
        
        # Calculate tile size based on available space
        tile_width = available_width // BOARD_WIDTH
        tile_height = available_height // BOARD_HEIGHT
        
        # Maintain reasonable aspect ratio (not too wide or too tall)
        # Target aspect ratio is roughly 3:4 (width:height)
        target_ratio = 3 / 4
        
        # More strict aspect ratio control for fullscreen
        if tile_width / tile_height > target_ratio * 1.2:  # Too wide - reduced from 1.5 to 1.2
            tile_width = int(tile_height * target_ratio * 1.2)
        elif tile_height / tile_width > (1 / target_ratio) * 1.2:  # Too tall - reduced from 1.5 to 1.2
            tile_height = int(tile_width * (1 / target_ratio) * 1.2)
        
        # Ensure minimum size
        tile_width = max(tile_width, 20)
        tile_height = max(tile_height, 25)
        
        return tile_width, tile_height
    
    def calculate_font_size(base_size, min_size=12, max_size=72):
        """Calculate dynamic font size based on window size"""
        # 根據視窗大小計算字體大小
        scale_factor = min(current_width / INITIAL_WIDTH, current_height / INITIAL_HEIGHT)
        font_size = int(base_size * scale_factor)
        return max(min_size, min(font_size, max_size))
    
    def calculate_board_position():
        tile_width, tile_height = calculate_tile_size()
        board_pixel_width = BOARD_WIDTH * tile_width
        board_pixel_height = BOARD_HEIGHT * tile_height
        offset_x = (current_width - board_pixel_width) // 2
        offset_y = (current_height - board_pixel_height) // 2
        return offset_x, offset_y, tile_width, tile_height
    
    offset_x, offset_y, tile_width, tile_height = calculate_board_position()
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
                offset_x, offset_y, tile_width, tile_height = calculate_board_position()
                if board:
                    board.update_position_and_size(offset_x, offset_y, tile_width, tile_height)
                scrolling_bg = ScrollingBackground(current_width, current_height)
                start_button.center = (current_width // 2, current_height // 2 + 60)
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
            
            # Calculate dynamic font sizes
            title_font_size = calculate_font_size(48, 24, 96)
            button_font_size = calculate_font_size(24, 16, 48)
            
            # Draw title with shadow effect
            try:
                # Try multiple Chinese fonts
                font_title = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", title_font_size)  # Microsoft YaHei
            except (IOError, OSError):
                try:
                    font_title = pygame.font.Font("C:/Windows/Fonts/simsun.ttc", title_font_size)  # SimSun
                except (IOError, OSError):
                    try:
                        font_title = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", title_font_size)  # macOS
                    except (IOError, OSError):
                        font_title = pygame.font.Font(None, title_font_size)  # Fallback to default
                
            # Draw shadow
            text_shadow = font_title.render("麻將連連看", True, (50, 30, 0))
            shadow_rect = text_shadow.get_rect(
                center=(current_width // 2 + 2, current_height // 2 - 60 + 2)
            )
            screen.blit(text_shadow, shadow_rect)
            
            # Draw main text
            text_title = font_title.render("麻將連連看", True, (255, 215, 0))
            title_rect = text_title.get_rect(
                center=(current_width // 2, current_height // 2 - 60)
            )
            screen.blit(text_title, title_rect)
            
            # Update button size based on font size
            button_width = max(120, int(button_font_size * 5))
            button_height = max(40, int(button_font_size * 1.8))
            start_button.width = button_width
            start_button.height = button_height
            start_button.center = (current_width // 2, current_height // 2 + 60)
            
            # Draw start button
            pygame.draw.rect(screen, (0, 100, 0), start_button)
            pygame.draw.rect(screen, (0, 200, 0), start_button, 3)
            
            try:
                # Try multiple Chinese fonts
                font_button = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", button_font_size)  # Microsoft YaHei
            except (IOError, OSError):
                try:
                    font_button = pygame.font.Font("C:/Windows/Fonts/simsun.ttc", button_font_size)  # SimSun
                except (IOError, OSError):
                    try:
                        font_button = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", button_font_size)  # macOS
                    except (IOError, OSError):
                        font_button = pygame.font.Font(None, button_font_size)  # Fallback to default
                
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