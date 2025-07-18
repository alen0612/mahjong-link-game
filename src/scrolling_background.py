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
        self.spawn_timer = 0
        self.spawn_interval = 60  # Spawn new tile every 60 frames
        
        # Initialize with some tiles
        for i in range(8):
            self.spawn_tile(initial_x=i * 150)
            
    def spawn_tile(self, initial_x=None):
        rows = 3  # Number of rows of scrolling tiles
        for row in range(rows):
            x = initial_x if initial_x is not None else -100
            y = 100 + row * 200 + random.randint(-30, 30)
            tile_type = random.randint(0, 35)
            speed = random.uniform(0.8, 1.5)
            self.tiles.append(ScrollingTile(x, y, tile_type, speed))
            
    def update(self):
        # Update existing tiles
        for tile in self.tiles[:]:
            tile.update()
            # Remove tiles that have scrolled off screen
            if tile.x > self.screen_width + 100:
                self.tiles.remove(tile)
                
        # Spawn new tiles periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_tile()
            
    def draw(self, screen):
        for tile in self.tiles:
            tile.draw(screen)