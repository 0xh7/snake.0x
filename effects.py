import pygame
import random
import math
from config import *

class Particle:
    def __init__(self, x, y, vel_x, vel_y, size, color, life, gravity=0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.size = size
        self.original_size = size
        if color is None:
            self.color = (255, 255, 255)
        else:
            self.color = tuple(max(0, min(255, c)) for c in color[:3])
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.drag = 0.98
        
    def update(self, dt):
        self.vel_y += self.gravity * dt
        
        self.vel_x *= self.drag
        self.vel_y *= self.drag
        
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        
        self.life -= dt
        
        self.size = self.original_size * (self.life / self.max_life)
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        if (screen_x < -self.size or screen_x > WINDOW_WIDTH + self.size or
            screen_y < -self.size or screen_y > WINDOW_HEIGHT + self.size):
            return
            
        alpha = int(255 * (self.life / self.max_life))
        
        size = max(1, int(self.size))
        particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        
        try:
            particle_color = (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            )
            pygame.draw.circle(
                particle_surface, 
                particle_color,
                (size, size), 
                size
            )
            
            surface.blit(particle_surface, (screen_x - size, screen_y - size))
        except (ValueError, TypeError) as e:
            pass

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def update(self, dt):
        i = 0
        while i < len(self.particles):
            self.particles[i].update(dt)
            
            if self.particles[i].life <= 0:
                self.particles.pop(i)
            else:
                i += 1
                
        if len(self.particles) > PARTICLE_MAX_COUNT:
            self.particles = self.particles[-PARTICLE_MAX_COUNT:]
    
    def draw(self, surface, camera_x, camera_y):
        for particle in self.particles:
            try:
                particle.draw(surface, camera_x, camera_y)
            except Exception:
                if particle in self.particles:
                    self.particles.remove(particle)
    
    def add_explosion(self, x, y, color):
        try:
            if color is None:
                color = (220, 100, 100)
            
            if len(color) > 3:
                color = color[:3]
                
            r, g, b = color
            softened_color = (
                min(255, int(r * 0.9)),
                min(255, int(g * 0.9)),
                min(255, int(b * 0.9))
            )
                
            for _ in range(DEATH_EXPLOSION_SIZE):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 7)
                
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                
                size = random.uniform(3, 10)
                life = random.uniform(0.5, 1.3)
                
                r, g, b = softened_color
                r = min(255, max(0, r + random.randint(-15, 15)))
                g = min(255, max(0, g + random.randint(-15, 15)))
                b = min(255, max(0, b + random.randint(-15, 15)))
                
                self.particles.append(
                    Particle(x, y, vel_x, vel_y, size, (r, g, b), life, gravity=0.1)
                )
        except Exception:
            pass
    
    def add_food_sparkle(self, x, y, color):
        try:
            if color is None:
                color = (220, 220, 100)
            
            if len(color) > 3:
                color = color[:3]
                
            r, g, b = color
            bright_color = (
                min(255, r + 70),
                min(255, g + 70),
                min(255, b + 70)
            )
            
            for _ in range(6):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(0.8, 2.5)
                
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                
                size = random.uniform(1.5, 4)
                life = random.uniform(0.2, 0.6)
                
                self.particles.append(
                    Particle(x, y, vel_x, vel_y, size, bright_color, life)
                )
        except Exception:
            pass

class TextEffect:
    def __init__(self, x, y, text, color, size=20, life=1.0, vel_y=-1.5):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.vel_y = vel_y
        
        self.font = pygame.font.SysFont(UI_FONT, size)
        self.text_surface = self.font.render(text, True, color)
        
    def update(self, dt):
        self.y += self.vel_y * dt * 60
        
        self.life -= dt
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        alpha = int(255 * (self.life / self.max_life))
        
        alpha_surface = self.text_surface.copy()
        alpha_surface.set_alpha(alpha)
        
        text_rect = alpha_surface.get_rect(center=(screen_x, screen_y))
        
        surface.blit(alpha_surface, text_rect)

class FloatingText:
    def __init__(self):
        self.texts = []
    
    def update(self, dt):
        i = 0
        while i < len(self.texts):
            self.texts[i].update(dt)
            
            if self.texts[i].life <= 0:
                self.texts.pop(i)
            else:
                i += 1
    
    def draw(self, surface, camera_x, camera_y):
        for text in self.texts:
            text.draw(surface, camera_x, camera_y)
    
    def add_text(self, x, y, text, color=WHITE, size=20):
        self.texts.append(TextEffect(x, y, text, color, size))
