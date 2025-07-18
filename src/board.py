import random
import pygame
from collections import deque
from copy import deepcopy
from tile import Tile
from particle import Firework

class Board:
    def __init__(self, width=16, height=8, tile_width=60, tile_height=80, offset_x=0, offset_y=0):
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
        
        # [自動解題相關變數] - 如需啟用自動解題功能，請取消以下註解
        self.auto_solving = False
        self.solve_timer = 0
        self.solve_button = pygame.Rect(0, 0, 100, 40)
        self.update_solve_button_position()
        
        self.game_completed = False
        self.fireworks = []
        self.firework_timer = 0
        self.play_again_button = pygame.Rect(0, 0, 200, 60)
        self.update_play_again_button_position()
        self.initialize_board()
        
    def initialize_board(self):
        self.tiles = self.generate_solvable_board()
        
    def generate_solvable_board(self):
        max_attempts = 100
        
        for attempt in range(max_attempts):
            tile_types = []
            # Use 32 tile types (0-31), each appears 4 times for 128 total tiles
            # This ensures balanced distribution
            for i in range(32):
                tile_types.extend([i, i, i, i])  # Each type appears exactly 4 times
                
            random.shuffle(tile_types)
            
            tiles = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    tile_type = tile_types.pop()
                    tile = Tile(x, y, tile_type, self.tile_width, self.tile_height, self.offset_x, self.offset_y)
                    row.append(tile)
                tiles.append(row)
                
            if self.is_board_solvable(tiles):
                return tiles
                
        return tiles
        
    def is_board_solvable(self, test_tiles):
        board_copy = [[tile.tile_type if tile else None for tile in row] for row in test_tiles]
        visible_copy = [[True if tile else False for tile in row] for row in test_tiles]
        
        def find_match():
            for y1 in range(self.height):
                for x1 in range(self.width):
                    if not visible_copy[y1][x1]:
                        continue
                        
                    for y2 in range(self.height):
                        for x2 in range(self.width):
                            if (x1, y1) == (x2, y2) or not visible_copy[y2][x2]:
                                continue
                                
                            if board_copy[y1][x1] == board_copy[y2][x2]:
                                if self.can_connect_test(x1, y1, x2, y2, visible_copy):
                                    return (x1, y1, x2, y2)
            return None
            
        remaining = sum(sum(1 for cell in row if cell) for row in visible_copy)
        
        while remaining > 0:
            match = find_match()
            if not match:
                return False
                
            x1, y1, x2, y2 = match
            visible_copy[y1][x1] = False
            visible_copy[y2][x2] = False
            remaining -= 2
            
        return True
        
    def can_connect_test(self, x1, y1, x2, y2, visible_grid):
        if (x1, y1) == (x2, y2):
            return False
            
        queue = deque([((x1, y1), -1, -1)])
        visited = set()
        
        while queue:
            (x, y), prev_dir, turns = queue.popleft()
            
            if (x, y) == (x2, y2):
                return True
                
            if turns > 2:
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
                    
                if new_turns <= 2:
                    queue.append(((nx, ny), i, new_turns))
                    
        return False
    
    def update_position(self, new_offset_x, new_offset_y):
        self.offset_x = new_offset_x
        self.offset_y = new_offset_y
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.rect.x = tile.x * self.tile_width + self.offset_x
                    tile.rect.y = tile.y * self.tile_height + self.offset_y
        self.update_solve_button_position()
        self.update_play_again_button_position()
    
    def update_solve_button_position(self):
        # Position button in bottom-right corner with some margin
        import pygame
        info = pygame.display.get_surface()
        if info:
            self.solve_button.x = info.get_width() - self.solve_button.width - 20
            self.solve_button.y = info.get_height() - self.solve_button.height - 20
            
    def update_play_again_button_position(self):
        # Position button in center of screen
        import pygame
        info = pygame.display.get_surface()
        if info:
            self.play_again_button.x = (info.get_width() - self.play_again_button.width) // 2
            self.play_again_button.y = info.get_height() // 2 + 100
            
    def update(self):
        if self.failed_match_timer > 0:
            self.failed_match_timer -= 1
            if self.failed_match_timer == 0:
                for tile in self.failed_match_tiles:
                    tile.selected = False
                self.selected_tiles.clear()
                self.failed_match_tiles = []
                
        # [自動解題更新邏輯] - 如需啟用，請取消以下註解
        # if self.auto_solving and not self.animating:
        #     self.solve_timer += 1
        #     # Speed up solving by checking every 15 frames instead of 30
        #     if self.solve_timer >= 7:
        #         self.solve_timer = 0
        #         self.auto_solve_step()
                
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
            try:
                # Try to use Chinese font
                font_big = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", 96)
            except:
                # Fallback to English if Chinese font not available
                font_big = pygame.font.Font(None, 72)
                
            # Draw shadow
            text_shadow = font_big.render("恭喜!!", True, (50, 30, 0))
            shadow_rect = text_shadow.get_rect(center=(screen.get_width() // 2 + 3, screen.get_height() // 2 - 50 + 3))
            screen.blit(text_shadow, shadow_rect)
            
            # Draw main text
            text_congrats = font_big.render("恭喜!!", True, (255, 215, 0))
            text_rect = text_congrats.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
            screen.blit(text_congrats, text_rect)
            
            # Draw play again button
            pygame.draw.rect(screen, (0, 100, 0), self.play_again_button)
            pygame.draw.rect(screen, (0, 200, 0), self.play_again_button, 3)
            try:
                font_button = pygame.font.Font("/System/Library/Fonts/STHeiti Medium.ttc", 36)
            except:
                font_button = pygame.font.Font(None, 36)
                
            text_play_again = font_button.render("再來一局", True, (255, 255, 255))
            text_rect = text_play_again.get_rect(center=self.play_again_button.center)
            screen.blit(text_play_again, text_rect)
            
    def draw_animation(self, screen):
        if len(self.animation_path) < 2:
            return
            
        # Draw the complete path instantly
        for i in range(len(self.animation_path) - 1):
            start_pos = self.get_pixel_position(self.animation_path[i])
            end_pos = self.get_pixel_position(self.animation_path[i + 1])
            pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 4)
        
        self.animation_progress += 1
        
        # Wait for 0.5 seconds normally, or 0.25 seconds during auto-solve
        wait_frames = 7 if self.auto_solving else 30
        if self.animation_progress >= wait_frames:
            self.finish_animation()
            
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
            if self.auto_solving:
                self.auto_solving = False
                    
    def handle_click(self, pos):
        if self.animating or self.failed_match_timer > 0 or self.auto_solving:
            return
            
        # Check if game is completed and play again button was clicked
        if self.game_completed:
            if self.play_again_button.collidepoint(pos):
                self.restart_game()
            return
            
        # [自動解題按鈕點擊處理] - 如需啟用，請取消以下註解
        # Check if solve button was clicked
        # if self.solve_button.collidepoint(pos):
        #     self.start_auto_solve()
        #     return
            
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
                
            if turns > 2:
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
                    
                if new_turns <= 2:
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
    
    def start_auto_solve(self):
        self.auto_solving = True
        self.solve_timer = 0
        # Clear any existing selections
        for tile in self.selected_tiles:
            tile.selected = False
        self.selected_tiles.clear()
        
    def auto_solve_step(self):
        # Find a matching pair
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
                                # Found a match, select and remove them
                                self.selected_tiles = [tile1, tile2]
                                tile1.selected = True
                                tile2.selected = True
                                # Start the animation
                                self.animation_path = path
                                self.animation_progress = 0
                                self.animating = True
                                self.tiles_to_remove = [tile1, tile2]
                                return
        
        # No more matches found, stop auto-solving
        self.auto_solving = False
        
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
        self.auto_solving = False
        self.solve_timer = 0
        self.fireworks = []
        self.firework_timer = 0
        # Initialize a new board
        self.initialize_board()