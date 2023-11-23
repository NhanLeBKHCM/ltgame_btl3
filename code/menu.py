import pygame, sys
from decoration import *
from settings import screen_width, screen_height, tile_size


class Menu:
    def __init__(self, surface, change_scene):
        self.display_surface = surface
        self.change_scene = change_scene
        self.sky = Sky(7)
        self.water = Water(screen_height - 50, screen_width + tile_size * 2)
        self.clouds = Clouds(350, screen_width + tile_size, 20)
        self.about = False

        def newgameAct():
            self.change_scene("level")

        self.newgameOp = TextBox(
            self.display_surface, (screen_width / 2, 250), "New game", newgameAct
        )

        def aboutAct():
            self.about = True

        self.aboutOp = TextBox(
            self.display_surface, (screen_width / 2, 350), "About", aboutAct
        )

        def exitAct():
            pygame.quit()
            sys.exit()

        self.exitOp = TextBox(
            self.display_surface, (screen_width / 2, 450), "Exit", exitAct
        )

        self.aboutTxt = TextBox(
            self.display_surface,
            (screen_width / 2, 300),
            """Lorem ipsum dolor sit amet,....""",
            None,
            30,
        )

        def backAct():
            self.about = False

        self.backOp = TextBox(
            self.display_surface, (screen_width / 2, 400), "Back", backAct
        )

    def run(self):
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, 0)
        self.water.draw(self.display_surface, 0)

        if not self.about:
            self.newgameOp.draw()
            self.aboutOp.draw()
            self.exitOp.draw()
        else:
            self.aboutTxt.draw()
            self.backOp.draw()


class TextBox(pygame.sprite.Sprite):
    def __init__(self, surface, center, text, action, weight=50):
        super().__init__()

        self.font = [
            pygame.font.Font("../graphics/ui/ARCADEPI.ttf", weight),
            pygame.font.Font("../graphics/ui/ARCADEPI.ttf", weight + 10),
        ]
        self.display_surface = surface
        self.action = action
        self.text = text
        self.center = center
        self.image = self.font[0].render(self.text, False, "#33323d")
        self.rect = self.image.get_rect(center=self.center)

    def get_input(self):
        if self.action:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.image = self.font[1].render(self.text, False, "#33323d")
                if pygame.mouse.get_pressed()[0]:
                    self.image = self.font[0].render(self.text, False, "#dc4949")
                    self.action()
            else:
                self.image = self.font[0].render(self.text, False, "#33323d")
            self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self):
        self.get_input()
        self.display_surface.blit(self.image, self.rect)
