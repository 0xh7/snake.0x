import pygame
import random
import math
import os
import json
from config import *
from snake import Snake
from food import FoodManager
from ai import AI
from effects import ParticleSystem, FloatingText

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(UI_FONT, SCORE_FONT_SIZE)
        
        if ENABLE_LOADING_SCREEN:
            self.show_loading_screen()
        
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        
        self.running = True
        self.game_over = False
        self.restart_timer = 0
        self.difficulty = 1.0
        self.time_played = 0
        self.in_menu = True
        self.selected_skin = 0
        self.menu_state = "main"
        
        
        
        self.particle_system = ParticleSystem()
        self.floating_text = FloatingText()
        
        self.player = None
        self.snakes = []
        self.food_manager = FoodManager()
        self.ai = AI(self)
        
        self.skins = SKINS
        
      
        
        self.scoreboard = self.load_scoreboard()
        
        self.minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        
        self.setup_new_game()

    def show_loading_screen(self):
        self.screen.fill(LOADING_SCREEN_BG_COLOR)
        
        loading_font = pygame.font.SysFont('Arial', 36)
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        title_text = title_font.render("Snake IO", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(title_text, title_rect)
        
        loading_text = loading_font.render("Loading...", True, LOADING_SCREEN_TEXT_COLOR)
        loading_rect = loading_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        self.screen.blit(loading_text, loading_rect)
        
        bar_width = 300
        bar_height = 10
        bar_x = (WINDOW_WIDTH - bar_width) // 2
        bar_y = WINDOW_HEIGHT//2 + 60
        
        pygame.draw.rect(self.screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height), 0, 5)
        
        pygame.display.flip()
        
        num_steps = 10
        for i in range(num_steps + 1):
            progress = i / num_steps
            
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, (80, 150, 255), (bar_x, bar_y, progress_width, bar_height), 0, 5)
            
            pygame.display.flip()
            
            pygame.time.delay(100)
    
    def create_grid_texture(self):
        texture_size = 200
        texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        texture.fill((0, 0, 0, 0))
        
        if MAP_DESIGN_STYLE == "modern":
            for i in range(0, texture_size, GRID_SIZE):
                pygame.draw.line(texture, (GRID_COLOR[0], GRID_COLOR[1], GRID_COLOR[2], 40), 
                                (i, 0), (i, texture_size), 1)
                pygame.draw.line(texture, (GRID_COLOR[0], GRID_COLOR[1], GRID_COLOR[2], 40), 
                                (0, i), (texture_size, i), 1)
                
            for x in range(0, texture_size, GRID_SIZE):
                for y in range(0, texture_size, GRID_SIZE):
                    pygame.draw.circle(texture, PATTERN_COLOR, (x, y), 2)
                    
        elif MAP_DESIGN_STYLE == "minimal":
            for x in range(0, texture_size, GRID_SIZE):
                for y in range(0, texture_size, GRID_SIZE):
                    pygame.draw.circle(texture, (PATTERN_COLOR[0], PATTERN_COLOR[1], PATTERN_COLOR[2], 120), (x, y), 1)
                    
        else:
            for i in range(0, texture_size, GRID_SIZE):
                pygame.draw.line(texture, GRID_COLOR, (i, 0), (i, texture_size), 1)
                pygame.draw.line(texture, GRID_COLOR, (0, i), (texture_size, i), 1)
        
        return texture
    
    def load_scoreboard(self):
        scoreboard_path = os.path.join(os.path.dirname(__file__), "scoreboard.json")
        try:
            if os.path.exists(scoreboard_path):
                with open(scoreboard_path, 'r') as f:
                    return json.load(f)
            else:
                return []
        except:
            return []
            
    def save_scoreboard(self):
        scoreboard_path = os.path.join(os.path.dirname(__file__), "scoreboard.json")
        try:
            with open(scoreboard_path, 'w') as f:
                json.dump(self.scoreboard, f)
        except:
            pass
    
    def add_score_to_board(self, score):
        time_bonus = int(self.time_played * 0.5)
        difficulty_multiplier = self.difficulty * 1.2
        
        final_score = int(score * difficulty_multiplier) + time_bonus
        
        self.scoreboard.append(final_score)
        self.scoreboard.sort(reverse=True)
        if len(self.scoreboard) > SCOREBOARD_ENTRIES:
            self.scoreboard = self.scoreboard[:SCOREBOARD_ENTRIES]
        self.save_scoreboard()
        
        return final_score
    
    def setup_new_game(self):
        self.game_over = False
        self.time_played = 0
        self.difficulty = 1.0
        
        player_x = WORLD_WIDTH // 2
        player_y = WORLD_HEIGHT // 2
        self.player = Snake(player_x, player_y, GREEN, is_player=True, skin_index=self.selected_skin)
        
        self.player.set_skin(self.selected_skin)
        
        self.target_camera_x = player_x - WINDOW_WIDTH // 2
        self.target_camera_y = player_y - WINDOW_HEIGHT // 2
        self.camera_x = self.target_camera_x
        self.camera_y = self.target_camera_y
        
        self.snakes = [self.player]
        self.spawn_ai_snakes(NUM_AI_SNAKES)
        
        self.food_manager = FoodManager()
    
    def spawn_ai_snakes(self, count):
        player_x, player_y = self.player.get_head_position()
        
        for _ in range(count):
            while True:
                x = random.randint(100, WORLD_WIDTH - 100)
                y = random.randint(100, WORLD_HEIGHT - 100)
                dist = math.sqrt((x - player_x)**2 + (y - player_y)**2)
                if dist > 300:
                    break
            self.snakes.append(Snake(x, y))
    

    
    def handle_menu_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.menu_state == "main":
                        self.running = False
                    else:
                        self.menu_state = "main"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
        
        if self.menu_state == "main":
            play_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50, 200, 50)
            if play_button.collidepoint(mouse_pos):
                if mouse_clicked:
                    self.in_menu = False
                    
            skin_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 20, 200, 50)
            if skin_button.collidepoint(mouse_pos):
                if mouse_clicked:
                    self.menu_state = "skins"
                    
        elif self.menu_state == "skins":
            skin_grid_cols = 3
            skin_width = 140
            skin_height = 100
            spacing = 20
            start_x = (WINDOW_WIDTH - (skin_grid_cols * skin_width + (skin_grid_cols-1) * spacing)) // 2
            start_y = 150
            
            for i, skin in enumerate(self.skins):
                row = i // skin_grid_cols
                col = i % skin_grid_cols
                x = start_x + col * (skin_width + spacing)
                y = start_y + row * (skin_height + spacing)
                
                skin_rect = pygame.Rect(x, y, skin_width, skin_height)
                if skin_rect.collidepoint(mouse_pos) and mouse_clicked:
                    self.selected_skin = i
                    if self.player:
                        self.player.set_skin(i)
    
    def draw_menu(self):
        self.screen.fill(MENU_BACKGROUND_COLOR)
        
        title_font = pygame.font.SysFont(UI_FONT, 72, bold=True)
        title_text = title_font.render("Snake IO", True, WHITE)
        shadow_text = title_font.render("Snake IO", True, MENU_ACCENT_COLOR)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title_text, title_rect)
        
        if self.menu_state == "main":
            self._draw_main_menu()
        elif self.menu_state == "skins":
            self._draw_skins_menu()
        
        pygame.display.flip()
    
    def _draw_main_menu(self):
        button_font = pygame.font.SysFont(UI_FONT, 32)
        info_font = pygame.font.SysFont(UI_FONT, 16)
        
        play_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, play_button, border_radius=10)
        pygame.draw.rect(self.screen, MENU_ACCENT_COLOR, play_button, 2, border_radius=10)
        
        play_text = button_font.render("PLAY", True, BUTTON_TEXT_COLOR)
        play_rect = play_text.get_rect(center=play_button.center)
        self.screen.blit(play_text, play_rect)
        
        skin_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 20, 200, 50)
        pygame.draw.rect(self.screen, BUTTON_COLOR, skin_button, border_radius=10)
        pygame.draw.rect(self.screen, MENU_ACCENT_COLOR, skin_button, 2, border_radius=10)
        
        skin_text = button_font.render("SKINS", True, BUTTON_TEXT_COLOR)
        skin_rect = skin_text.get_rect(center=skin_button.center)
        self.screen.blit(skin_text, skin_rect)
        
        instruction_text = info_font.render("WASD or Arrows to move | Space to boost | Esc to exit", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 40))
        self.screen.blit(instruction_text, instruction_rect)
        
        if self.player:
            preview_x = WINDOW_WIDTH//2
            preview_y = WINDOW_HEIGHT - 120
            self._draw_snake_preview(preview_x, preview_y, self.selected_skin)
    
    def _draw_skins_menu(self):
        title_font = pygame.font.SysFont(UI_FONT, 36, bold=True)
        button_font = pygame.font.SysFont(UI_FONT, 24)
        
        title_shadow = title_font.render("Choose Snake Skin", True, (40, 60, 100))
        title_text = title_font.render("Choose Snake Skin", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_text, title_rect)
        
        back_button = pygame.Rect(40, 40, 100, 40)
        back_button_hover = back_button.collidepoint(pygame.mouse.get_pos())
        back_color = BUTTON_HOVER_COLOR if back_button_hover else BUTTON_COLOR
        
        pygame.draw.rect(self.screen, (20, 30, 60), 
                        (back_button.x + 3, back_button.y + 3, back_button.width, back_button.height), 
                        border_radius=8)
        pygame.draw.rect(self.screen, back_color, back_button, border_radius=8)
        pygame.draw.rect(self.screen, MENU_ACCENT_COLOR, back_button, 2, border_radius=8)
        
        back_text = button_font.render("BACK", True, BUTTON_TEXT_COLOR)
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)
        
        if back_button_hover and pygame.mouse.get_pressed()[0]:
            self.menu_state = "main"
        
        skin_grid_cols = 3
        skin_width = 140
        skin_height = 120
        spacing = 20
        start_x = (WINDOW_WIDTH - (skin_grid_cols * skin_width + (skin_grid_cols-1) * spacing)) // 2
        start_y = 130
        
        for i, skin in enumerate(self.skins):
            row = i // skin_grid_cols
            col = i % skin_grid_cols
            x = start_x + col * (skin_width + spacing)
            y = start_y + row * (skin_height + spacing)
            
            skin_rect = pygame.Rect(x, y, skin_width, skin_height)
            shadow_rect = pygame.Rect(x + 3, y + 3, skin_width, skin_height)
            
            pygame.draw.rect(self.screen, (15, 20, 35), shadow_rect, border_radius=10)
            
            pygame.draw.rect(self.screen, (25, 30, 45), skin_rect, border_radius=10)
            
            border_color = MENU_ACCENT_COLOR if i == self.selected_skin else (60, 70, 90)
            border_width = 3 if i == self.selected_skin else 1
            pygame.draw.rect(self.screen, border_color, skin_rect, border_width, border_radius=10)
            
            name_shadow = button_font.render(skin["name"], True, (20, 20, 30))
            name_text = button_font.render(skin["name"], True, WHITE)
            name_rect = name_text.get_rect(centerx=x + skin_width//2, y=y + skin_height - 22)
            
            if i == self.selected_skin:
                selected_font = pygame.font.SysFont(UI_FONT, 14)
                selected_text = selected_font.render("SELECTED", True, (80, 200, 120))
                selected_rect = selected_text.get_rect(centerx=x + skin_width//2, y=y + skin_height - 40)
                self.screen.blit(selected_text, selected_rect)
            
            self.screen.blit(name_shadow, (name_rect.x + 1, name_rect.y + 1))
            self.screen.blit(name_text, name_rect)
            
            self._draw_snake_preview(x + skin_width//2, y + skin_height//2 - 15, i)
    
    def _draw_snake_preview(self, x, y, skin_index):
        preview_snake = Snake(0, 0, skin_index=skin_index)
        
        preview_snake.color_cycle_timer = 0
        
        preview_snake.set_skin(skin_index)
        
        for i in range(preview_snake.MAX_SEGMENTS):
            preview_snake.segment_colors[i] = preview_snake._compute_static_color(i)
        
        segments = []
        segment_radius = 8
        head_radius = 10
        
        for i in range(12):
            if i < 6:
                offset_x = i * segment_radius * 1.3
                offset_y = -math.sin(i * 0.5) * segment_radius * 2.2
            else:
                offset_x = (i-6) * segment_radius * 1.3
                offset_y = math.sin((i-6) * 0.5) * segment_radius * 2.2 + segment_radius * 4.5
            segments.append([x + offset_x - segment_radius * 4, y + offset_y])
        
        preview_snake.segments = segments
        
        for i in range(len(segments) - 1, -1, -1):
            segment = segments[i]
            segment_color = preview_snake.segment_colors[i]
            
            radius = head_radius if i == 0 else segment_radius
            
            pygame.draw.circle(self.screen, segment_color, (int(segment[0]), int(segment[1])), radius)
            
            if i > 0 and preview_snake.skin["pattern"] != "solid" and i % 3 == 0:
                pattern_radius = int(radius * 0.7)
                darker_color = tuple(max(0, c - 50) for c in segment_color)
                pygame.draw.circle(self.screen, darker_color, (int(segment[0]), int(segment[1])), pattern_radius)
        
        head = segments[0]
        eye_offset = 3
        pygame.draw.circle(self.screen, WHITE, (int(head[0]) + eye_offset, int(head[1]) - eye_offset), 3)
        pygame.draw.circle(self.screen, WHITE, (int(head[0]) + eye_offset, int(head[1]) + eye_offset), 3)
        pygame.draw.circle(self.screen, BLACK, (int(head[0]) + eye_offset + 1, int(head[1]) - eye_offset), 1.5)
        pygame.draw.circle(self.screen, BLACK, (int(head[0]) + eye_offset + 1, int(head[1]) + eye_offset), 1.5)
        
        pygame.draw.circle(self.screen, (255, 255, 255, 150), (int(head[0]) - 2, int(head[1]) - 2), 2)
    
    def restart_game(self):
        self.game_over = False
        self.time_played = 0
        self.difficulty = 1.0
        
        player_x = WORLD_WIDTH // 2
        player_y = WORLD_HEIGHT // 2
        self.player = Snake(player_x, player_y, GREEN, is_player=True)
        
        self.target_camera_x = player_x - WINDOW_WIDTH // 2
        self.target_camera_y = player_y - WINDOW_HEIGHT // 2
        self.camera_x = self.target_camera_x
        self.camera_y = self.target_camera_y
        
        self.snakes = [self.player]
        for _ in range(NUM_AI_SNAKES):
            while True:
                x = random.randint(100, WORLD_WIDTH - 100)
                y = random.randint(100, WORLD_HEIGHT - 100)
                dist = math.sqrt((x - player_x)**2 + (y - player_y)**2)
                if dist > 300:
                    break
            self.snakes.append(Snake(x, y))
        
        self.food_manager = FoodManager()
    
    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    self.menu_state = "main"
                elif event.key == pygame.K_r and self.game_over:
                    self.setup_new_game()
                    self.game_over = False
                elif event.key == pygame.K_SPACE:
                    if self.player.alive:
                        self.player.toggle_boost(True)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if self.player.alive:
                        self.player.toggle_boost(False)
        
        if not self.game_over and self.player.alive:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            head_x, head_y = self.player.get_head_position()
            
            world_mouse_x = mouse_x + self.camera_x
            world_mouse_y = mouse_y + self.camera_y
            
            dx = world_mouse_x - head_x
            dy = world_mouse_y - head_y
            
            if dx != 0 or dy != 0:
                angle = math.atan2(dy, dx)
                self.player.set_direction(angle)
            
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                self.player.toggle_boost(True)
            else:
                self.player.toggle_boost(False)
    
    def update_game(self):
        if self.game_over:
            self.restart_timer += 1
            if self.restart_timer > FPS * 3:
                self.restart_game()
            return
        
        self.particle_system.update(1/FPS)
        self.floating_text.update(1/FPS)
        
        self.time_played += 1 / FPS
        self.difficulty = min(MAX_DIFFICULTY, 1.0 + self.time_played * DIFFICULTY_INCREASE_RATE)
        
        snake_positions = [snake.segments for snake in self.snakes if snake.alive]
        
        self.food_manager.update(snake_positions)
        
        if self.player.alive:
            head_x, head_y = self.player.get_head_position()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            look_ahead_x = (mouse_x - WINDOW_WIDTH/2) * 0.3
            look_ahead_y = (mouse_y - WINDOW_HEIGHT/2) * 0.3
            
            self.target_camera_x = head_x - WINDOW_WIDTH // 2 + look_ahead_x
            self.target_camera_y = head_y - WINDOW_WIDTH // 2 + look_ahead_y
            
            self.camera_x += (self.target_camera_x - self.camera_x) * CAMERA_SMOOTHING
            self.camera_y += (self.target_camera_y - self.camera_y) * CAMERA_SMOOTHING
            
            self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - WINDOW_WIDTH))
            self.camera_y = max(0, min(self.camera_y, WORLD_HEIGHT - WINDOW_HEIGHT))
        
        for snake in self.snakes:
            if snake != self.player and snake.alive:
                self.ai.update_snake(snake, self.snakes, self.food_manager.foods)
        
        all_dropped_segments = []
        
        for snake in self.snakes:
            if snake.alive:
                dropped_segments, score_reduced = snake.move()
                
                if snake == self.player and score_reduced:
                    head_x, head_y = snake.get_head_position()
                    self.floating_text.add_text(head_x, head_y - 30, "-1", color=(255, 100, 100), size=16)
                
                if dropped_segments and len(dropped_segments) > 0:
                    for segment in dropped_segments:
                        all_dropped_segments.append((segment, snake.color))
        
        for segment_data in all_dropped_segments:
            segment, color = segment_data
            self.food_manager.add_food_at_position(segment[0], segment[1], BOOST_FOOD_SIZE, color)
        
        self.check_collisions()
        
        self.respawn_ai_snakes()
        
        if not self.player.alive and not self.game_over:
            head_x, head_y = self.player.get_head_position()
            self.particle_system.add_explosion(head_x, head_y, self.player.color)
            
            final_score = self.add_score_to_board(self.player.score)
            
            self.final_score = final_score
            
            self.game_over = True
            self.restart_timer = 0
    
    def respawn_ai_snakes(self):
        alive_ai = sum(1 for snake in self.snakes if snake != self.player and snake.alive)
        if alive_ai < NUM_AI_SNAKES // 2:
            for _ in range(min(2, NUM_AI_SNAKES - alive_ai)):
                while True:
                    x = random.randint(100, WORLD_WIDTH - 100)
                    y = random.randint(100, WORLD_HEIGHT - 100)
                    if (x < self.camera_x - 100 or x > self.camera_x + WINDOW_WIDTH + 100 or
                        y < self.camera_y - 100 or y > self.camera_y + WINDOW_HEIGHT + 100):
                        break
                self.snakes.append(Snake(x, y))
    
    def check_collisions(self):
        all_dropped_food = []
        
        for snake in self.snakes:
            if snake.alive and snake.check_boundary_collision(WORLD_WIDTH, WORLD_HEIGHT):
                head_x, head_y = snake.get_head_position()
                self.particle_system.add_explosion(head_x, head_y, snake.color)
                
                dropped_food = snake.die()
                all_dropped_food.extend(dropped_food)
                
                if snake == self.player:
                    print("Player died: Hit the boundary")
        
        for i, snake1 in enumerate(self.snakes):
            if not snake1.alive:
                continue
            
            if snake1.check_self_collision():
                dropped_food = snake1.die()
                all_dropped_food.extend(dropped_food)
                if snake1 == self.player:
                    print("Player died: Self collision")
                continue
            
            for j, snake2 in enumerate(self.snakes):
                if i != j and snake2.alive:
                    if snake1.check_snake_collision(snake2):
                        dropped_food = snake1.die()
                        all_dropped_food.extend(dropped_food)
                        
                        bonus_points = len(snake1.segments) // 5
                        if bonus_points > 0:
                            snake2.score += bonus_points
                        
                        if snake1 == self.player:
                            print(f"Player died: Collision with snake {j}")
                        break
        
        for food_x, food_y, value in all_dropped_food:
            self.food_manager.add_food_at_position(food_x, food_y, value)
        
        for snake in self.snakes:
            if not snake.alive:
                continue
                
            head_x, head_y = snake.get_head_position()
            value = self.food_manager.check_collision(head_x, head_y, snake.head_radius)
            
            if value > 0:
                self.particle_system.add_food_sparkle(head_x, head_y, snake.color)
                
                if snake == self.player:
                    points_text = f"+{value * GROWTH_PER_FOOD}"
                    self.floating_text.add_text(head_x, head_y - 20, points_text, color=snake.color, size=18)
                
                snake.grow(value * GROWTH_PER_FOOD)
    
    def world_to_screen(self, x, y):
        return x - self.camera_x, y - self.camera_y
    
    def draw_grid(self):
        offset_x = int(-(self.camera_x % GRID_SIZE))
        offset_y = int(-(self.camera_y % GRID_SIZE))
        
        for x in range(offset_x, WINDOW_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(offset_y, WINDOW_HEIGHT + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
    
    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        offset_x = int(-(self.camera_x % GRID_SIZE))
        offset_y = int(-(self.camera_y % GRID_SIZE))
        
        grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        for x in range(offset_x, WINDOW_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(grid_surface, (*GRID_COLOR, 180), (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(offset_y, WINDOW_HEIGHT + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(grid_surface, (*GRID_COLOR, 180), (0, y), (WINDOW_WIDTH, y), 1)
        
        self.screen.blit(grid_surface, (0, 0))
        
        if BACKGROUND_PATTERN:
            seed = int(self.camera_x + self.camera_y) // 100
            random.seed(seed)
            pattern_style = BACKGROUND_PATTERN_STYLE
            
            pattern_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            
            for _ in range(MAP_DECORATION_DENSITY):
                try:
                    pattern_x = random.randint(0, WINDOW_WIDTH)
                    pattern_y = random.randint(0, WINDOW_HEIGHT)
                    
                    if pattern_style == "dots":
                        size = random.randint(1, 2)
                        alpha = random.randint(20, 40)
                        color = (*PATTERN_COLOR, alpha)
                        pygame.draw.circle(pattern_surface, color, (pattern_x, pattern_y), size)
                except Exception:
                    pass
            
            self.screen.blit(pattern_surface, (0, 0))
            
            random.seed()
    
    def draw_boundary(self):
        x1, y1 = self.world_to_screen(0, 0)
        x2, y2 = self.world_to_screen(WORLD_WIDTH, WORLD_HEIGHT)
        
        boundary_glow = 3
        
        if x1 >= -boundary_glow and x1 <= WINDOW_WIDTH + boundary_glow:
            for i in range(boundary_glow, 0, -1):
                alpha = 200 - (i * 50)
                pygame.draw.line(self.screen, (*MAP_BORDER_COLOR, alpha), 
                                (x1-i, max(0, y1)), (x1-i, min(WINDOW_HEIGHT, y2)), 1)
            pygame.draw.line(self.screen, MAP_BORDER_COLOR, 
                            (x1, max(0, y1)), (x1, min(WINDOW_HEIGHT, y2)), 
                            BOUNDARY_WIDTH)
            
            for y in range(max(0, int(y1)), min(WINDOW_HEIGHT, int(y2)), 100):
                border_dot_color = (255, 50, 50) if y % 200 == 0 else MAP_BORDER_COLOR
                pygame.draw.circle(self.screen, border_dot_color, (x1, y), BOUNDARY_WIDTH + 2)
                
                if y % 50 == 0 and y % 200 != 0 and y % 100 != 0:
                    pygame.draw.circle(self.screen, MAP_BORDER_COLOR, (x1, y), BOUNDARY_WIDTH)
        
        if x2 >= -boundary_glow and x2 <= WINDOW_WIDTH + boundary_glow:
            for i in range(boundary_glow, 0, -1):
                alpha = 200 - (i * 50)
                pygame.draw.line(self.screen, (*MAP_BORDER_COLOR, alpha), 
                                (x2+i, max(0, y1)), (x2+i, min(WINDOW_HEIGHT, y2)), 1)
            pygame.draw.line(self.screen, MAP_BORDER_COLOR, 
                            (x2, max(0, y1)), (x2, min(WINDOW_HEIGHT, y2)), 
                            BOUNDARY_WIDTH)
            
            for y in range(max(0, int(y1)), min(WINDOW_HEIGHT, int(y2)), 100):
                border_dot_color = (255, 50, 50) if y % 200 == 0 else MAP_BORDER_COLOR
                pygame.draw.circle(self.screen, border_dot_color, (x2, y), BOUNDARY_WIDTH + 2)
                if y % 50 == 0 and y % 200 != 0 and y % 100 != 0:
                    pygame.draw.circle(self.screen, MAP_BORDER_COLOR, (x2, y), BOUNDARY_WIDTH)
        
        if y1 >= -boundary_glow and y1 <= WINDOW_HEIGHT + boundary_glow:
            for i in range(boundary_glow, 0, -1):
                alpha = 200 - (i * 50)
                pygame.draw.line(self.screen, (*MAP_BORDER_COLOR, alpha), 
                                (max(0, x1), y1-i), (min(WINDOW_WIDTH, x2), y1-i), 1)
            pygame.draw.line(self.screen, MAP_BORDER_COLOR, 
                            (max(0, x1), y1), (min(WINDOW_WIDTH, x2), y1), 
                            BOUNDARY_WIDTH)
            
            for x in range(max(0, int(x1)), min(WINDOW_WIDTH, int(x2)), 100):
                border_dot_color = (255, 50, 50) if x % 200 == 0 else MAP_BORDER_COLOR
                pygame.draw.circle(self.screen, border_dot_color, (x, y1), BOUNDARY_WIDTH + 2)
                if x % 50 == 0 and x % 200 != 0 and x % 100 != 0:
                    pygame.draw.circle(self.screen, MAP_BORDER_COLOR, (x, y1), BOUNDARY_WIDTH)
        
        if y2 >= -boundary_glow and y2 <= WINDOW_HEIGHT + boundary_glow:
            for i in range(boundary_glow, 0, -1):
                alpha = 200 - (i * 50)
                pygame.draw.line(self.screen, (*MAP_BORDER_COLOR, alpha), 
                                (max(0, x1), y2+i), (min(WINDOW_WIDTH, x2), y2+i), 1)
            pygame.draw.line(self.screen, MAP_BORDER_COLOR, 
                            (max(0, x1), y2), (min(WINDOW_WIDTH, x2), y2), 
                            BOUNDARY_WIDTH)
            
            for x in range(max(0, int(x1)), min(WINDOW_WIDTH, int(x2)), 100):
                border_dot_color = (255, 50, 50) if x % 200 == 0 else MAP_BORDER_COLOR
                pygame.draw.circle(self.screen, border_dot_color, (x, y2), BOUNDARY_WIDTH + 2)
                if x % 50 == 0 and x % 200 != 0 and x % 100 != 0:
                    pygame.draw.circle(self.screen, MAP_BORDER_COLOR, (x, y2), BOUNDARY_WIDTH)
    
    def draw_minimap(self):
        self.minimap_surface.fill((0, 0, 0, 0))
        
        minimap_rect = pygame.Rect(0, 0, MINIMAP_SIZE, MINIMAP_SIZE)
        minimap_bg = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE), pygame.SRCALPHA)
        minimap_bg.fill((0, 0, 0, MINIMAP_OPACITY))
        self.minimap_surface.blit(minimap_bg, (0, 0))
        
        scale_x = MINIMAP_SIZE / WORLD_WIDTH
        scale_y = MINIMAP_SIZE / WORLD_HEIGHT
        
        grid_spacing = 40 * scale_x
        for x in range(0, MINIMAP_SIZE, int(grid_spacing)):
            pygame.draw.line(self.minimap_surface, (50, 50, 60, 100), (x, 0), (x, MINIMAP_SIZE), 1)
        for y in range(0, MINIMAP_SIZE, int(grid_spacing)):
            pygame.draw.line(self.minimap_surface, (50, 50, 60, 100), (0, y), (MINIMAP_SIZE, y), 1)
        
        pygame.draw.rect(self.minimap_surface, MAP_BORDER_COLOR, (0, 0, MINIMAP_SIZE, MINIMAP_SIZE), 2)
        
        view_x = int(self.camera_x * scale_x)
        view_y = int(self.camera_y * scale_y)
        view_width = int(WINDOW_WIDTH * scale_x)
        view_height = int(WINDOW_HEIGHT * scale_y)
        pygame.draw.rect(self.minimap_surface, WHITE, (view_x, view_y, view_width, view_height), 1)
        
        for snake in self.snakes:
            if not snake.alive:
                continue
            positions = snake.segments
            
            if len(positions) > 1:
                for i in range(1, min(len(positions), 15)):
                    pos = positions[i]
                    map_x = int(pos[0] * scale_x)
                    map_y = int(pos[1] * scale_y)
                    size = max(1, 3 - i // 5)
                    alpha = max(50, 200 - i * 10)
                    if 0 <= map_x <= MINIMAP_SIZE and 0 <= map_y <= MINIMAP_SIZE:
                        if snake == self.player:
                            color = (255, 255, 255, alpha)
                        else:
                            r, g, b = snake.color
                            color = (r, g, b, alpha)
                        
                        dot_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                        pygame.draw.circle(dot_surface, color, (size, size), size)
                        self.minimap_surface.blit(dot_surface, (map_x-size, map_y-size))
            
            head_x, head_y = snake.get_head_position()
            map_x = int(head_x * scale_x)
            map_y = int(head_y * scale_y)
            
            color = snake.color
            if snake == self.player:
                color = WHITE
                size = 4
            else:
                size = 3
                
            pygame.draw.circle(self.minimap_surface, color, (map_x, map_y), size)
        
        for food in self.food_manager.foods:
            map_x = int(food.x * scale_x)
            map_y = int(food.y * scale_y)
            if 0 <= map_x <= MINIMAP_SIZE and 0 <= map_y <= MINIMAP_SIZE:
                size = 1 if food.value == 1 else 2
                pygame.draw.circle(self.minimap_surface, food.color, (map_x, map_y), size)
        
        border_width = 2
        border_rect = pygame.Rect(
            MINIMAP_POSITION[0] - border_width,
            MINIMAP_POSITION[1] - border_width,
            MINIMAP_SIZE + border_width * 2,
            MINIMAP_SIZE + border_width * 2
        )
        pygame.draw.rect(self.screen, (60, 60, 70), border_rect, border_width, border_radius=5)
        self.screen.blit(self.minimap_surface, MINIMAP_POSITION)
    
    def draw_game(self):
        self.draw_background()
        self.draw_boundary()
        self.food_manager.draw(self.screen, self.camera_x, self.camera_y, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.particle_system.draw(self.screen, self.camera_x, self.camera_y)
        
        if self.player.alive:
            self.draw_danger_indicators()
        for snake in sorted(self.snakes, key=lambda s: 1 if s == self.player else 0):
            if snake.alive:
                snake.draw(self.screen, self.camera_x, self.camera_y)
        
        self.floating_text.draw(self.screen, self.camera_x, self.camera_y)
        self.draw_minimap()
        
        self.draw_scores()
        self.draw_snake_stats()
        self.draw_controls()
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_scores(self):
        if self.player.alive:
            score_text = f"Score: {self.player.score}"
            text_surface = self.font.render(score_text, True, WHITE)
            self.screen.blit(text_surface, (WINDOW_WIDTH - 150, 20))
            
            time_text = f"Time: {int(self.time_played)}s"
            time_surface = self.font.render(time_text, True, WHITE)
            self.screen.blit(time_surface, (WINDOW_WIDTH - 150, 50))
        
        alive_ai = [s for s in self.snakes if s != self.player and s.alive]
        top_ai = sorted(alive_ai, key=lambda s: s.score, reverse=True)[:3]
        
        for i, ai in enumerate(top_ai):
            ai_text = f"AI #{i+1}: {ai.score}"
            text_surface = self.font.render(ai_text, True, ai.color)
            self.screen.blit(text_surface, (WINDOW_WIDTH - 150, 80 + i * 30))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_font = pygame.font.SysFont('Arial', 64)
        text_surface = game_over_font.render("GAME OVER", True, RED)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        self.screen.blit(text_surface, text_rect)
        
        score_font = pygame.font.SysFont('Arial', 36)
        
        base_score = self.player.score
        base_score_text = f"Base Score: {base_score}"
        base_score_surface = score_font.render(base_score_text, True, WHITE)
        base_score_rect = base_score_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4 + 60))
        self.screen.blit(base_score_surface, base_score_rect)
        
        time_bonus = int(self.time_played * 0.5)
        time_bonus_text = f"Time Bonus: +{time_bonus}"
        time_bonus_surface = score_font.render(time_bonus_text, True, (100, 255, 100))
        time_bonus_rect = time_bonus_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4 + 100))
        self.screen.blit(time_bonus_surface, time_bonus_rect)
        
        final_score_text = f"FINAL SCORE: {self.final_score}"
        final_score_surface = score_font.render(final_score_text, True, YELLOW)
        final_score_rect = final_score_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4 + 150))
        self.screen.blit(final_score_surface, final_score_rect)
        
        high_score_font = pygame.font.SysFont('Arial', 28)
        title_surface = high_score_font.render("HIGH SCORES", True, YELLOW)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.screen.blit(title_surface, title_rect)
        
        for i, score in enumerate(self.scoreboard[:5]):
            score_text = f"#{i+1}: {score}"
            color = YELLOW if i == 0 else WHITE
            hs_surface = high_score_font.render(score_text, True, color)
            hs_rect = hs_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90 + i * 30))
            self.screen.blit(hs_surface, hs_rect)
        
        restart_font = pygame.font.SysFont('Arial', 24)
        restart_surface = restart_font.render("Press R to restart", True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 80))
        self.screen.blit(restart_surface, restart_rect)
    
    def draw_danger_indicators(self):
        if not self.player.alive:
            return
            
        player_head_x, player_head_y = self.player.get_head_position()
        player_angle = self.player.angle
        
        for snake in self.snakes:
            if snake is self.player or not snake.alive:
                continue
                
            snake_head_x, snake_head_y = snake.get_head_position()
            
            distance = math.sqrt((player_head_x - snake_head_x)**2 + (player_head_y - snake_head_y)**2)
            
            danger_distance = 200
            if distance < danger_distance:
                dx = snake_head_x - player_head_x
                dy = snake_head_y - player_head_y
                angle_to_danger = math.atan2(dy, dx)
                
                danger_is_behind = abs(math.sin(angle_to_danger - player_angle)) > 0.7
                
                if danger_is_behind:
                    screen_x, screen_y = self.world_to_screen(player_head_x, player_head_y)
                    
                    warning_distance = 100
                    warning_x = screen_x + math.cos(angle_to_danger) * warning_distance
                    warning_y = screen_y + math.sin(angle_to_danger) * warning_distance
                    
                    margin = 50
                    warning_x = max(margin, min(warning_x, WINDOW_WIDTH - margin))
                    warning_y = max(margin, min(warning_y, WINDOW_HEIGHT - margin))
                    
                    warning_radius = int(12 * (1 - distance/danger_distance))
                    warning_surface = pygame.Surface((warning_radius*2, warning_radius*2), pygame.SRCALPHA)
                    
                    pygame.draw.circle(
                        warning_surface,
                        DANGER_WARNING_COLOR,
                        (warning_radius, warning_radius),
                        warning_radius
                    )
                    
                    arrow_points = [
                        (warning_radius, 0),
                        (warning_radius*2, warning_radius),
                        (warning_radius, warning_radius*2),
                        (0, warning_radius)
                    ]
                    
                    rotated_surface = pygame.transform.rotate(
                        warning_surface,
                        -math.degrees(angle_to_danger) + 90
                    )
                    
                    self.screen.blit(
                        rotated_surface,
                        (warning_x - rotated_surface.get_width()//2, warning_y - rotated_surface.get_height()//2)
                    )
    
    def draw_controls(self):
        if self.player.alive and not self.game_over:
            instructions = [
                "Move: Mouse",
                "Boost: Space/Left Click",
                "Exit: ESC"
            ]
            
            text_y = WINDOW_HEIGHT - 80
            control_font = pygame.font.SysFont('Arial', 16)
            for instruction in instructions:
                text_surface = control_font.render(instruction, True, (200, 200, 200))
                self.screen.blit(text_surface, (20, text_y))
                text_y += 20
            
            boost_status = self.player.get_boost_status()
            if boost_status['boosting']:
                status = "BOOST ACTIVE"
                color = (255, 255, 0)
            elif boost_status['can_boost']:
                status = "Boost Ready"
                color = (200, 200, 200)
            else:
                status = f"Boost: Cooling down..."
                color = (150, 150, 150)
            
            status_surface = control_font.render(status, True, color)
            self.screen.blit(status_surface, (20, WINDOW_HEIGHT - 100))
    
    def draw_snake_stats(self):
        if not self.player.alive:
            return
        
        info_height = 30
        info_surface = pygame.Surface((WINDOW_WIDTH, info_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 120))
        
        alive_count = sum(1 for snake in self.snakes if snake.alive)
        
        info_font = pygame.font.SysFont(UI_FONT, 16)
        player_length = len(self.player.segments)
        
        stats_text = f"Length: {player_length} | Snakes Alive: {alive_count}/{len(self.snakes)} | Food: {len(self.food_manager.foods)}/{MAX_FOOD_ITEMS}"
        text_surface = info_font.render(stats_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, info_height//2))
        
        info_surface.blit(text_surface, text_rect)
        self.screen.blit(info_surface, (0, WINDOW_HEIGHT - info_height))
    
    def run(self):
        while self.running:
            if self.in_menu:
                self.handle_menu_events()
                self.draw_menu()
            else:
                self.handle_game_events()
                self.update_game()
                self.draw_game()
                
            self.clock.tick(FPS)
        
        pygame.quit()