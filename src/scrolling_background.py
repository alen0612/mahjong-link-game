import pygame
import random
import os

class ScrollingTile:
    def __init__(self, x, y, tile_type, speed):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.speed = speed
        self.width = 60
        self.height = 80
        self.image = None
        self.load_image()
        
    def load_image(self):
        display_type = self.tile_type
        if self.tile_type == 34:
            display_type = 0
        elif self.tile_type == 35:
            display_type = 1
            
        image_path = f"assets/tiles/{display_type}.svg"
        if os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                # Make it semi-transparent
                self.image.set_alpha(100)
            except:
                self.image = None
                
    def update(self):
        self.x += self.speed
        
    def draw(self, screen):
        # Draw white background for tile
        white_bg = pygame.Surface((self.width, self.height))
        white_bg.fill((255, 255, 255))
        white_bg.set_alpha(100)
        screen.blit(white_bg, (self.x, self.y))
        
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback to rectangle if image not found
            surf = pygame.Surface((self.width, self.height))
            surf.set_alpha(100)
            surf.fill((150, 150, 150))
            screen.blit(surf, (self.x, self.y))
            
        # Draw border
        border_color = (180, 180, 180, 100)
        pygame.draw.rect(screen, border_color, pygame.Rect(self.x, self.y, self.width, self.height), 2)

class ScrollingBackground:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tiles = []
        self.tile_spacing_x = 180  # Horizontal spacing
        self.tile_spacing_y = 120  # Vertical spacing for diagonal
        self.base_speed = 1.0  # Fixed speed for all tiles
        self.rows = []  # Track tiles by row
        self.spawn_offset = 0  # Track position for new tiles
        
        # Create diagonal rows
        num_rows = 7
        self.row_configs = []
        
        # Configure each row with different starting positions and y coordinates
        for i in range(num_rows):
            y_base = 50 + i * self.tile_spacing_y
            # Alternate rows start at different x positions for diagonal effect
            x_offset = (i % 2) * (self.tile_spacing_x / 2)
            self.row_configs.append({
                'y': y_base,
                'x_offset': x_offset,
                'tiles': []
            })
        
        # Initialize with tiles
        for row_idx, config in enumerate(self.row_configs):
            # Start with enough tiles to fill the screen
            num_initial_tiles = int(screen_width / self.tile_spacing_x) + 3
            for i in range(num_initial_tiles):
                x = config['x_offset'] + i * self.tile_spacing_x - 200
                self.spawn_tile_in_row(row_idx, x)
            
    def spawn_tile_in_row(self, row_idx, x_pos):
        config = self.row_configs[row_idx]
        y = config['y']
        tile_type = random.randint(0, 31)
        tile = ScrollingTile(x_pos, y, tile_type, self.base_speed)
        self.tiles.append(tile)
        config['tiles'].append(tile)
            
    def update(self):
        # Update all tiles
        for config in self.row_configs:
            tiles_to_remove = []
            
            for tile in config['tiles']:
                tile.update()
                # Mark tiles that have scrolled off screen for removal
                if tile.x > self.screen_width + 100:
                    tiles_to_remove.append(tile)
            
            # Remove tiles that are off screen
            for tile in tiles_to_remove:
                config['tiles'].remove(tile)
                self.tiles.remove(tile)
        
        # Check each row to see if new tiles are needed
        for row_idx, config in enumerate(self.row_configs):
            tiles = config['tiles']
            
            # Need to check the leftmost tile (first in list since we spawn from left)
            if tiles:
                leftmost_tile = min(tiles, key=lambda t: t.x)
                # Spawn new tile if the leftmost has moved far enough from the left edge
                if leftmost_tile.x > -50:
                    new_x = leftmost_tile.x - self.tile_spacing_x
                    self.spawn_tile_in_row(row_idx, new_x)
            else:
                # No tiles in this row, spawn one
                self.spawn_tile_in_row(row_idx, -100)
            
    def draw(self, screen):
        for tile in self.tiles:
            tile.draw(screen)