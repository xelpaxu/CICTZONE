import pygame
import random
from config import RED, WIDTH, HEIGHT
from pathfinding import astar
from math import sqrt

pygame.mixer.init()

# Load the shooting sound effect at the beginning of your main game loop
shoot_sound = pygame.mixer.Sound("assets/audio/shoot_sound.mp3")
pygame.mixer.music.set_volume(0.09)

class Student(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Load and resize the frames for each direction
        self.downward_frames = [
            pygame.image.load("assets/sprites/student/downward/downward1.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/downward/downward2.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/downward/downward3.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/downward/downward4.png").convert_alpha()
        ]
        
        self.downward_frames = [pygame.transform.scale(frame, (40, 60)) for frame in self.downward_frames]
    
        self.upward_frames = [
            pygame.image.load("assets/sprites/student/upward/upward1.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/upward/upward2.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/upward/upward3.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/upward/upward4.png").convert_alpha()
        ]
        
        self.upward_frames = [pygame.transform.scale(frame, (40, 60)) for frame in self.upward_frames]

        self.left_frames = [
            pygame.image.load("assets/sprites/student/left/left1.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/left/left2.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/left/left3.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/left/left2.png").convert_alpha()
        ]
        
        self.left_frames = [pygame.transform.scale(frame, (40, 60)) for frame in self.left_frames]

        self.right_frames = [
            pygame.image.load("assets/sprites/student/right/right1.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/right/right2.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/right/right3.png").convert_alpha(),
            pygame.image.load("assets/sprites/student/right/right2.png").convert_alpha()
        ]

        self.right_frames = [pygame.transform.scale(frame, (40, 60)) for frame in self.right_frames]


        self.frames = self.downward_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        self.rect.width = 20  
        self.rect.height = 40 
        
      
        self.base_damage = 10  
        self.thunderbolt_speed_increase = 0.5  
        self.gunpowder_damage_increase = 2 

    
        self.has_thunderbolt_effect = False
        self.has_gunpowder_effect = False
        
    
        self.max_ammo = 25
        self.ammo = self.max_ammo
        self.reload_time = 2500  
        self.last_shot_time = pygame.time.get_ticks() 
        self.reloading = False 

   
        self.animation_frame = 0
        self.animation_speed = 200  
        self.last_frame_change = pygame.time.get_ticks()

      
        self.projectiles = pygame.sprite.Group() 
        self.reset(x, y)
        
    def step_on_thunderbolt(self):
        if not self.has_thunderbolt_effect: 
            self.speed += self.thunderbolt_speed_increase
            self.has_thunderbolt_effect = True 

    def step_on_gunpowder(self):
        if not self.has_gunpowder_effect: 
            self.base_damage += self.gunpowder_damage_increase
            self.has_gunpowder_effect = True  

    def reset(self, x, y):
       
        self.rect.center = (x, y)
        self.speed = 3
        self.max_ammo = 25
        self.ammo = self.max_ammo
        self.reloading = False
        self.last_shot_time = pygame.time.get_ticks()
        self.projectiles.empty() 
        self.animation_frame = 0
        self.frames = self.downward_frames  
        self.image = self.frames[0]
        self.rect.width = 20  
        self.rect.height = 40  

    def update(self, keys, obstacles, mouse_pos):
        move_x = 0
        move_y = 0

        # Movement keys
        if keys[pygame.K_a]:
            move_x = -self.speed
            self.frames = self.left_frames  # Use left frames when moving left
        if keys[pygame.K_d]:
            move_x = self.speed
            self.frames = self.right_frames  # Use right frames when moving right
        if keys[pygame.K_w]:
            move_y = -self.speed
            self.frames = self.upward_frames  # Use upward frames when moving up
        if keys[pygame.K_s]:
            move_y = self.speed
            self.frames = self.downward_frames  # Use downward frames when moving down

        # Move the student
        new_rect = self.rect.move(move_x, move_y)

        # Check for boundaries
        if new_rect.left < 0:  # Left boundary
            new_rect.left = 0
        if new_rect.right > WIDTH:  # Right boundary
            new_rect.right = WIDTH
        if new_rect.top < 0:  # Top boundary
            new_rect.top = 0
        if new_rect.bottom > HEIGHT:  # Bottom boundary
            new_rect.bottom = HEIGHT

        # Update the rect position
        self.rect = new_rect

        # Check for collisions with obstacles
        collided_obstacle = self.check_collision(obstacles)
        if collided_obstacle:
            # Slide along the obstacle
            if move_x > 0:  # Moving right
                self.rect.right = collided_obstacle.left  
            elif move_x < 0:  # Moving left
                self.rect.left = collided_obstacle.right  

        # Handle animation only if moving
        if move_x != 0 or move_y != 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_change >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % len(self.frames)
                self.image = self.frames[self.animation_frame]
                self.last_frame_change = current_time
        else:
            # Set the image to the first frame of the current direction when stationary
            self.image = self.frames[0]

        # If reloading, check if reload time has passed
        current_time = pygame.time.get_ticks()
        if self.reloading and current_time - self.last_shot_time >= self.reload_time:
            self.ammo = self.max_ammo
            self.reloading = False

        # Allow manual reload by pressing R key
        if keys[pygame.K_r] and not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.last_shot_time = current_time    

    def shoot(self, target_pos):
        if self.reloading:
            return  # Do not allow shooting while reloading
        if self.ammo > 0:
            bullet = Projectile(self.rect.centerx, self.rect.centery, target_pos)
            self.projectiles.add(bullet)
            self.ammo -= 1 
            self.last_shot_time = pygame.time.get_ticks()  
            
            shoot_sound.play()  # Play the sound effect

    def draw_ammo(self, surface):

        ammo_text = f"Ammo: {self.ammo}/{self.max_ammo}"
        font = pygame.font.SysFont("Arial", 24)
        ammo_surface = font.render(ammo_text, True, (255, 255, 255)) 
        surface.blit(ammo_surface, (10, HEIGHT - 40))  

    def draw_reload_bar(self, surface):
        if self.reloading:
          
            current_time = pygame.time.get_ticks()
            reload_progress = (current_time - self.last_shot_time) / self.reload_time

         
            bar_width = self.rect.width
            bar_height = 5

       
            reload_bar_bg_color = (169, 169, 169)  
            pygame.draw.rect(surface, reload_bar_bg_color, 
                            (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width, bar_height))

            reload_bar_fg_color = (211, 211, 211)  
            pygame.draw.rect(surface, reload_bar_fg_color, 
                            (self.rect.centerx - bar_width // 2, self.rect.top - 10, bar_width * reload_progress, bar_height))

    def check_collision(self, obstacles):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle): 
                return obstacle  
        return None  

    def is_within_bounds(self):
      
        if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.top < 0 or self.rect.bottom > HEIGHT:
            return False
        return True
    
    def spawn_obstacle(obstacles, student, min_distance=50):
        while True:
          
            x = random.randint(0, WIDTH - 20) 
            y = random.randint(0, HEIGHT - 20)  
            
       
            distance = sqrt((student.rect.centerx - x) ** 2 + (student.rect.centery - y) ** 2)
            
          
            if distance >= min_distance:
                obstacles.append((x, y)) 
                break 
    def get_angle(self, target_pos):
        
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        return pygame.math.Vector2(dx, dy).angle_to(pygame.math.Vector2(1, 0))  

class GameState:
    def __init__(self, robot_pos, student_pos, obstacles):
        self.robot_pos = robot_pos
        self.student_pos = student_pos
        self.obstacles = obstacles

    def is_terminal(self):
      
        return self.robot_pos == self.student_pos

    def evaluate(self):
      
        distance = sqrt((self.robot_pos[0] - self.student_pos[0]) ** 2 + 
                        (self.robot_pos[1] - self.student_pos[1]) ** 2)
        return -distance 

    def get_possible_moves(self):
      
        possible_moves = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: 
            new_pos = (self.robot_pos[0] + dx * 20, self.robot_pos[1] + dy * 20)  # Move by 20 pixels
            if self.is_valid_move(new_pos):
                possible_moves.append(new_pos)
        return possible_moves

    def is_valid_move(self, new_pos):
        # Check if the new position is valid (not colliding with obstacles and within bounds)
        if (0 <= new_pos[0] < WIDTH and 0 <= new_pos[1] < HEIGHT):
            for obstacle in self.obstacles:
                if obstacle.collidepoint(new_pos):  
                    return False 
            return True
        return False

    def make_move(self, move):
        # Return a new GameState after making a move
        return GameState(move, self.student_pos, self.obstacles)

class Robot(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, speed=2):
        super().__init__()

        # Load and resize the frames for each direction
        self.downward_frames = [
            pygame.image.load("assets/sprites/robot/downward/downward1.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/downward/downward2.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/downward/downward3.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/downward/downward4.png").convert_alpha()
        ]
        self.downward_frames = [pygame.transform.scale(frame, (80, 90)) for frame in self.downward_frames]

        self.upward_frames = [
            pygame.image.load("assets/sprites/robot/upward/upward1.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/upward/upward2.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/upward/upward3.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/upward/upward4.png").convert_alpha()
        ]
        self.upward_frames = [pygame.transform.scale(frame, (80, 90)) for frame in self.upward_frames]

        self.left_frames = [
            pygame.image.load("assets/sprites/robot/left/left1.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/left/left2.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/left/left3.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/left/left2.png").convert_alpha()
        ]
        self.left_frames = [pygame.transform.scale(frame, (90, 90)) for frame in self.left_frames]

        self.right_frames = [
            pygame.image.load("assets/sprites/robot/right/right1.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/right/right2.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/right/right3.png").convert_alpha(),
            pygame.image.load("assets/sprites/robot/right/right2.png").convert_alpha()
        ]
        self.right_frames = [pygame.transform.scale(frame, (80, 90)) for frame in self.right_frames]

        # Set initial animation state
        self.frames = self.downward_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.width = 50 
        self.rect.height = 70  

        if x is None or y is None:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        else:
            self.rect.center = (x, y)

        self.speed = speed 
        self.health = 100
        self.max_health = 100

       
        self.animation_frame = 0
        self.animation_speed = 200 
        self.last_frame_change = pygame.time.get_ticks()

    def update(self, student, obstacles):
     
        direction = pygame.math.Vector2(student.rect.centerx - self.rect.centerx,
                                        student.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction.normalize_ip() 
            move_x = direction.x * self.speed
            move_y = direction.y * self.speed

            # Move the robot
            self.rect.x += move_x
            collided_obstacle = self.check_collision(obstacles)
            if collided_obstacle:
                # Slide along the obstacle
                if move_x > 0:  # Moving right
                    self.rect.right = collided_obstacle.left 
                elif move_x < 0:  # Moving left
                    self.rect.left = collided_obstacle.right 

            self.rect.y += move_y
            collided_obstacle = self.check_collision(obstacles)
            if collided_obstacle:
                # Slide along the obstacle
                if move_y > 0:  # Moving down
                    self.rect.bottom = collided_obstacle.top 
                elif move_y < 0:  # Moving up
                    self.rect.top = collided_obstacle.bottom 

            # Update animation frames based on movement direction
            if abs(move_x) > abs(move_y):
                if move_x > 0:
                    self.frames = self.right_frames
                else:
                    self.frames = self.left_frames
            else:
                if move_y > 0:
                    self.frames = self.downward_frames
                else:
                    self.frames = self.upward_frames

            # Update the animation frame
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_change > self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % len(self.frames)
                self.image = self.frames[self.animation_frame]
                self.last_frame_change = current_time

    def check_collision(self, obstacles):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle): 
                return obstacle  
        return None  

    def take_damage(self, base_damage):
     
        self.health -= base_damage
        if self.health <= 0:
            self.kill()  

    def draw_health_bar(self, surface):
   
        health_percentage = self.health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), 
                         (self.rect.centerx - 20, self.rect.top - 10, 40, 5)) 
        pygame.draw.rect(surface, (0, 255, 0), 
                         (self.rect.centerx - 20, self.rect.top - 10, 40 * health_percentage, 5)) 

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()

  
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        self.direction = pygame.math.Vector2(dx, dy).normalize() 

    
        self.image = pygame.image.load("assets/sprites/projectile/bullet.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, (10, 10)) 

       
        self.rect = self.image.get_rect(center=(x, y))

      
        self.speed = 6 
        
    def update(self):
       
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

      
        if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.kill()
            
class Thunderbolt(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/objects/task_objects/thunderbolt.png").convert_alpha()  
        self.image = pygame.transform.scale(self.image, (30, 30))  
        self.rect = self.image.get_rect(center=(x, y))
        self.is_collected = False 

    def update(self):
     
        pass
    
class Gunpowder(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/objects/task_objects/gunpowder.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, (30, 30)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.is_collected = False  

    def update(self):

        pass