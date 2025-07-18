import pygame

class Tile:
    def __init__(self, x, y, tile_type, size=80):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.size = size
        self.selected = False
        self.visible = True
        self.rect = pygame.Rect(x * size, y * size, size, size)
        
    def draw(self, screen):
        if not self.visible:
            return
            
        color = (100, 100, 100)
        if self.selected:
            color = (150, 150, 150)
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
    def handle_click(self, pos):
        if self.visible and self.rect.collidepoint(pos):
            self.selected = not self.selected
            return True
        return False
        
    def match(self, other):
        return self.tile_type == other.tile_type