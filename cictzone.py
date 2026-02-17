import arcade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, PLAYER_SPEED
from player import Player

class CICTZONE(arcade.Window):
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        self.background_list = arcade.SpriteList()

        # Create background sprite
        background = arcade.Sprite("assets/bg/Map.jpg")


        background.center_x = SCREEN_WIDTH / 2
        background.center_y = SCREEN_HEIGHT / 2
        
        background.width = SCREEN_WIDTH
        background.height = SCREEN_HEIGHT

        self.background_list.append(background)
        
        self.player = Player(SCREEN_HEIGHT / 2, SCREEN_WIDTH / 2)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        
    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.player_list.draw()
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = PLAYER_SPEED
            self.player.direction = "up"
        elif key == arcade.key.S:
            self.player.change_y = -PLAYER_SPEED
            self.player.direction = "down"
        elif key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED
            self.player.direction = "right"
        elif key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
            self.player.direction = "left"
    
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        if key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0
            
    def on_update(self, delta_time):
        self.player.update()
        
def main():
    window = CICTZONE()
    arcade.run()
    
if __name__ == "__main__":
    main()