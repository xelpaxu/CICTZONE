import arcade 

class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/student/downward/downward1.png", scale=0.7)
        
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.direction = 'down'
        self.texture_index = 0
        self.animation_timer = 0
        self.ANIMATION_SPEED = 0.15 
        
        # Load textures
        self.textures_dict = {
            "up": [arcade.load_texture(f"assets/sprites/student/upward/upward{i}.png") for i in range(1, 5)],
            "down": [arcade.load_texture(f"assets/sprites/student/downward/downward{i}.png") for i in range(1, 5)],
            "left": [arcade.load_texture(f"assets/sprites/student/left/left{i}.png") for i in range(1, 4)],
            "right": [arcade.load_texture(f"assets/sprites/student/right/right{i}.png") for i in range(1, 4)],
        }
        
    def update(self, delta_time: float, map_boundary=None, walls=None):
        # 1. Handle X movement and wall collisions
        self.center_x += self.change_x
        if walls and arcade.check_for_collision_with_list(self, walls):
            self.center_x -= self.change_x 

        # 2. Handle Y movement and wall collisions
        self.center_y += self.change_y
        if walls and arcade.check_for_collision_with_list(self, walls):
            self.center_y -= self.change_y

        # 3. Handle Map Boundaries (Clamping to background photo)
        if map_boundary:
            l, r, b, t = map_boundary
            hw, hh = self.width / 2, self.height / 2
            self.center_x = arcade.math.clamp(self.center_x, l + hw, r - hw)
            self.center_y = arcade.math.clamp(self.center_y, b + hh, t - hh)

        # Update direction based on movement
        if self.change_y > 0: self.direction = "up"
        elif self.change_y < 0: self.direction = "down"
        elif self.change_x > 0: self.direction = "right"
        elif self.change_x < 0: self.direction = "left"
        
        # Animation Logic
        if self.change_x != 0 or self.change_y != 0:
            self.animation_timer += delta_time
            if self.animation_timer >= self.ANIMATION_SPEED:
                self.animation_timer = 0
                self.texture_index = (self.texture_index + 1) % len(self.textures_dict[self.direction])
                self.texture = self.textures_dict[self.direction][self.texture_index]
        else:
            self.texture = self.textures_dict[self.direction][0]
            self.texture_index = 0