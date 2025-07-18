import random

import pygame

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-15, -5)
        self.gravity = 0.5
        self.lifetime = random.randint(30, 60)
        self.age = 0
        
        if color is None:
            self.color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
        else:
            self.color = color
            
        self.size = random.randint(2, 4)
        self.current_color = self.color
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.age += 1
        
        # Fade out
        fade_factor = 1 - (self.age / self.lifetime)
        self.current_color = (
            int(self.color[0] * fade_factor),
            int(self.color[1] * fade_factor),
            int(self.color[2] * fade_factor)
        )
        
    def draw(self, screen):
        if self.age < self.lifetime:
            pygame.draw.circle(screen, self.current_color, 
                             (int(self.x), int(self.y)), self.size)
            
    def is_alive(self):
        return self.age < self.lifetime

class Firework:
    def __init__(self, x, y):
        self.particles = []
        self.exploded = False
        self.rocket_y = y
        self.rocket_x = x
        self.target_y = random.randint(100, 300)
        self.rocket_speed = -10
        
    def update(self):
        if not self.exploded:
            self.rocket_y += self.rocket_speed
            if self.rocket_y <= self.target_y:
                self.explode()
        else:
            for particle in self.particles[:]:
                particle.update()
                if not particle.is_alive():
                    self.particles.remove(particle)
                    
    def explode(self):
        self.exploded = True
        num_particles = random.randint(30, 50)
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        for _ in range(num_particles):
            self.particles.append(Particle(self.rocket_x, self.rocket_y, color))
            
    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, (255, 255, 200), 
                             (int(self.rocket_x), int(self.rocket_y)), 3)
        else:
            for particle in self.particles:
                particle.draw(screen)
                
    def is_alive(self):
        return not self.exploded or len(self.particles) > 0