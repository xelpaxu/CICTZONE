import pygame
import math
import random
from PIL import Image
from config import WIDTH, HEIGHT, FPS
from game_objects import Student, Robot, Projectile, Thunderbolt, Gunpowder
from csp import CSP, no_overlap_constraint, within_bounds_constraint


pygame.init()


pygame.mixer.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("CICTZONE")

map_image = pygame.image.load("assets/bg/Map.jpg").convert()  
map_image = pygame.transform.scale(map_image, (WIDTH, HEIGHT))


student = Student(WIDTH // 2, HEIGHT // 2)

# Initialize counters for thunderbolts and gunpowder
thunderbolt_spawn_count = 0
gunpowder_spawn_count = 0
max_spawns = 10  

def spawn_thunderbolt():
    global thunderbolt_spawn_count
    if thunderbolt_spawn_count < max_spawns:
     
        x = random.randint(WIDTH // 3, 2 * WIDTH // 3 - 20) 
        y = random.randint(HEIGHT // 3, 2 * HEIGHT // 3 - 20) 
        thunderbolt = Thunderbolt(x, y)
        thunderbolt_spawn_count += 1  
        return thunderbolt
    return None 

def spawn_gunpowder():
    global gunpowder_spawn_count
    if gunpowder_spawn_count < max_spawns:
       
        x = random.randint(WIDTH // 3, 2 * WIDTH // 3 - 20)  
        y = random.randint(HEIGHT // 3, 2 * HEIGHT // 3 - 20)
        powder = Gunpowder(x, y)
        gunpowder_spawn_count += 1 
        return powder
    return None


obstacle_size = (60, 30)  
min_distance = 50  


car_positions = [
    (100, 200),  
    (300, 400),  
    (500, 250), 
    (700, 170), 
    (700, 350),
    (400, 200),
    (600, 450), 
    (850, 250),  
    (120, 320)
]


car_image_size = (80, 120) 

car_images = []
for i in range(1, 7):
    car_image = pygame.image.load(f"assets/objects/car_obstacles/car{i}.png").convert_alpha()
    
    
    car_image = pygame.transform.scale(car_image, car_image_size)
    
    car_images.append(car_image)


obstacles = []
for pos in car_positions:
    obstacle_rect = pygame.Rect(pos[0], pos[1], obstacle_size[0], obstacle_size[1])
    obstacles.append(obstacle_rect)
    

all_sprites = pygame.sprite.Group()
remaining_robots = 5  # Set the initial count of remaining robots

def spawn_slow_robots(num_robots):
    for _ in range(num_robots):
        # Define the starting position for the slow robots
        x = random.randint(0, WIDTH - 50)  
        y = random.randint(0, HEIGHT - 70) 
        slow_robot = Robot(x, y, speed=1) 
        all_sprites.add(slow_robot) 

def spawn_robots(num_robots):
    variables = [f'robot_{i}' for i in range(num_robots)]
    domains = {var: [] for var in variables}
    
    for var in variables:
        while True:
            # Generate random position
            x = random.randint(0, WIDTH - 50)  # Adjust the width as needed
            y = random.randint(0, HEIGHT - 70)  # Adjust the height as needed
            robot_rect = pygame.Rect(x, y, 50, 70)  # Create a rect for the robot
            
            # Check for collisions with obstacles
            if not any(robot_rect.colliderect(obstacle) for obstacle in obstacles):
                domains[var].append((x, y))  # Add valid position to the domain
                break  # Exit the loop once a valid position is found

    # Create a CSP instance with the new constraint
    constraints = [no_overlap_constraint, within_bounds_constraint]
    csp = CSP(variables, domains, constraints)

    assignment = csp.backtrack({})
    if assignment:
        for var, position in assignment.items():
            x, y = position
            robot = Robot(x, y)  
            all_sprites.add(robot) 
    else:
        print("No valid positions found for robots.")


spawn_robots(remaining_robots)

robot_start_position = (WIDTH // 4, HEIGHT // 2) 

robot = Robot(*robot_start_position)

all_sprites = pygame.sprite.Group()
all_sprites.add(student, robot)

thunderbolts = pygame.sprite.Group()
gunpowder = pygame.sprite.Group()

# Game states
START_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
GAME_WON = 3
game_state = START_SCREEN

# Buttons
font = pygame.font.SysFont("Century Gothic", 36)
button_font = pygame.font.SysFont("Century Gothic", 24)

# Initialize remaining robots
remaining_robots = 3  
robot_destroyed_time = 0 
robot_respawn_delay = 5000  
robot_is_destroyed = False 

def is_frame_white(frame):
    """Check if the frame is predominantly white."""
    # Convert the frame to a pixel array
    pixels = pygame.surfarray.array3d(frame)
    # Count the number of white pixels
    white_pixels = (pixels[:, :, 0] > 240) & (pixels[:, :, 1] > 240) & (pixels[:, :, 2] > 240)
    return white_pixels.sum() > (pixels.shape[0] * pixels.shape[1] * 0.9) 

def extract_gif_frames(gif_path, width, height):
    """Extract frames from a GIF, resize them to the specified size, and return them as Pygame surfaces."""
    gif = Image.open(gif_path)
    frames = []

    try:
        while True:
          
            frame = pygame.image.fromstring(gif.tobytes(), gif.size, gif.mode)
         
            frame_resized = pygame.transform.scale(frame, (width, height))
            
         
            if not is_frame_white(frame_resized):
                frames.append(frame_resized)
                
            gif.seek(gif.tell() + 1) 
    except EOFError:
        pass 

    return frames


background_frames = extract_gif_frames("assets/bg/bgmain.gif", WIDTH, HEIGHT)
frame_index = 0
frame_delay = 30  
last_frame_time = 0  


title_frames = extract_gif_frames("assets/text_graphics/animated_title.gif", 600, 500)  
title_frame_index = 0
title_frame_delay = 300 
last_title_frame_time = 0 

def draw_start_screen():
    global frame_index, last_frame_time, title_frame_index, last_title_frame_time

   
    if not pygame.mixer.music.get_busy(): 
        try:
            pygame.mixer.music.load("assets/audio/mainstartbg.mp3")
            pygame.mixer.music.set_volume(1)  
            pygame.mixer.music.play(-1) 
        except pygame.error as e:
            print(f"Error loading music: {e}")

    current_time = pygame.time.get_ticks()

    # Update the background frame
    if current_time - last_frame_time > frame_delay:
        frame_index = (frame_index + 1) % len(background_frames)
        last_frame_time = current_time

    # Update the title frame
    if current_time - last_title_frame_time > title_frame_delay:
        title_frame_index = (title_frame_index + 1) % len(title_frames)
        last_title_frame_time = current_time

    # Display current frame of the GIF as the background
    screen.blit(background_frames[frame_index], (0, 0))

    # Load and display the animated title image
    title_rect = title_frames[title_frame_index].get_rect(center=(WIDTH // 2, 250))  
    screen.blit(title_frames[title_frame_index], title_rect)

    # Load and resize the start button image
    start_button_image = pygame.image.load("assets/button/start_button.png").convert_alpha()
    start_button_image = pygame.transform.scale(start_button_image, (200, 70)) 

    # Create a rectangle for the button and set its position
    start_button_rect = start_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

    # Draw the start button image
    screen.blit(start_button_image, start_button_rect) 

    pygame.display.flip()

    return start_button_rect 


game_over_title_image = pygame.image.load("assets/text_graphics/gameover_title.png").convert_alpha()
game_over_title_image = pygame.transform.scale(game_over_title_image, (800, 700))


restart_button_image = pygame.image.load("assets/button/playagain_button.png").convert_alpha()
restart_button_image = pygame.transform.scale(restart_button_image, (210, 80))  


quit_button_image = pygame.image.load("assets/button/quit_button.png").convert_alpha()
quit_button_image = pygame.transform.scale(quit_button_image, (180, 60))  

def draw_game_over_screen():

    screen.blit(background_frames[frame_index], (0, 0)) 

    # Draw the game over title image in the center
    title_rect = game_over_title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 150)) 
    screen.blit(game_over_title_image, title_rect)

    # Restart button
    restart_button_rect = restart_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  
    screen.blit(restart_button_image, restart_button_rect) 

    # Quit button
    quit_button_rect = quit_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170))  
    screen.blit(quit_button_image, quit_button_rect)  

    pygame.display.flip()

    return restart_button_rect, quit_button_rect   

# Load the game won title image at the beginning of your script
game_won_title_image = pygame.image.load("assets/text_graphics/win.png").convert_alpha()
game_won_title_image = pygame.transform.scale(game_won_title_image, (800, 700))

# Load the restart button image at the beginning of your script
playagain_button_image = pygame.image.load("assets/button/playagain_button.png").convert_alpha()
playagain_button_image = pygame.transform.scale(restart_button_image, (200, 50))  

# Load the quit button image at the beginning of your script
quitbutton = pygame.image.load("assets/button/quit_button.png").convert_alpha()
quitbutton = pygame.transform.scale(quit_button_image, (200, 50)) 

def draw_win_screen():
    screen.blit(background_frames[frame_index], (0, 0))

    title_rect = game_won_title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 150)) 
    screen.blit(game_won_title_image, title_rect)

    playagain_button_rect = playagain_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)) 
    screen.blit(playagain_button_image, playagain_button_rect)  

    quitbutton_rect = quitbutton.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170)) 
    screen.blit(quitbutton, quitbutton_rect)  # Use quitbutton instead of quit_button_image

    pygame.display.flip()

    return playagain_button_rect, quitbutton_rect  # Return the correct rectangles

def reset_game():
    global remaining_robots
    student.rect.center = (WIDTH // 2, HEIGHT // 2)
    student.projectiles.empty()

 
    remaining_robots = 3

 
    thunderbolts.empty()
    gunpowder.empty()

   
    global robot 
    robot.kill() 
    robot = Robot(*robot_start_position)  
    all_sprites.add(robot)

# Draw remaining robots count
def draw_remaining_robots_count(surface, count):
    font = pygame.font.SysFont("Arial", 24)
    text = f"Robots Remaining: {count}"
    text_surface = font.render(text, True, (255, 255, 255)) 
    surface.blit(text_surface, (10, 10)) 


running = True
clock = pygame.time.Clock()


thunderbolt_spawn_time = 0
gunpowder_spawn_time = 0
spawn_interval = 3000  

while running:
    if game_state == START_SCREEN:
        start_button_rect = draw_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    try:
                        pygame.mixer.music.load("assets/audio/mainbg.mp3")
                        pygame.mixer.music.set_volume(0.5) 
                        pygame.mixer.music.play(-1) 
                        print("Playing music...")
                    except pygame.error as e:
                        print(f"Error loading music: {e}")
                    game_state = GAME_RUNNING

    elif game_state == GAME_RUNNING:
        
        screen.blit(map_image, (0, 0)) 

       
        shake_amplitude = 1 
        shake_speed = 200 
        
        # Calculate shake effect
        current_time = pygame.time.get_ticks()
        shake_offset = shake_amplitude * math.sin(current_time / shake_speed)  

        # Spawn thunderbolt every 3 seconds
        if current_time - thunderbolt_spawn_time > spawn_interval:
            thunderbolt = spawn_thunderbolt()
            if thunderbolt: 
                thunderbolts.add(thunderbolt)  
            thunderbolt_spawn_time = current_time  

        # Spawn gunpowder every 3 seconds
        if current_time - gunpowder_spawn_time > spawn_interval:
            gunpowder_item = spawn_gunpowder()
            if gunpowder_item:
                gunpowder.add(gunpowder_item) 
            gunpowder_spawn_time = current_time 

        for thunderbolt in thunderbolts:
            if student.rect.colliderect(thunderbolt.rect):
                if not thunderbolt.is_collected: 
                    student.step_on_thunderbolt()  
                    thunderbolt.is_collected = True  
                    thunderbolt.kill()  

        for powder in gunpowder:
            if student.rect.colliderect(powder.rect):
                if not powder.is_collected: 
                    student.step_on_gunpowder() 
                    powder.is_collected = True 
                    powder.kill()  

        # Draw thunderbolts and gunpowder
        thunderbolts.draw(screen)
        gunpowder.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                student.shoot(pygame.mouse.get_pos())  # Shoot with the Student class

        keys = pygame.key.get_pressed()
        student.update(keys, obstacles, pygame.mouse.get_pos())  
        robot.update(student, obstacles) 

        for projectile in student.projectiles:
            if robot.health > 0 and projectile.rect.colliderect(robot.rect):
                robot.take_damage(student.base_damage) 
                projectile.kill() 

                if robot.health <= 0:
                    remaining_robots -= 1 
                    if remaining_robots <= 0:
                        game_state = GAME_WON  
                    else:
                        robot_is_destroyed = True 
                        robot_destroyed_time = pygame.time.get_ticks() 

        # Check if the robot is destroyed and if the respawn delay has passed
        if robot_is_destroyed:
            current_time = pygame.time.get_ticks()
            if current_time - robot_destroyed_time >= robot_respawn_delay:
                robot_is_destroyed = False
                robot.speed += 2  
                robot = Robot(*robot_start_position, speed=robot.speed)  
                all_sprites.add(robot) 


           
        if robot.health > 0 and student.rect.colliderect(robot.rect):
        
            game_state = GAME_OVER

      
        for i, obs in enumerate(obstacles):
            shake_x = obs.x + shake_offset
            shake_y = obs.y 
            screen.blit(car_images[i % len(car_images)], (shake_x, shake_y))  

      
        all_sprites.draw(screen)
        student.projectiles.update()
        student.projectiles.draw(screen)

        if robot.health > 0:
            robot.draw_health_bar(screen)  
        

        student.draw_reload_bar(screen)

        draw_remaining_robots_count(screen, remaining_robots)

        pygame.display.flip()
        clock.tick(FPS)
    
    elif game_state == GAME_OVER:
      
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            frame_index = (frame_index + 1) % len(background_frames)
            last_frame_time = current_time

        restart_button_rect, quit_button_rect = draw_game_over_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    reset_game() 
                    game_state = GAME_RUNNING 
                elif quit_button_rect.collidepoint(event.pos):
                    running = False 

    elif game_state == GAME_WON:
      
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > frame_delay:
            frame_index = (frame_index + 1) % len(background_frames)
            last_frame_time = current_time

  
        playagain_button, quit_button_image = draw_win_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if playagain_button.collidepoint(event.pos):
                    reset_game() 
                    game_state = GAME_RUNNING  
                elif start_button_rect.collidepoint(event.pos):
                    running = False 

pygame.quit()