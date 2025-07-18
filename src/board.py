import random
import pygame
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
                pygame.time.wait(300)
                self.check_match()
            
    def check_match(self):
        tile1, tile2 = self.selected_tiles
        
        if tile1.match(tile2) and self.can_connect(tile1, tile2):
            tile1.visible = False
            tile2.visible = False
            
        for tile in self.selected_tiles:
            tile.selected = False
        self.selected_tiles.clear()
        
    def can_connect(self, tile1, tile2):
        return True
        
    def is_game_complete(self):
        for row in self.tiles:
            for tile in row:
                if tile and tile.visible:
                    return False
        return True