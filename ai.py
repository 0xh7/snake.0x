import math
import random
from config import *

class AI:
    def __init__(self, game):
        self.game = game
    
    def update_snake(self, snake, all_snakes, foods):
        if not snake.alive:
            return
            
        snake.decision_counter += 1
        if snake.decision_counter < AI_DECISION_RATE:
            angle_diff = snake.target_angle - snake.angle
            if abs(angle_diff) > 0.1:
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                turn_rate = 0.05
                if angle_diff > 0:
                    snake.angle += min(turn_rate, angle_diff)
                else:
                    snake.angle -= min(turn_rate, -angle_diff)
                    
            self.handle_ai_boost(snake, all_snakes, foods)
            return
        
        snake.decision_counter = 0
        head_x, head_y = snake.get_head_position()
        
        strategy = self.choose_strategy(snake, all_snakes, foods)
        
        if strategy == 'hunt_food':
            target_x, target_y = self.hunt_food_strategy(snake, foods)
        elif strategy == 'attack':
            target_x, target_y = self.attack_strategy(snake, all_snakes)
        elif strategy == 'encircle':
            target_x, target_y = self.encircle_strategy(snake, all_snakes)
        elif strategy == 'target_player':
            target_x, target_y = self.target_player_strategy(snake, all_snakes)
        else:
            target_x, target_y = self.evasion_strategy(snake, all_snakes)
        
        dx = target_x - head_x
        dy = target_y - head_y
        
        if dx != 0 or dy != 0:
            base_angle = math.atan2(dy, dx)
            
            randomness = 0.15 / (1 + len(snake.segments) * 0.01)
            snake.target_angle = base_angle + random.uniform(-randomness, randomness)
        
        self.handle_ai_boost(snake, all_snakes, foods)

    def choose_strategy(self, snake, all_snakes, foods):
        head_x, head_y = snake.get_head_position()
        snake_size = len(snake.segments)
        
        player_snake = None
        for other_snake in all_snakes:
            if other_snake.is_player and other_snake.alive:
                player_snake = other_snake
                break
        
        if (player_snake and snake_size > 30 and 
                random.random() < AI_TARGET_PLAYER_CHANCE):
            player_head_x, player_head_y = player_snake.get_head_position()
            distance_to_player = math.sqrt((head_x - player_head_x)**2 + (head_y - player_head_y)**2)
            
            if (distance_to_player < 400 and 
                    len(snake.segments) > len(player_snake.segments) * 1.2):
                return 'target_player'
        
        nearby_snakes = []
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            other_head_x, other_head_y = other_snake.get_head_position()
            distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
            
            if distance < 300:
                nearby_snakes.append({
                    'snake': other_snake,
                    'distance': distance,
                    'size': len(other_snake.segments)
                })
        
        close_food = []
        for food in foods:
            distance = math.sqrt((head_x - food.x)**2 + (head_y - food.y)**2)
            if distance < AI_VISION_RANGE:
                close_food.append({
                    'food': food,
                    'distance': distance,
                    'value': food.value
                })
        
        if not nearby_snakes and close_food:
            return 'hunt_food'
        
        if snake_size > 20:
            smaller_nearby = [s for s in nearby_snakes if s['size'] < snake_size * 0.7]
            if smaller_nearby:
                encircle_chance = min(0.7, snake_size / 100)
                if random.random() < encircle_chance:
                    return 'encircle'
                else:
                    return 'attack'
        
        bigger_nearby = [s for s in nearby_snakes if s['size'] > snake_size * 1.3]
        if bigger_nearby:
            return 'evade'
        
        return 'hunt_food'

    def hunt_food_strategy(self, snake, foods):
        head_x, head_y = snake.get_head_position()
        
        best_food = None
        best_score = float('-inf')
        
        for food in foods:
            distance = math.sqrt((head_x - food.x)**2 + (head_y - food.y)**2)
            if distance < AI_VISION_RANGE:
                score = food.value * 50 - distance
                if score > best_score:
                    best_score = food.value * 50 - distance
                    best_food = food
        
        if best_food:
            return best_food.x, best_food.y
            
        center_x = WORLD_WIDTH / 2
        center_y = WORLD_HEIGHT / 2
        
        wander_radius = 300
        target_x = center_x + random.uniform(-wander_radius, wander_radius)
        target_y = center_y + random.uniform(-wander_radius, wander_radius)
        
        return target_x, target_y

    def attack_strategy(self, snake, all_snakes):
        head_x, head_y = snake.get_head_position()
        
        best_target = None
        best_score = float('-inf')
        
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            other_size = len(other_snake.segments)
            if other_size > len(snake.segments) * 1.5 or other_size < 10:
                continue
                
            other_head_x, other_head_y = other_snake.get_head_position()
            distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
            
            if distance < 250 and distance > 50:
                if len(other_snake.segments) > 1:
                    dx = other_head_x - other_snake.segments[1][0]
                    dy = other_head_y - other_snake.segments[1][1]
                    if dx != 0 or dy != 0:
                        score = 300 - distance - other_size * 0.5
                        if score > best_score:
                            best_score = score
                            best_target = other_snake
        
        if best_target:
            target_head_x, target_head_y = best_target.get_head_position()
            if len(best_target.segments) > 1:
                dx = target_head_x - best_target.segments[1][0]
                dy = target_head_y - best_target.segments[1][1]
                
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    intercept_distance = 50 + random.uniform(0, 30)
                    target_x = target_head_x + dx * intercept_distance
                    target_y = target_head_y + dy * intercept_distance
                    
                    return target_x, target_y
        
        return self.hunt_food_strategy(snake, self.game.food_manager.foods)

    def encircle_strategy(self, snake, all_snakes):
        head_x, head_y = snake.get_head_position()
        
        best_target = None
        best_score = float('-inf')
        
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            other_size = len(other_snake.segments)
            if other_size > len(snake.segments) * 0.5 or other_size < 5:
                continue
                
            other_head_x, other_head_y = other_snake.get_head_position()
            distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
            
            if distance < 200:
                score = 250 - distance - other_size
                if score > best_score:
                    best_score = score
                    best_target = other_snake
        
        if best_target:
            target_head_x, target_head_y = best_target.get_head_position()
            
            circle_radius = 60 + random.uniform(-10, 10)
            
            angle_to_target = math.atan2(target_head_y - head_y, target_head_x - head_x)
            
            circle_offset = math.pi / 2
            
            target_x = target_head_x + math.cos(angle_to_target + circle_offset) * circle_radius
            target_y = target_head_y + math.sin(angle_to_target + circle_offset) * circle_radius
            
            return target_x, target_y
        
        return self.hunt_food_strategy(snake, self.game.food_manager.foods)

    def evasion_strategy(self, snake, all_snakes):
        head_x, head_y = snake.get_head_position()
        
        threats = []
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            other_head_x, other_head_y = other_snake.get_head_position()
            distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
            
            is_larger = len(other_snake.segments) > len(snake.segments)
            if distance < 200 and is_larger:
                threats.append({
                    'x': other_head_x,
                    'y': other_head_y,
                    'distance': distance,
                    'size': len(other_snake.segments)
                })
        
        if threats:
            evade_x, evade_y = 0, 0
            
            for threat in threats:
                dx = head_x - threat['x']
                dy = head_y - threat['y']
                
                distance = max(0.1, threat['distance'])
                threat_level = (200 / distance) * (threat['size'] / max(1, len(snake.segments)))
                
                if distance > 0:
                    evade_x += (dx / distance) * threat_level
                    evade_y += (dy / distance) * threat_level
            
            evade_length = math.sqrt(evade_x*evade_x + evade_y*evade_y)
            if evade_length > 0:
                evade_x /= evade_length
                evade_y /= evade_length
                
                evasion_distance = 150
                target_x = head_x + evade_x * evasion_distance
                target_y = head_y + evade_y * evasion_distance
                
                margin = 100
                if target_x < margin:
                    target_x = margin
                elif target_x > WORLD_WIDTH - margin:
                    target_x = WORLD_WIDTH - margin
                    
                if target_y < margin:
                    target_y = margin
                elif target_y > WORLD_HEIGHT - margin:
                    target_y = WORLD_HEIGHT - margin
                    
                return target_x, target_y
        
        return self.hunt_food_strategy(snake, self.game.food_manager.foods)

    def target_player_strategy(self, snake, all_snakes):
        head_x, head_y = snake.get_head_position()
        
        for other_snake in all_snakes:
            if other_snake.is_player and other_snake.alive:
                player_snake = other_snake
                player_head_x, player_head_y = player_snake.get_head_position()
                
                distance = math.sqrt((head_x - player_head_x)**2 + (head_y - player_head_y)**2)
                
                if distance < 300:
                    if len(player_snake.segments) > 1:
                        player_dx = player_head_x - player_snake.segments[1][0]
                        player_dy = player_head_y - player_snake.segments[1][1]
                        
                        magnitude = math.sqrt(player_dx**2 + player_dy**2)
                        if magnitude > 0:
                            player_dx /= magnitude
                            player_dy /= magnitude
                        
                        intercept_distance = min(200, distance * 0.5)
                        
                        intercept_x = player_head_x + player_dx * intercept_distance
                        intercept_y = player_head_y + player_dy * intercept_distance
                        
                        jitter = 30 * random.uniform(-1, 1)
                        intercept_x += jitter
                        intercept_y += jitter
                        
                        return intercept_x, intercept_y
                        
                else:
                    return player_head_x, player_head_y
        
        return self.hunt_food_strategy(snake, self.game.food_manager.foods)

    def handle_ai_boost(self, snake, all_snakes, foods):
        if len(snake.segments) <= BOOST_MIN_LENGTH or snake.boost_cooldown > 0:
            snake.toggle_boost(False)
            return
        
        head_x, head_y = snake.get_head_position()
        
        for food in foods:
            distance = math.sqrt((head_x - food.x)**2 + (head_y - food.y)**2)
            if distance < 150 and food.value >= 3:
                snake.toggle_boost(True)
                return
        
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            if len(other_snake.segments) > len(snake.segments):
                other_head_x, other_head_y = other_snake.get_head_position()
                distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
                
                if distance < 100:
                    if len(other_snake.segments) > 1:
                        other_dir_x = other_head_x - other_snake.segments[1][0]
                        other_dir_y = other_head_y - other_snake.segments[1][1]
                        
                        to_us_x = head_x - other_head_x
                        to_us_y = head_y - other_head_y
                        
                        dot_product = other_dir_x * to_us_x + other_dir_y * to_us_y
                        
                        if dot_product > 0:
                            snake.toggle_boost(True)
                            return
        
        for other_snake in all_snakes:
            if other_snake is snake or not other_snake.alive:
                continue
                
            if len(other_snake.segments) < len(snake.segments) * 0.7:
                other_head_x, other_head_y = other_snake.get_head_position()
                distance = math.sqrt((head_x - other_head_x)**2 + (head_y - other_head_y)**2)
                
                if distance < 120:
                    if len(snake.segments) > 1:
                        our_dir_x = head_x - snake.segments[1][0]
                        our_dir_y = head_y - snake.segments[1][1]
                        
                        to_other_x = other_head_x - head_x
                        to_other_y = other_head_y - head_y
                        
                        dot_product = our_dir_x * to_other_x + our_dir_y * to_other_y
                        
                        if dot_product > 0:
                            if random.random() < AI_AGGRESSION_FACTOR * 0.7:
                                snake.toggle_boost(True)
                                return
        
        snake.toggle_boost(False)
