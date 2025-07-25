import random
from collections import deque

import pygame

from particle import Firework
from tile import Tile
from font_utils import get_chinese_font

class Board:
    def __init__(self, width=14, height=7, tile_width=60, tile_height=80,
                 offset_x=0, offset_y=0):
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tiles = []
        self.selected_tiles = []
        self.animation_path = []
        self.animation_progress = 0
        self.animating = False
        self.tiles_to_remove = []
        self.failed_match_timer = 0
        self.failed_match_tiles = []
        
        
        self.game_completed = False
        self.fireworks = []
        self.firework_timer = 0
        self.play_again_button = pygame.Rect(0, 0, 200, 60)
        self.update_play_again_button_position()
        
        # Hint button
        self.hint_button = pygame.Rect(0, 0, 100, 40)
        self.update_hint_button_position()
        self.hint_timer = 0
        self.hint_tiles = []
        
        self.initialize_board()
        
    def initialize_board(self):
        self.tiles = self.generate_solvable_board()
        
    def generate_solvable_board(self):
        # Generate a board and ensure at least one pair can connect
        max_attempts = 10
        
        for attempt in range(max_attempts):
            tiles = self.generate_board()
            if self.has_valid_move(tiles):
                return tiles
        
        # If no valid board found, use last generated board
        # (very unlikely with many tiles)
        return tiles
        
    def generate_board(self):
        # We have 34 SVG files (0-33)
        # We need 98 tiles total (14×7)
        # Each type must appear an even number of times
        tile_types = []
        
        # Distribution: 15 types × 4 tiles + 19 types × 2 tiles = 98 tiles
        # Types 0-14: 4 tiles each (60 tiles)
        for i in range(15):
            tile_types.extend([i, i, i, i])
        
        # Types 15-33: 2 tiles each (38 tiles)
        for i in range(15, 34):
            tile_types.extend([i, i])
        
        # Shuffle the tiles
        random.shuffle(tile_types)
        
        # Create the board
        tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if tile_types:  # Check if we still have tiles to place
                    tile_type = tile_types.pop()
                    tile = Tile(x, y, tile_type, self.tile_width, self.tile_height,
                               self.offset_x, self.offset_y)
                    row.append(tile)
                else:
                    row.append(None)  # Empty cell if we run out of tiles
            tiles.append(row)
        
        return tiles
    
    def show_hint(self):
        # Find a valid pair that can connect
        import random
        
        # Clear any existing selections
        for tile in self.selected_tiles:
            tile.selected = False
        self.selected_tiles.clear()
        
        # Collect all possible pairs
        possible_pairs = []
        
        for y1 in range(self.height):
            for x1 in range(self.width):
                tile1 = self.tiles[y1][x1]
                if not tile1 or not tile1.visible:
                    continue
                
                for y2 in range(self.height):
                    for x2 in range(self.width):
                        if (x1, y1) == (x2, y2):
                            continue
                        tile2 = self.tiles[y2][x2]
                        if not tile2 or not tile2.visible:
                            continue
                        
                        if tile1.match(tile2):
                            path = self.can_connect(tile1, tile2)
                            if path:
                                possible_pairs.append((tile1, tile2))
        
        if possible_pairs:
            # Select a random pair
            tile1, tile2 = random.choice(possible_pairs)
            tile1.selected = True
            tile2.selected = True
            self.hint_tiles = [tile1, tile2]
            self.hint_timer = 60  # Show for 1 second at 60 FPS
    
    def shuffle_board(self):
        # Collect all visible tiles and their types
        visible_tiles = []
        tile_types = []
        
        for row in self.tiles:
            for tile in row:
                if tile and tile.visible:
                    visible_tiles.append(tile)
                    tile_types.append(tile.tile_type)
        
        if len(visible_tiles) < 2:
            return  # Not enough tiles to shuffle
        
        # Try shuffling until we get a board with at least one valid move
        max_shuffle_attempts = 50
        original_types = tile_types.copy()
        
        for attempt in range(max_shuffle_attempts):
            # Shuffle the tile types
            random.shuffle(tile_types)
            
            # Assign shuffled types back to tiles
            for i, tile in enumerate(visible_tiles):
                tile.tile_type = tile_types[i]
                tile.load_image()
            
            # Check if this configuration has at least one valid move
            if self.has_any_valid_move():
                print(f"Board shuffled successfully after {attempt + 1} attempts")
                return
        
        # If no valid configuration found after many attempts,
        # restore original (this is very unlikely)
        print("Warning: Could not find valid shuffle configuration")
        for i, tile in enumerate(visible_tiles):
            tile.tile_type = original_types[i]
            tile.load_image()
    
    def can_connect_test(self, x1, y1, x2, y2, visible_grid):
        if (x1, y1) == (x2, y2):
            return False
        
        from collections import deque
        queue = deque([((x1, y1), -1, -1)])
        visited = set()
        
        while queue:
            (x, y), prev_dir, turns = queue.popleft()
            
            if (x, y) == (x2, y2):
                return True
            
            if turns > 1:
                continue
            
            state = (x, y, prev_dir, turns)
            if state in visited:
                continue
            visited.add(state)
            
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            
            for i, (dx, dy) in enumerate(directions):
                nx, ny = x + dx, y + dy
                
                if nx < -1 or nx > self.width or ny < -1 or ny > self.height:
                    continue
                
                if (nx, ny) != (x2, y2):
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if visible_grid[ny][nx]:
                            continue
                
                new_turns = turns
                if prev_dir != -1 and prev_dir != i:
                    new_turns += 1
                
                if new_turns <= 1:
                    queue.append(((nx, ny), i, new_turns))
        
        return False
    
    def has_valid_move(self, test_tiles):
        # Check if there's at least one valid move
        for y1 in range(self.height):
            for x1 in range(self.width):
                tile1 = test_tiles[y1][x1] if test_tiles else self.tiles[y1][x1]
                if not tile1 or not tile1.visible:
                    continue
                    
                for y2 in range(self.height):
                    for x2 in range(self.width):
                        if (x1, y1) == (x2, y2):
                            continue
                        tile2 = test_tiles[y2][x2] if test_tiles else self.tiles[y2][x2]
                        if not tile2 or not tile2.visible:
                            continue
                            
                        if tile1.tile_type == tile2.tile_type:
                            if test_tiles:
                                # For initial board generation
                                visible_grid = [[True if t else False for t in row] for row in test_tiles]
                                if self.can_connect_test(x1, y1, x2, y2, visible_grid):
                                    return True
                            else:
                                # For current board state
                                if self.can_connect(tile1, tile2):
                                    return True
        return False
    
    def has_any_valid_move(self):
        # Check current board for any valid moves
        return self.has_valid_move(None)
    
    
    def update_position(self, new_offset_x, new_offset_y):
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.rect.x = tile.x * self.tile_width + self.offset_x
                    tile.rect.y = tile.y * self.tile_height + self.offset_y
        self.update_play_again_button_position()
        self.update_hint_button_position()
    
    def update_size_and_position(self, new_tile_width, new_tile_height, new_offset_x, new_offset_y):
        self.tile_width = new_tile_width
        self.tile_height = new_tile_height
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        
        # Update all tiles with new size and position
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.update_size(new_tile_width, new_tile_height)
                    tile.rect.x = tile.x * self.tile_width + self.offset_x
                    tile.rect.y = tile.y * self.tile_height + self.offset_y
        
        self.update_play_again_button_position()
        self.update_hint_button_position()
    
            
    def update_play_again_button_position(self):
        # Position button in center of screen with scaled size
        info = pygame.display.get_surface()
        if info:
            scale_factor = min(info.get_width() / 1600, info.get_height() / 1000)
            button_width = int(200 * scale_factor)
            button_height = int(60 * scale_factor)
            self.play_again_button.width = button_width
            self.play_again_button.height = button_height
            self.play_again_button.x = (info.get_width() - self.play_again_button.width) // 2
            self.play_again_button.y = info.get_height() // 2 + int(100 * scale_factor)
    
    def update_hint_button_position(self):
        # Position button in bottom-left corner with scaled size
        info = pygame.display.get_surface()
        if info:
            scale_factor = min(info.get_width() / 1600, info.get_height() / 1000)
            button_width = int(100 * scale_factor)
            button_height = int(40 * scale_factor)
            self.hint_button.width = button_width
            self.hint_button.height = button_height
            self.hint_button.x = 20
            self.hint_button.y = info.get_height() - self.hint_button.height - 20
            
    def update(self):
        if self.failed_match_timer > 0:
            self.failed_match_timer -= 1
            if self.failed_match_timer == 0:
                for tile in self.failed_match_tiles:
                    tile.selected = False
                self.selected_tiles.clear()
                self.failed_match_tiles = []
        
        # Update hint timer
        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer == 0:
                # Clear hint selection
                for tile in self.hint_tiles:
                    tile.selected = False
                self.hint_tiles = []
                
        # [自動解題更新邏輯] - 如需啟用，請取消以下註解
                
        if self.game_completed:
            # Update fireworks
            for firework in self.fireworks[:]:
                firework.update()
                if not firework.is_alive():
                    self.fireworks.remove(firework)
                    
            # Add new fireworks periodically
            self.firework_timer += 1
            if self.firework_timer >= 20:  # Every 20 frames
                self.firework_timer = 0
                info = pygame.display.get_surface()
                if info:
                    x = random.randint(100, info.get_width() - 100)
                    y = info.get_height() - 50
                    self.fireworks.append(Firework(x, y))
    
    def draw(self, screen):
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw(screen)
                    
        if self.animating and self.animation_path:
            self.draw_animation(screen)
            
        # [自動解題按鈕] - 如需啟用，請取消以下註解
        # Draw solve button only if game is not completed
        # if not self.game_completed:
        #     pygame.draw.rect(screen, (100, 100, 100), self.solve_button)
        #     pygame.draw.rect(screen, (200, 200, 200), self.solve_button, 2)
        #     font = pygame.font.Font(None, 24)
        #     text = font.render("SOLVE", True, (255, 255, 255))
        #     text_rect = text.get_rect(center=self.solve_button.center)
        #     screen.blit(text, text_rect)
            
        # Draw celebration if game is completed
        if self.game_completed:
            # Draw fireworks
            for firework in self.fireworks:
                firework.draw(screen)
                
            # Draw semi-transparent overlay
            overlay = pygame.Surface((screen.get_width(), screen.get_height()))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Draw congratulations text with shadow
            # Scale font size based on window size
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            scale_factor = min(screen_width / 1600, screen_height / 1000)  # Using initial dimensions
            congrats_font_size = int(96 * scale_factor)
            congrats_font_size = max(congrats_font_size, 48)  # Minimum font size
            font_big = get_chinese_font(congrats_font_size)
                
            # Draw shadow
            text_shadow = font_big.render("恭喜!!", True, (50, 30, 0))
            shadow_rect = text_shadow.get_rect(
                center=(screen.get_width() // 2 + 3, screen.get_height() // 2 - 50 + 3)
            )
            screen.blit(text_shadow, shadow_rect)
            
            # Draw main text
            text_congrats = font_big.render("恭喜!!", True, (255, 215, 0))
            text_rect = text_congrats.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2 - 50)
            )
            screen.blit(text_congrats, text_rect)
            
            # Draw play again button
            pygame.draw.rect(screen, (0, 100, 0), self.play_again_button)
            pygame.draw.rect(screen, (0, 200, 0), self.play_again_button, 3)
            # Scale button font
            button_font_size = int(36 * scale_factor)
            button_font_size = max(button_font_size, 20)  # Minimum font size
            font_button = get_chinese_font(button_font_size)
                
            text_play_again = font_button.render("再來一局", True, (255, 255, 255))
            text_rect = text_play_again.get_rect(center=self.play_again_button.center)
            screen.blit(text_play_again, text_rect)
        
        # Draw hint button (only during gameplay)
        if not self.game_completed:
            # Scale button appearance
            scale_factor = min(screen.get_width() / 1600, screen.get_height() / 1000)
            
            # Draw button
            # Gray out button during animation or hint display
            button_enabled = not self.animating and self.hint_timer == 0
            button_color = (0, 80, 150) if button_enabled else (100, 100, 100)
            border_color = (0, 150, 255) if button_enabled else (150, 150, 150)
            pygame.draw.rect(screen, button_color, self.hint_button)
            pygame.draw.rect(screen, border_color, self.hint_button, 2)
            
            # Draw text
            hint_font_size = int(24 * scale_factor)
            hint_font_size = max(hint_font_size, 16)  # Minimum font size
            font_hint = pygame.font.Font(None, hint_font_size)
            text_color = (255, 255, 255) if button_enabled else (200, 200, 200)
            text_hint = font_hint.render("提示", True, text_color)
            text_rect = text_hint.get_rect(center=self.hint_button.center)
            screen.blit(text_hint, text_rect)
        
            
    def draw_animation(self, screen):
        if len(self.animation_path) < 2:
            return
            
        # Draw the complete path instantly
        for i in range(len(self.animation_path) - 1):
            start_pos = self.get_pixel_position(self.animation_path[i])
            end_pos = self.get_pixel_position(self.animation_path[i + 1])
            pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 4)
        
        self.animation_progress += 1
        
        # Wait for 0.5 seconds
        wait_frames = 30
        if self.animation_progress >= wait_frames:
            self.finish_animation()
            # Check if there are still valid moves after removing tiles
            if not self.has_any_valid_move():
                self.shuffle_board()
            
    def get_pixel_position(self, grid_pos):
        x, y = grid_pos
        pixel_x = x * self.tile_width + self.tile_width // 2 + self.offset_x
        pixel_y = y * self.tile_height + self.tile_height // 2 + self.offset_y
        return (pixel_x, pixel_y)
        
    def finish_animation(self):
        for tile in self.tiles_to_remove:
            tile.visible = False
            tile.selected = False
            self.tiles[tile.y][tile.x] = None
            
        self.selected_tiles.clear()
        self.animation_path = []
        self.animation_progress = 0
        self.animating = False
        self.tiles_to_remove = []
        
        # Check if game is complete
        if self.is_game_complete():
            self.game_completed = True
                    
    def handle_click(self, pos):
        if self.animating or self.failed_match_timer > 0:
            return
            
        # Check if game is completed and play again button was clicked
        if self.game_completed:
            if self.play_again_button.collidepoint(pos):
                self.restart_game()
            return
        
        # Check if hint button was clicked
        if not self.animating and self.hint_timer == 0:
            if self.hint_button.collidepoint(pos):
                self.show_hint()
                return
            
            
        clicked_tile = None
        for row in self.tiles:
            for tile in row:
                if tile and tile.visible and tile.rect.collidepoint(pos):
                    clicked_tile = tile
                    break
            if clicked_tile:
                break
                
        if clicked_tile:
            self.handle_tile_selection(clicked_tile)
                    
    def handle_tile_selection(self, tile):
        if tile in self.selected_tiles:
            self.selected_tiles.remove(tile)
            tile.selected = False
        else:
            if len(self.selected_tiles) >= 2:
                for selected in self.selected_tiles:
                    selected.selected = False
                self.selected_tiles.clear()
                
            self.selected_tiles.append(tile)
            tile.selected = True
            
            if len(self.selected_tiles) == 2:
                self.check_match()
            
    def check_match(self):
        tile1, tile2 = self.selected_tiles
        
        path = self.can_connect(tile1, tile2)
        if tile1.match(tile2) and path:
            self.animation_path = path
            self.animation_progress = 0
            self.animating = True
            self.tiles_to_remove = [tile1, tile2]
        else:
            # Show both tiles selected for a moment before clearing
            self.failed_match_timer = 30  # 1 second at 60 FPS
            self.failed_match_tiles = self.selected_tiles.copy()
        
    def can_connect(self, tile1, tile2):
        if tile1 == tile2:
            return None
            
        pos1 = (tile1.x, tile1.y)
        pos2 = (tile2.x, tile2.y)
        
        queue = deque([(pos1, -1, -1, [pos1])])
        visited = set()
        
        while queue:
            (x, y), prev_dir, turns, path = queue.popleft()
            
            if (x, y) == pos2:
                return path
                
            if turns > 1:
                continue
                
            state = (x, y, prev_dir, turns)
            if state in visited:
                continue
            visited.add(state)
            
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            
            for i, (dx, dy) in enumerate(directions):
                nx, ny = x + dx, y + dy
                
                if nx < -1 or nx > self.width or ny < -1 or ny > self.height:
                    continue
                    
                if (nx, ny) != pos2:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.tiles[ny][nx] and self.tiles[ny][nx].visible:
                            continue
                
                new_turns = turns
                if prev_dir != -1 and prev_dir != i:
                    new_turns += 1
                    
                if new_turns <= 1:
                    new_path = path + [(nx, ny)]
                    queue.append(((nx, ny), i, new_turns, new_path))
                    
        return None
        
    def is_game_complete(self):
        for row in self.tiles:
            for tile in row:
                if tile and tile.visible:
                    return False
        return True
    
    # [自動解題功能] - 如需啟用，請取消以下所有註解
    # 步驟1: 取消 __init__ 中的自動解題相關變數註解
    # 步驟2: 取消 update() 中的自動解題更新邏輯註解
    # 步驟3: 取消 draw() 中的 SOLVE 按鈕繪製註解
    # 步驟4: 取消 handle_click() 中的 SOLVE 按鈕點擊處理註解
    # 步驟5: 取消以下兩個方法的註解
        
    def restart_game(self):
        # Reset all game state
        self.game_completed = False  # Set this first so main.py can detect the change
        self.tiles = []
        self.selected_tiles = []
        self.animation_path = []
        self.animation_progress = 0
        self.animating = False
        self.tiles_to_remove = []
        self.failed_match_timer = 0
        self.failed_match_tiles = []
        self.fireworks = []
        self.firework_timer = 0
        self.hint_timer = 0
        self.hint_tiles = []
        # Initialize a new board
        self.initialize_board()