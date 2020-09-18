from pygame.surface import Surface
from .component import Component


class Animation:
    # TODO: Make further encapsulation by making the constructor
    #  simply take in a filepath to the directory and transform
    #  it into a list of Surfaces

    def __init__(self, sprite_sheet, start, end, flip=False, speed=5):
        self.images = sprite_sheet.get_images_at(start, end, flip)
        self.current_index = 0
        self.frame_counter = 0
        self.FRAMES_PER_UPDATE = speed
        self.animation_length = len(self.images)

    def get_image_at(self, index):
        return self.images[index]

    def get_next_image(self) -> Surface:
        self.frame_counter = (self.frame_counter + 1) % self.FRAMES_PER_UPDATE
        if self.frame_counter is 0:
            self.current_index = (self.current_index + 1) % self.animation_length
        return self.get_image_at(self.current_index)


class TerrainAnimationComponent(Component):
    """Handles simple animation of sprites, regardless of
    the state of the sprite. This should be used for terrain
    sprites, which do not have EntityState as an attribute,
    and only has a single animation sequence."""

    def __init__(self, terrain_sprite, animation: Animation):
        super().__init__()
        self.animation = animation
        self.terrain_sprite = terrain_sprite

    def update(self):
        self.terrain_sprite.image = self.animation.get_next_image()


class EntityAnimationComponent(Component):
    """Handles animation of entities, whose animation
    sequence is dependent on its current state."""

    def __init__(self, entity, animations: dict):
        """Creates an Entity Animation Component.

        :param entity: The entity that contains this component.
        :param animations: A dictionary with Entity states
                            as keys and Animations as values.
        """
        super().__init__()
        self.entity = entity
        self.animations = animations
        self.current_state = entity.get_state()
        self.current_animation = self.animations[self.current_state]

    def get_initial_image(self):
        return self.current_animation.get_next_image()

    def update(self):
        """Switches to a new Animation if the Entity has changed its state."""
        new_state = self.entity.get_state()
        has_changed_state = new_state is not self.current_state
        if has_changed_state:
            self.current_state = new_state
            self.current_animation = self.animations[self.current_state]
        self.entity.image = self.current_animation.get_next_image()
