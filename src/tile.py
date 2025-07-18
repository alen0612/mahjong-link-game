import os

import pygame
from utils import resource_path

class Tile:
    def __init__(self, x, y, tile_type, width=60, height=80, offset_x=0, offset_y=0):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.width = width
        self.height = height
        self.selected = False
        self.visible = True
        self.rect = pygame.Rect(x * width + offset_x, y * height + offset_y, width, height)
        self.image = None
        self.load_image()
        
    def load_image(self):
        # Map tile types to actual file names
        # 34 -> 0, 35 -> 1 (since they are duplicates)
        display_type = self.tile_type
        if self.tile_type == 34:
            display_type = 0
        elif self.tile_type == 35:
            display_type = 1
            
        image_path = resource_path(os.path.join("assets", "tiles", f"{display_type}.svg"))
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, IOError, OSError):
            self.image = None
        
    def draw(self, screen):
        if not self.visible:
            return
            
        # Draw white background for tile
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (180, 180, 180), self.rect, 2)
        
        if self.image:
            # Create a slightly smaller rect for the image to show border
            image_rect = self.rect.inflate(-4, -4)
            scaled_image = pygame.transform.scale(self.image, (image_rect.width, image_rect.height))
            screen.blit(scaled_image, image_rect.topleft)
        else:
            color = (100, 100, 100)
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
            
            # Calculate font size based on tile size
            font_size = max(12, min(self.width // 3, 36))
            font = pygame.font.Font(None, font_size)
            text = font.render(str(self.tile_type), True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
            
        if self.selected:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(100)
            overlay.fill((255, 255, 0))
            screen.blit(overlay, self.rect.topleft)
            pygame.draw.rect(screen, (255, 255, 0), self.rect, 3)
        
    def handle_click(self, pos):
        if self.visible and self.rect.collidepoint(pos):
            self.selected = not self.selected
            return True
        return False
        
    def match(self, other):
        return self.tile_type == other.tile_type
    
    def update_size_and_position(self, new_width, new_height, new_offset_x, new_offset_y):
        """Update tile size and position when window is resized"""
        self.width = new_width
        self.height = new_height
        self.rect = pygame.Rect(self.x * new_width + new_offset_x, self.y * new_height + new_offset_y, new_width, new_height)
        # Reload image with new size
        self.load_image()