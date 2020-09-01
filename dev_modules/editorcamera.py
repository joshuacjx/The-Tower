import pygame as pg


class EditorCamera:
    def __init__(self):
        self.rect = pg.Rect(0, 0, 400, 300)

    def update(self, up: bool, down: bool, left: bool, right: bool, boundaries: tuple):
        if up:
            self.rect.y -= 5
        if down:
            self.rect.y += 5
        if left:
            self.rect.x -= 5
        if right:
            self.rect.x += 5

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > boundaries[0]:
            self.rect.right = boundaries[0]
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > boundaries[1]:
            self.rect.bottom = boundaries[1]


class PanelCamera:
    def __init__(self, lower_boundary):
        self.rect = pg.Rect(0, 0, 125, 240)
        self.lower_boundary = lower_boundary

    def scroll(self, up, down):
        if up:
            self.rect.y -= 10
        if down:
            self.rect.y += 10

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.lower_boundary:
            self.rect.bottom = self.lower_boundary
