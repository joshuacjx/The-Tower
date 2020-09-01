import pygame as pg
from .camera import Camera

"""
* =============================================================== *
* This module contains classes to facilitate the rendering of     *
* backgrounds onto a surface. Backgrounds can be either static,   *
* parallax (moves with the camera), or auto-scrolling.            *
* =============================================================== *

Implementation of moving backgrounds
--------------------------------------
Two images are positioned side by side, one at (0, 0) and one at (BG_WIDTH, 0).
The exact position of the portion of the surface to blit is given by the blit 
coordinates.
The blit coordinates are incremented/decremented proportionally to the movement 
of the camera.
As the blit coordinates always lie between 0 and BG_WIDTH (since it is a modulo 
of the BG_WIDTH), the viewport will always lie within the boundaries of the two 
images.
"""


class StaticBackground:
    """Handles the rendering of a static, unmoving background, which does not change with the camera position"""
    def __init__(self, filepath: str, surface: pg.Surface):
        self.surface = surface
        self.image = pg.image.load(filepath).convert_alpha()
        # scales the image to fill the screen
        if self.image.get_width() / self.image.get_height() > surface.get_width() / surface.get_height():
            self.background = pg.transform.scale(self.image,
                                                 (int(self.image.get_width() *
                                                  surface.get_height() / self.image.get_height()),
                                                  surface.get_height()))
        else:
            self.background = pg.transform.scale(self.image,
                                                 (surface.get_width(),
                                                  int(self.image.get_height() *
                                                  surface.get_width() / self.image.get_width())))

        self.blit_coordinates = (int((self.surface.get_width() - self.background.get_width()) / 2),
                                 int((self.surface.get_height() - self.background.get_height()) / 2))

    def update(self, *args):
        pass

    def render(self):
        """Renders the background onto the surface"""
        self.surface.blit(self.background, self.blit_coordinates)


# Used for GameScene
class ParallaxBackground:
    """Handles the rendering of a background that moves with the camera"""
    def __init__(self, filepath: str, surface: pg.Surface):
        self.surface = surface
        self.image = pg.image.load(filepath).convert_alpha()
        self.background = pg.transform.scale(self.image,
            (self.image.get_width() * int(surface.get_height() / self.image.get_height()), surface.get_height()))
        
        # The x-coordinate of the position where the background will be blitted
        self.blit_position = 0

        self.BACKGROUND_WIDTH = self.background.get_width()
        self.BACKGROUND_HEIGHT = self.background.get_height()

    def update(self, speed: float, camera: Camera):
        """
        Updates the section of the background to be blitted based on the movement of the
        given camera and proportional to the given speed
        """
        current_x_position = camera.rect.left
        self.blit_position = - int(current_x_position * speed) % self.BACKGROUND_WIDTH

    def render(self):
        """Renders the background onto the surface according to the blit position"""
        self.surface.blit(self.background, (self.blit_position, 0))
        self.surface.blit(self.background, (self.blit_position - self.BACKGROUND_WIDTH, 0))


# Used for TitleScene
class ScrollingBackground:
    """Handles the rendering of a background that automatically scrolls"""
    def __init__(self, filepath: str, surface: pg.Surface):
        self.surface = surface
        self.image = pg.image.load(filepath).convert_alpha()
        self.background = pg.transform.scale(self.image,
                                             (self.image.get_width() * int(
                                                 surface.get_height() / self.image.get_height()), surface.get_height()))

        # The x-coordinate of the position where the background will be blitted
        self.blit_position = 0

        self.BACKGROUND_WIDTH = self.background.get_width()
        self.BACKGROUND_HEIGHT = self.background.get_height()

    def update(self, speed: float):
        """Changes the blit position by the value of the given speed"""
        # blit_position is now a float to allow slower updates
        self.blit_position = (self.blit_position - speed) % self.BACKGROUND_WIDTH

    def render(self):
        """Renders the background onto the surface according to the blit position"""
        integer_blit_position = int(self.blit_position)
        self.surface.blit(self.background, (integer_blit_position, 0))
        self.surface.blit(self.background, (integer_blit_position - self.BACKGROUND_WIDTH, 0))