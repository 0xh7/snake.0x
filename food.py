import random
import pygame
import math
from config import *

class Food:
    def __init__(self, x, y, value=1, color=None):
        self.x = x
        self.y = y
        self.value = value
        self.radius = 5 + value
        self.color = color if color else self._get_random_color()
        self.pulse_size = 0
        self.pulse_dir = 0.1
        self.pulse_speed = random.uniform(0.05, 0.15)
        self.rotation = random.uniform(0, 360)
        self.spin_speed = random.uniform(-3, 3)
        
    def _get_random_color(self):
        base_colors = [
            (255, 100, 100),
            (100, 255, 100),
            (100, 100, 255),
            (255, 255, 100),
            (255, 150, 50),
            (200, 100, 255),
            (100, 255, 255),
            (255, 100, 255),
        ]
        return random.choice(base_colors)
        
    def update(self):
        self.pulse_size += self.pulse_dir * self.pulse_speed
        if self.pulse_size > 1.0:
            self.pulse_size = 1.0
            self.pulse_dir = -0.1
        elif self.pulse_size < 0.0:
            self.pulse_size = 0.0
            self.pulse_dir = 0.1
            
        self.rotation += self.spin_speed
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        if (screen_x + self.radius < 0 or screen_x - self.radius > WINDOW_WIDTH or
            screen_y + self.radius < 0 or screen_y - self.radius > WINDOW_HEIGHT):
            return
        
        if self.value <= 2:
            self._draw_circle_food(surface, screen_x, screen_y)
        else:
            sides = min(8, self.value + 3)
            self._draw_polygon_food(surface, screen_x, screen_y, sides)
    
    def _draw_circle_food(self, surface, x, y):
        pulse_radius = self.radius + int(self.pulse_size * 3)
        
        food_surface = pygame.Surface((pulse_radius*2+2, pulse_radius*2+2), pygame.SRCALPHA)
        
        if self.pulse_size > 0:
            for r in range(pulse_radius, self.radius, -1):
                alpha = int(max(0, min(150, 180 * (1 - (r - self.radius) / (pulse_radius - self.radius + 0.1)) * self.pulse_size)))
                pygame.draw.circle(
                    food_surface,
                    (*self.color, alpha),
                    (pulse_radius+1, pulse_radius+1),
                    r
                )
        
        pygame.draw.circle(
            food_surface,
            self.color,
            (pulse_radius+1, pulse_radius+1),
            self.radius
        )
        
        highlight_radius = max(2, int(self.radius * 0.6))
        highlight_offset = int(self.radius * 0.2)
        highlight_color = (255, 255, 255, 180)
        
        pygame.draw.ellipse(
            food_surface,
            highlight_color,
            (
                pulse_radius+1-highlight_radius//2-highlight_offset, 
                pulse_radius+1-highlight_radius//2-highlight_offset,  
                highlight_radius,
                highlight_radius//1.3
            )
        )
        
        surface.blit(food_surface, (x-pulse_radius-1, y-pulse_radius-1))
        
        if self.radius > 5:
            reflection_radius = int(self.radius * 0.4)
            reflection_offset = int(self.radius * 0.5)
            reflection_color = (255, 255, 255, 70)
            
            pygame.draw.circle(
                surface,
                reflection_color,
                (x, y + reflection_offset),
                reflection_radius
            )
    
    def _draw_polygon_food(self, surface, x, y, sides):
        points = []
        radius = self.radius + int(self.pulse_size * 2)
        for i in range(sides):
            angle = math.radians(self.rotation + i * (360 / sides))
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        
        polygon_surface = pygame.Surface((radius*2+2, radius*2+2), pygame.SRCALPHA)
        
        offset_points = [(p[0]-x+radius+1, p[1]-y+radius+1) for p in points]
        
        glow_color = (*self.color, 100)
        pygame.draw.polygon(polygon_surface, glow_color, offset_points)
        
        inner_points = []
        inner_radius = radius * 0.8
        for i in range(sides):
            angle = math.radians(self.rotation + i * (360 / sides))
            px = radius+1 + math.cos(angle) * inner_radius
            py = radius+1 + math.sin(angle) * inner_radius
            inner_points.append((px, py))
        
        inner_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.polygon(polygon_surface, inner_color, inner_points)
        
        highlight_radius = radius * 0.3
        pygame.draw.circle(
            polygon_surface,
            (255, 255, 255, 200),
            (radius+1, radius+1),
            int(highlight_radius)
        )
        
        surface.blit(polygon_surface, (x-radius-1, y-radius-1))

class FoodManager:
    def __init__(self):
        self.foods = []
        
    def spawn_food(self, snake_positions):
        if len(self.foods) < MAX_FOOD_ITEMS and random.random() < FOOD_SPAWN_RATE:
            margin = 100
            x = random.randint(margin, WORLD_WIDTH - margin)
            y = random.randint(margin, WORLD_HEIGHT - margin)
            
            too_close = False
            for snake_pos in snake_positions:
                for pos in snake_pos:
                    if ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) < 400:
                        too_close = True
                        break
                if too_close:
                    break
            
            if not too_close:
                if random.random() < 0.1:
                    value = random.randint(2, 5)
                    self.foods.append(Food(x, y, value, YELLOW))
                else:
                    self.foods.append(Food(x, y))
                    
    def update(self, snake_positions):
        self.spawn_food(snake_positions)
        
        for food in self.foods:
            food.update()
        
    def draw(self, surface, camera_x, camera_y, view_width, view_height):
        for food in self.foods:
            food.draw(surface, camera_x, camera_y)
            
    def check_collision(self, x, y, radius):
        for i, food in enumerate(self.foods):
            distance = ((food.x - x) ** 2 + (food.y - y) ** 2) ** 0.5
            if distance < (radius + food.radius - COLLISION_BUFFER):
                value = food.value
                self.foods.pop(i)
                return value
        return 0
    
    def add_food_at_position(self, x, y, value=1, color=None):
        if len(self.foods) < MAX_FOOD_ITEMS:
            if color is None:
                boost_food_color = (100, 200, 255)
            else:
                r, g, b = color
                boost_food_color = (
                    min(255, r + 50),
                    min(255, g + 50),
                    min(255, b + 50)
                )
                
            self.foods.append(Food(x, y, value, boost_food_color))
