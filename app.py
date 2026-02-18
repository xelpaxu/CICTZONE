import arcade
import arcade.math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, PLAYER_SPEED
from player import Player

class CICTZONE(arcade.Window):
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Background Setup
        self.background_list = arcade.SpriteList()
        self.background = arcade.Sprite("assets/bg/Map.jpg")
        self.background.center_x = SCREEN_WIDTH / 2
        self.background.center_y = SCREEN_HEIGHT / 2
        self.background_list.append(self.background)
        
        # Player Setup
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        
        # Collision / Wall Setup
        self.wall_list = arcade.SpriteList()
        self.debug_mode = False
        
        # --- ADD YOUR BOUNDARIES HERE ---
        # Format: (x, y, width, height)
        self.add_boundary(0, 700, 2200, 140)
        self.add_boundary(1000, 198, 70, 100)
        self.add_boundary(40, 230, 80, 110)
        
        # Camera Setup
        self.camera = arcade.Camera2D()
        self.camera.zoom = 1
        
    def add_boundary(self, x, y, width, height):
        # Semi-transparent red for debug mode
        wall = arcade.SpriteSolidColor(width, height, arcade.color.BLACK)
        
        wall.color = (0, 0, 0) 
        wall.alpha = 150
        
        wall.center_x = x
        wall.center_y = y
        self.wall_list.append(wall)
        
    def on_draw(self):
        self.clear()
        self.camera.use()
        
        self.background_list.draw()
        
        # Draw walls only in debug mode
        if self.debug_mode:
            self.wall_list.draw()
            
        self.player_list.draw()
        
        # Debug UI
        if self.debug_mode:
            # Draw player coordinates near the top left of the view
            cam_x, cam_y = self.camera.position
            arcade.draw_text(f"Pos: {int(self.player.center_x)}, {int(self.player.center_y)} | F1: Debug Off", 
                             cam_x - (SCREEN_WIDTH/2)/self.camera.zoom + 10, 
                             cam_y + (SCREEN_HEIGHT/2)/self.camera.zoom - 30, 
                             arcade.color.WHITE, 12)
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F1:
            self.debug_mode = not self.debug_mode
            
        if key == arcade.key.W: self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.S: self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.D: self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.A: self.player.change_x = -PLAYER_SPEED
    
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S): self.player.change_y = 0
        if key in (arcade.key.A, arcade.key.D): self.player.change_x = 0
            
    def on_update(self, delta_time):
        # Update player with walls and map boundaries
        map_bounds = (self.background.left, self.background.right, 
                      self.background.bottom, self.background.top)
        
        self.player.update(delta_time, map_boundary=map_bounds, walls=self.wall_list)

        # Camera Clamping Logic
        view_w = SCREEN_WIDTH / self.camera.zoom
        view_h = SCREEN_HEIGHT / self.camera.zoom

        left_limit = self.background.left + (view_w / 2)
        right_limit = self.background.right - (view_w / 2)
        bottom_limit = self.background.bottom + (view_h / 2)
        top_limit = self.background.top - (view_h / 2)

        target_x = arcade.math.clamp(self.player.center_x, left_limit, right_limit)
        target_y = arcade.math.clamp(self.player.center_y, bottom_limit, top_limit)

        self.camera.position = arcade.math.lerp_2d(self.camera.position, (target_x, target_y), 0.1)

def main():
    window = CICTZONE()
    arcade.run()
    
if __name__ == "__main__":
    main()