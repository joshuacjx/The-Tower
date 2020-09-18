import pygame as pg


class Animation:
    """Represents the animation sequence of a state of a particular sprite."""

    def __init__(self, sprite_sheet, start, end, flip=False):
        self.images = sprite_sheet.get_images_at(start, end, flip)


class Spritesheet:
    """Utility class to load animation sequences from a spritesheet"""

    def __init__(self, filepath: str, rows: int, columns: int, width=None, height=None):
        self.spritesheet = pg.image.load(filepath)
        self.rows = rows
        self.columns = columns
        self.width = width
        self.height = height
        if width is None:
            self.width = int(self.spritesheet.get_width() / columns)
        if height is None:
            self.height = int(self.spritesheet.get_height() / rows)

    def get_image_at_position(self, position: int) -> pg.Surface:
        """Returns an image at the specified position, representing a single frame of an animation"""
        # Positions are 0-indexed
        image_row = int(position / self.columns)
        image_column = position % self.columns

        # Create a new transparent Surface
        surface = pg.Surface((self.width, self.height)).convert()
        surface.set_colorkey((0, 0, 0))

        # Blit frame into the transparent Surface, scaled to Surface size
        surface.blit(self.spritesheet, (0, 0),
            pg.Rect((image_column * self.width,
                    image_row * self.height,
                    (image_column + 1) * self.width,
                    (image_row + 1) * self.height)))
        return surface

    def get_images_at(self, start, end, flip=False) -> list:
        """Returns a sequence of Surfaces representing the specified
        sequence of frames,which represents an animation sequence"""
        images = []
        for i in range(start, end + 1):
            if flip:
                images.append(pg.transform.flip(self.get_image_at_position(i), True, False))
            else:
                images.append(self.get_image_at_position(i))
        return images

    def get_images_and_flip(self, *positions: int) -> list:
        """Does the same thing as the previous function but all images are flipped"""
        return [pg.transform.flip(self.get_image_at_position(position), True, False) for position in positions]

    def scale_images_to_size(self, image_width, image_height):
        """Scales the entire spritesheet such that the width and height of each image from get_images_at()
        matches the width and height specified in this function"""
        self.width = image_width
        self.height = image_height
        self.spritesheet = pg.transform.scale(self.spritesheet, (self.width * self.columns, self.height * self.rows))
