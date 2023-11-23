import pygame, sys
from settings import *
from level import Level
from game_data import level_0
from menu import Menu


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.level = Level(level_0, self.screen, self.change_scene)
        self.menu = Menu(self.screen, self.change_scene)
        self.status = "menu"

    def change_scene(self, scene):
        self.status = scene
        self.level = Level(level_0, self.screen, self.change_scene)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")
            if self.status == "level":
                self.level.run()
            else:
                self.menu.run()

            pygame.display.update()
            self.clock.tick(60)


pygame.init()
game = Game()
game.run()
