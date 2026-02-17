import arcade 

class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/student/downward/downward1.png", scale=1.5)
        
        self.center_x = x
        self.center_y = y
        
        self.change_x = 0
        self.change_y = 0
        self.direction = 'down'
        self.texture_index = 0
        
        self.textures_dict = {
            "up": [arcade.load_texture("assets/sprites/student/upward/upward1.png"),
                   arcade.load_texture("assets/sprites/student/upward/upward2.png"),
                   arcade.load_texture("assets/sprites/student/upward/upward3.png"),
                   arcade.load_texture("assets/sprites/student/upward/upward4.png")],
            "down": [arcade.load_texture("assets/sprites/student/downward/downward1.png"),
                   arcade.load_texture("assets/sprites/student/downward/downward2.png"),
                   arcade.load_texture("assets/sprites/student/downward/downward3.png"),
                   arcade.load_texture("assets/sprites/student/downward/downward4.png")],
            "left": [arcade.load_texture("assets/sprites/student/left/left1.png"),
                   arcade.load_texture("assets/sprites/student/left/left2.png"),
                   arcade.load_texture("assets/sprites/student/left/left3.png")],
            "right": [arcade.load_texture("assets/sprites/student/right/right1.png"),
                   arcade.load_texture("assets/sprites/student/right/right2.png"),
                   arcade.load_texture("assets/sprites/student/right/right3.png")],
        }
        
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        if self.change_x != 0 or self.change_y != 0:
            self.texture_index += 1
            if self.texture_index >= len(self.textures_dict[self.direction]):
                self.texture_index = 0
            self.texture = self.textures_dict[self.direction][self.texture_index]
        else:
            self.texture = self.textures_dict[self.direction][0]