import random
import pygame
from collections import deque
from copy import deepcopy
from tile import Tile

class Board:
    def __init__(self, width=12, height=6, tile_size=80, offset_x=0, offset_y=0):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tiles = []
        self.selected_tiles = []
        self.animation_path = []
        self.animation_progress = 0
        self.animation_speed = 5
        self.animating = False
        self.tiles_to_remove = []
        self.failed_match_timer = 0
        self.failed_match_tiles = []
        self.initialize_board()
        
    def initialize_board(self):
        self.tiles = self.generate_solvable_board()
        
    def generate_solvable_board(self):
        max_attempts = 100
        
        for attempt in range(max_attempts):
            tile_types = []
            # Use 36 tile types (0-35), each appears twice for 72 total tiles
            for i in range(36):
                tile_types.extend([i, i])
                
            random.shuffle(tile_types)
            
            tiles = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    tile_type = tile_types.pop()
                    tile = Tile(x, y, tile_type, self.tile_size, self.offset_x, self.offset_y)
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
                    tile.rect.x = tile.x * self.tile_size + self.offset_x
                    tile.rect.y = tile.y * self.tile_size + self.offset_y
            
    def update(self):
        if self.failed_match_timer > 0:
            self.failed_match_timer -= 1
            if self.failed_match_timer == 0:
                for tile in self.failed_match_tiles:
                    tile.selected = False
                self.selected_tiles.clear()
                self.failed_match_tiles = []
    
    def draw(self, screen):
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw(screen)
                    
        if self.animating and self.animation_path:
            self.draw_animation(screen)
            
    def draw_animation(self, screen):
        if len(self.animation_path) < 2:
            return
            
        segments_to_draw = min(self.animation_progress // self.animation_speed + 1, len(self.animation_path) - 1)
        
        for i in range(segments_to_draw):
            if i + 1 < len(self.animation_path):
                start_pos = self.get_pixel_position(self.animation_path[i])
                end_pos = self.get_pixel_position(self.animation_path[i + 1])
                
                if i < segments_to_draw - 1:
                    pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 4)
                else:
                    progress = (self.animation_progress % self.animation_speed) / self.animation_speed
                    current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                    current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                    pygame.draw.line(screen, (255, 0, 0), start_pos, (current_x, current_y), 4)
        
        self.animation_progress += 1
        
        if self.animation_progress >= (len(self.animation_path) - 1) * self.animation_speed:
            self.finish_animation()
            
    def get_pixel_position(self, grid_pos):
        x, y = grid_pos
        pixel_x = x * self.tile_size + self.tile_size // 2 + self.offset_x
        pixel_y = y * self.tile_size + self.tile_size // 2 + self.offset_y
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
                    
    def handle_click(self, pos):
        if self.animating or self.failed_match_timer > 0:
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