import pygame
import math
import random
from config import *

class Snake:
    def __init__(self, x, y, color=None, is_player=False, skin_index=0):
        self.is_player = is_player
        
        self.skin_index = skin_index if is_player else random.randint(0, len(SKINS)-1)
        self.skin = SKINS[self.skin_index]
        self.color = color if color else self._get_skin_color()
        
        self.speed = PLAYER_SPEED if is_player else AI_SPEED
        self.angle = random.uniform(0, 2 * math.pi)
        self.segments = []
        self.head_radius = 10
        self.segment_radius = 8
        self.score = 0
        self.alive = True
        self.glow_effect = 0
        
        self.trail = []
        self.trail_length = 10
        self.trail_counter = 0
        
        self.boosting = False
        self.boost_cooldown = 0
        self.boost_effect_counter = 0
        self.boost_drop_timer = 0
        
        self.last_direction_change = 0
        self.collision_immune = False
        self.collision_immune_time = 0
        
        self.color_index = 0
        self.color_cycle_timer = 0
        
        self.MAX_SEGMENTS = 1000
        self.segment_colors = {}
        
        for i in range(self.MAX_SEGMENTS):
            self.segment_colors[i] = self._compute_static_color(i)
        
        for i in range(INITIAL_SNAKE_LENGTH):
            offset = i * self.segment_radius * 2
            self.segments.append([
                x - offset * math.cos(self.angle),
                y - offset * math.sin(self.angle)
            ])
        
        self.target_angle = self.angle
        self.decision_counter = 0
    
    def _get_skin_color(self):
        if len(self.skin["colors"]) > 0:
            return self.skin["colors"][0]
        return (0, 255, 0)
    
    def _get_segment_color(self, segment_index):
        if segment_index < self.MAX_SEGMENTS:
            return self.segment_colors[segment_index]
        return self.segment_colors[segment_index % self.MAX_SEGMENTS]
    
    def _compute_static_color(self, segment_index):
        pattern = self.skin["pattern"]
        colors = self.skin["colors"]
        
        if not colors:
            return (0, 255, 0)
            
        if pattern == "solid":
            return colors[0]
            
        elif pattern == "rainbow":
            rainbow_colors = PATTERN_COLORS["rainbow"]
            group_size = 3
            color_index = (segment_index // group_size) % len(rainbow_colors)
            return rainbow_colors[color_index]
            
        elif pattern == "gradient":
            if len(colors) >= 2:
                color1 = colors[0]
                color2 = colors[1]
                
                fixed_segment_count = 30
                ratio = min(1.0, segment_index / fixed_segment_count)
                
                return (
                    int(color1[0] * (1 - ratio) + color2[0] * ratio),
                    int(color1[1] * (1 - ratio) + color2[1] * ratio),
                    int(color1[2] * (1 - ratio) + color2[2] * ratio)
                )
            return colors[0]
            
        elif pattern == "tiger":
            tiger_colors = PATTERN_COLORS["tiger"]
            return tiger_colors[segment_index % 2]
            
        elif pattern == "neon":
            neon_colors = PATTERN_COLORS["neon"]
            return neon_colors[segment_index % 2]
            
        elif pattern == "lava":
            lava_colors = PATTERN_COLORS["lava"]
            
            if len(lava_colors) >= 3:
                if segment_index == 0:
                    return lava_colors[0]
                elif segment_index % 5 == 0:
                    return lava_colors[2]
                elif segment_index % 3 == 0:
                    return lava_colors[1]
                else:
                    return lava_colors[0]
            return colors[0]
            
        return colors[0]
    
    def set_skin(self, skin_index):
        if 0 <= skin_index < len(SKINS):
            self.skin_index = skin_index
            self.skin = SKINS[skin_index]
            self.color = self._get_skin_color()
            
           
            for i in range(self.MAX_SEGMENTS):
                self.segment_colors[i] = self._compute_static_color(i)
            
          
            self.color_index = 0
            self.color_cycle_timer = 0
    
    def set_direction(self, angle):
        old_angle = self.angle
        self.angle = angle
        
        if abs(math.sin(old_angle - angle)) > 0.7:
            self.collision_immune = True
            self.collision_immune_time = pygame.time.get_ticks()
    
    def toggle_boost(self, activate):
        if activate:
            if not self.boosting and self.boost_cooldown <= 0 and len(self.segments) > BOOST_MIN_LENGTH:
                self.boosting = True
                self.boost_effect_counter = 0
                self.boost_drop_timer = 0
        else:
            if self.boosting:
                self.boosting = False
                self.boost_cooldown = BOOST_COOLDOWN * FPS
    
    def move(self):
        if not self.alive:
            return [], False
        
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1
        
        current_speed = self.speed
        if self.boosting:
            current_speed *= BOOST_SPEED_MULTIPLIER
        
        dx = current_speed * math.cos(self.angle)
        dy = current_speed * math.sin(self.angle)
        
        new_head = [self.segments[0][0] + dx, self.segments[0][1] + dy]
        
        self.segments.insert(0, new_head)
        
        dropped_segments = []
        score_reduced = False
        
        if self.boosting and len(self.segments) > BOOST_MIN_LENGTH:
            self.boost_drop_timer += 1
            
            boost_drop_interval = BOOST_SEGMENT_DROP_INTERVAL
            
            if self.boost_drop_timer >= boost_drop_interval:
                self.boost_drop_timer = 0
                
                dropped_segment = self.segments.pop()
                dropped_segments.append(dropped_segment)
                
                if self.is_player and self.score > 0:
                    self.score -= 1
                    score_reduced = True
                
                if len(self.segments) > BOOST_MIN_LENGTH:
                    self.segments.pop()
            else:
                self.segments.pop()
        else:
            self.segments.pop()
        
        self.trail_counter += 1
        if self.trail_counter >= 2:
            self.trail_counter = 0
            if len(self.trail) >= self.trail_length:
                self.trail.pop()
            self.trail.insert(0, list(new_head))
            
        if self.glow_effect > 0:
            self.glow_effect -= 0.05
        
        if self.collision_immune and pygame.time.get_ticks() - self.collision_immune_time > 500:
            self.collision_immune = False
        
        if self.boost_effect_counter > 0 and not self.boosting:
            self.boost_effect_counter = max(0, self.boost_effect_counter - 0.1)
            
        return dropped_segments, score_reduced
    
    def grow(self, amount=1):
        for _ in range(amount):
            last_segment = self.segments[-1]
            self.segments.append(list(last_segment))
            self.score += 1
            
        self.glow_effect = 1.0
    
    def check_boundary_collision(self, world_width, world_height):
        x, y = self.segments[0]
        margin = self.head_radius - COLLISION_BUFFER
        
        if (x < margin or x > world_width - margin or
            y < margin or y > world_height - margin):
            return True
        return False
    
    def check_self_collision(self):
        if not ENABLE_SELF_COLLISION:
            return False
        
        if self.collision_immune:
            return False
            
        if len(self.segments) <= SELF_COLLISION_START_INDEX:
            return False
            
        head = self.segments[0]
        for i in range(SELF_COLLISION_START_INDEX, len(self.segments)):
            segment = self.segments[i]
            distance = math.sqrt((head[0] - segment[0])**2 + (head[1] - segment[1])**2)
            
            if distance < (self.head_radius - COLLISION_BUFFER):
                return True
        return False
    
    def check_snake_collision(self, other_snake):
        if not self.alive or not other_snake.alive:
            return False
            
        head = self.segments[0]
        
        for segment in other_snake.segments:
            distance = math.sqrt((head[0] - segment[0])**2 + (head[1] - segment[1])**2)
            if distance < (self.head_radius + other_snake.segment_radius - COLLISION_BUFFER):
                return True
        return False
    
    def die(self):
        if not self.alive:
            return []
            
        self.alive = False
        
        dropped_food = []
        
        food_count = min(DROPPED_FOOD_COUNT, len(self.segments) // 2)
        
        head_x, head_y = self.segments[0]
        for _ in range(food_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 80)
            food_x = head_x + math.cos(angle) * distance
            food_y = head_y + math.sin(angle) * distance
            
            value = max(1, min(5, len(self.segments) // 20))
            dropped_food.append((food_x, food_y, value))
            
        return dropped_food
    
    def draw(self, surface, camera_x, camera_y):
        if not self.alive:
            return
        
        in_view = False
        for segment in self.segments:
            screen_x = segment[0] - camera_x
            screen_y = segment[1] - camera_y
            if (0 <= screen_x <= WINDOW_WIDTH and 0 <= screen_y <= WINDOW_HEIGHT):
                in_view = True
                break
        
        if not in_view:
            return
            
        if self.boosting:
            self._draw_boost_effect(surface, camera_x, camera_y)
        
        segment_count = len(self.segments)
        
        for i in range(segment_count - 1, -1, -1):
            segment = self.segments[i]
            screen_x = int(segment[0] - camera_x)
            screen_y = int(segment[1] - camera_y)
            
            if not (0 <= screen_x <= WINDOW_WIDTH and 0 <= screen_y <= WINDOW_HEIGHT):
                continue
                
            segment_color = self.segment_colors[i]
                
            if i == 0:
                radius = self.head_radius
                if GLOW_INTENSITY > 0:
                    glow_radius = int(radius * 1.5)
                    glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                    
                    for r in range(glow_radius, 0, -2):
                        alpha = max(0, int(150 * (r / glow_radius) * (1.0 - r / glow_radius)))
                        glow_color = (*segment_color, alpha)
                        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), r)
                    
                    surface.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius))
            else:
                factor = 0.85 + 0.15 * min(1.0, i / (segment_count * 0.25))
                radius = int(self.segment_radius * factor)
            
            pygame.draw.circle(surface, segment_color, (screen_x, screen_y), radius)
            
            if i > 0 and self.skin["pattern"] != "solid" and i % 3 == 0:
                pattern_radius = int(radius * 0.7)
                darker_color = tuple(max(0, c - 50) for c in segment_color)
                pygame.draw.circle(surface, darker_color, (screen_x, screen_y), pattern_radius)
        
        self._draw_head_details(surface, camera_x, camera_y)
    
    def _draw_boost_effect(self, surface, camera_x, camera_y):
        head = self.segments[0]
        screen_head_x = int(head[0] - camera_x)
        screen_head_y = int(head[1] - camera_y)
        
        boost_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        if len(self.segments) > 1:
            num_points = min(25, len(self.segments) - 1)
            
            flame_points = []
            for i in range(min(num_points, len(self.segments))):
                if i >= len(self.segments) - 1:
                    break
                    
                segment = self.segments[i]
                screen_x = int(segment[0] - camera_x)
                screen_y = int(segment[1] - camera_y)
                
                jitter_x = random.uniform(-2, 2) * (1 - i/num_points)
                jitter_y = random.uniform(-2, 2) * (1 - i/num_points)
                
                flame_points.append((screen_x + jitter_x, screen_y + jitter_y))
                
            for i in range(len(flame_points) - 1):
                effect_width = max(2, int(18 * (1 - i/num_points)))
                opacity = max(20, int(180 * (1 - i/num_points)))
                
                effect_color = self._get_segment_color(0)
                blend_factor = 1 - i/num_points
                r = int(255 * blend_factor + effect_color[0] * (1-blend_factor))
                g = int(215 * blend_factor + effect_color[1] * (1-blend_factor))
                b = int(120 * blend_factor + effect_color[2] * (1-blend_factor))
                
                pygame.draw.line(
                    boost_surface,
                    (r, g, b, opacity),
                    flame_points[i],
                    flame_points[i+1],
                    effect_width
                )
                
                if i % 2 == 0 and i > 5:
                    particle_size = max(1, int(3 * (1 - i/num_points)))
                    pygame.draw.circle(
                        boost_surface,
                        (r, g, b, opacity//2),
                        flame_points[i],
                        particle_size
                    )
        
        surface.blit(boost_surface, (0, 0))
    
    def _draw_head_details(self, surface, camera_x, camera_y):
        head = self.segments[0]
        screen_head_x = int(head[0] - camera_x)
        screen_head_y = int(head[1] - camera_y)
        
        if not (0 <= screen_head_x <= WINDOW_WIDTH and 0 <= screen_head_y <= WINDOW_HEIGHT):
            return
        
        eye_offset = 4
        eye_radius = 3.5
        eye_color = WHITE
        
        eye1_x = screen_head_x + eye_offset * math.cos(self.angle - 0.4)
        eye1_y = screen_head_y + eye_offset * math.sin(self.angle - 0.4)
        eye2_x = screen_head_x + eye_offset * math.cos(self.angle + 0.4)
        eye2_y = screen_head_y + eye_offset * math.sin(self.angle + 0.4)
        
        pygame.draw.circle(surface, eye_color, (int(eye1_x), int(eye1_y)), eye_radius)
        pygame.draw.circle(surface, eye_color, (int(eye2_x), int(eye2_y)), eye_radius)
        
        pupil_radius = 1.5
        pupil_color = BLACK
        
        pupil1_x = eye1_x + 1 * math.cos(self.angle)
        pupil1_y = eye1_y + 1 * math.sin(self.angle)
        pupil2_x = eye2_x + 1 * math.cos(self.angle)
        pupil2_y = eye2_y + 1 * math.sin(self.angle)
        
        pygame.draw.circle(surface, pupil_color, (int(pupil1_x), int(pupil1_y)), pupil_radius)
        pygame.draw.circle(surface, pupil_color, (int(pupil2_x), int(pupil2_y)), pupil_radius)
        
        if len(self.segments) > 5:
            font = pygame.font.SysFont(UI_FONT, 14)
            text = str(self.score) if not self.is_player else "You: " + str(self.score)
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_head_x, screen_head_y - 25))
            surface.blit(text_surface, text_rect)
        
        if self.is_player:
            self._draw_boost_indicator(surface, screen_head_x, screen_head_y)
    
    def _draw_boost_indicator(self, surface, x, y):
        if self.boost_cooldown > 0:
            cooldown_percent = self.boost_cooldown / (BOOST_COOLDOWN * FPS)
            width = 36
            height = COOLDOWN_BAR_HEIGHT
            bar_x = x - width // 2
            bar_y = y - self.head_radius - 15
            
            pygame.draw.rect(
                surface, 
                COOLDOWN_BAR_BG_COLOR, 
                (bar_x, bar_y, width, height),
                0,
                COOLDOWN_BAR_BORDER_RADIUS
            )
            
            if cooldown_percent < 1:
                progress_width = int(width * (1-cooldown_percent))
                if progress_width > 0:
                    pygame.draw.rect(
                        surface, 
                        COOLDOWN_BAR_COLOR, 
                        (bar_x, bar_y, progress_width, height),
                        0,
                        COOLDOWN_BAR_BORDER_RADIUS
                    )
        elif len(self.segments) > BOOST_MIN_LENGTH:
            boost_icon_radius = 4
            boost_color = BOOST_EFFECT_COLOR[:3] if self.boosting else (220, 220, 220)
            
            pygame.draw.circle(
                surface,
                boost_color,
                (x, y - self.head_radius - 12),
                boost_icon_radius + (1 if self.boosting else 0)
            )
            
            if self.boosting:
                glow_surface = pygame.Surface((boost_icon_radius*6, boost_icon_radius*6), pygame.SRCALPHA)
                for r in range(boost_icon_radius*3, 0, -1):
                    alpha = max(0, int(120 * (r / (boost_icon_radius*3)) * (1 - r / (boost_icon_radius*3))))
                    pygame.draw.circle(
                        glow_surface,
                        (*BOOST_EFFECT_COLOR[:3], alpha),
                        (boost_icon_radius*3, boost_icon_radius*3),
                        r
                    )
                surface.blit(
                    glow_surface, 
                    (x - boost_icon_radius*3, y - self.head_radius - 12 - boost_icon_radius*3)
                )
    
    def get_head_position(self):
        return self.segments[0]
    
    def get_boost_status(self):
        can_boost = len(self.segments) > BOOST_MIN_LENGTH and self.boost_cooldown <= 0
        return {
            'boosting': self.boosting,
            'can_boost': can_boost,
            'cooldown': self.boost_cooldown,
            'cooldown_max': BOOST_COOLDOWN * FPS
        }
