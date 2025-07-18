import random
import pygame
from collections import deque
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
        self.initialize_board()
        
    def initialize_board(self):
        tile_types = []
        num_tile_types = 36
        
        for i in range(num_tile_types):
            tile_types.extend([i, i])
            
        random.shuffle(tile_types)
        
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = tile_types.pop()
                tile = Tile(x, y, tile_type, self.tile_size, self.offset_x, self.offset_y)
                row.append(tile)
            self.tiles.append(row)
            
    def draw(self, screen):
        for row in self.tiles:
            for tile in row:
                if tile:
                    tile.draw(screen)
                    
    def handle_click(self, pos):
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
        
        if tile1.match(tile2) and self.can_connect(tile1, tile2):
            tile1.visible = False
            tile2.visible = False
            self.tiles[tile1.y][tile1.x] = None
            self.tiles[tile2.y][tile2.x] = None
            
        for tile in self.selected_tiles:
            tile.selected = False
        self.selected_tiles.clear()
        
    def can_connect(self, tile1, tile2):
        if tile1 == tile2:
            return False
            
        pos1 = (tile1.x, tile1.y)
        pos2 = (tile2.x, tile2.y)
        
        queue = deque([(pos1, -1, -1, -1)])
        visited = set()
        
        while queue:
            (x, y), prev_dir, turns = queue.popleft()
            
            if (x, y) == pos2:
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
                    
                if (nx, ny) != pos2:
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.tiles[ny][nx] and self.tiles[ny][nx].visible:
                            continue
                
                new_turns = turns
                if prev_dir != -1 and prev_dir != i:
                    new_turns += 1
                    
                if new_turns <= 2:
                    queue.append(((nx, ny), i, new_turns))
                    
        return False
        
    def is_game_complete(self):
        for row in self.tiles:
            for tile in row:
                if tile and tile.visible:
                    return False
        return True