import pygame as pg


class SpriteSheet:
    """This is a utility class that allows us generate
    Sprite Sheets from large images, or to load specific
    images / image sequences from a Sprite Sheet."""

    def __init__(self, filepath, rows, columns):
        """Generates a SpriteSheet.

        :param filepath:    The filepath to the sprite sheet image.
        :param rows:        Number of rows in the sprite sheet.
        :param columns:     Number of columns in the sprite sheet.
        """

        self.rows = rows
        self.columns = columns
        self.sprite_sheet = pg.image.load(filepath)

        # Dimensions of an image in the sprite sheet
        self.width = int(self.sprite_sheet.get_width() / columns)
        self.height = int(self.sprite_sheet.get_height() / rows)

    def get_image_at(self, position: int) -> pg.Surface:
        """Returns an image at the specified position,
        representing a single frame of an Animation."""

        row = int(position / self.columns)
        col = position % self.columns
        surface = pg.Surface((self.width, self.height))
        surface.set_colorkey((0, 0, 0))
        area = pg.Rect((col * self.width,
                        row * self.height,
                        (col + 1) * self.width,
                        (row + 1) * self.height))
        surface.blit(self.sprite_sheet, (0, 0), area)
        return surface

    def get_image_subsequence(self, start, end, flip=False) -> list:
        """Returns a sequence of Surfaces representing the specified
        sequence of images, which represents an animation sequence."""

        images = []
        for i in range(start, end + 1):
            image = self.get_image_at(i)
            if flip:
                image = pg.transform.flip(image, True, False)
            # image = image.subsurface(image.get_bounding_rect())
            images.append(image)
        return images

    def get_image_sequence(self, flip=False) -> list:
        """Returns a sequence of Surfaces representing the
        all images found inside the SpriteSheet. Used when
        all images in the SpriteSheet are part of a single
        Animation."""

        num_images = self.rows * self.columns - 1
        return self.get_image_subsequence(0, num_images, flip)

    def scale(self, new_width, new_height):
        """Scales each image in the SpriteSheet to the
        width and height specified in the arguments."""

        self.width = new_width
        self.height = new_height
        self.sprite_sheet = pg.transform.scale(
            self.sprite_sheet,
            (self.width * self.columns, self.height * self.rows))
        return self
