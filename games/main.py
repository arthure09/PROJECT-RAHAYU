import arcade

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from games.core.state import SaveData
from games.hub.overworld import Overworld




class Game(arcade.Window):
    def __init__(self):
        super().__init__(1024, 576, "Project RAHAYU")
        self.save = SaveData()

    def go(self, view: arcade.View):
        view.game = self
        self.show_view(view)

if __name__ == "__main__":
    game = Game()
    game.go(Overworld())
    arcade.run()
