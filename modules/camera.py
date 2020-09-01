import pygame as pg

"""
* =============================================================== *
* The Camera class keeps track of the viewport of the game using  *
* a Rect. The camera object is always passed to the renderer when *
* rendering sprites onto the screen.                              *
* =============================================================== *
"""


class Camera:
    def __init__(self, camera_size, map_rect):
        self.boundaries = map_rect

        # Rudimentary clamping of camera to map bounds only on the x-axis
        # If the map is smaller than the camera, then rescale the camera size (pretty sure this code is buggy though)
        # Solution: Either delegate all drawing to the Camera, or don't make maps smaller than the camera
        if self.boundaries.right < camera_size[0]:
            temp = camera_size
            camera_size = (self.boundaries.right, int(temp[1] * self.boundaries.right / temp[0]))
        
        self.camera_size = camera_size
        self.rect = pg.Rect((0, 0), camera_size)

    # Moves this camera's position to the target's position
    def follow_target(self, target):
        # Give the camera some lag
        lerp = 0.1
        self.rect.x += int((target.rect.centerx - self.rect.centerx) * lerp)
        self.rect.y += int((target.rect.centery - self.rect.centery) * lerp * 0.5)

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > self.boundaries.bottom:
            self.rect.bottom = self.boundaries.bottom
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.boundaries.right:
            self.rect.right = self.boundaries.right

    def snap_to_target(self, target):
        self.rect.centerx = target.rect.centerx
        self.rect.centery = target.rect.centery

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > self.boundaries.bottom:
            self.rect.bottom = self.boundaries.bottom
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.boundaries.right:
            self.rect.right = self.boundaries.right

    def update_boundaries(self, map_rect):
        self.boundaries = map_rect
