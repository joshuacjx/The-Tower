from modules.component import Component


class TerrainAnimationComponent(Component):
    """Handles simple animation of sprites, regardless of
    the state of the sprite. This should be used for terrain
    sprites, which do not have EntityState as an attribute,
    and only has a single animation sequence."""

    def __init__(self, terrain_sprite, animation_sequence: list, frames_per_update=5):
        """Creates an animation component.

        :param terrain_sprite: The terrain sprite that contains this component.
        :param animation_sequence: A list of Surfaces in the animation.
        :param frames_per_update: The speed of the animation.
        """

        super().__init__()
        self.current_animation = animation_sequence
        self.terrain_sprite = terrain_sprite

        # TODO: Abstract all these counting information into another Animation class
        self.current_index = 0
        '''Index of the current image displayed in the animation sequence.'''

        self.frame_counter = 0
        '''Number of frames that has elapsed so far for a particular image.'''

        self.frames_per_update = frames_per_update
        '''Number of frames to elapse before the next image in the sequence is shown.'''

        self.animation_length = len(self.current_animation)
        '''Number of images in an animation sequence.'''

    def get_current_image(self):
        return self.current_animation[self.current_index]

    def update(self):
        """Updates the image of the sprite to the
        next Surface in the animation sequence"""
        self.frame_counter = (self.frame_counter + 1) % self.frames_per_update
        if self.frame_counter is 0:
            self.current_index = (self.current_index + 1) % self.animation_length
            self.terrain_sprite.image = self.get_current_image()


class EntityAnimationComponent(Component):
    """Handles animation of entities, whose animation
    sequence is dependent on its current state."""

    def __init__(self, entity, animation_sequences: dict, frames_per_update=5):
        """Creates an Entity Animation Component.

        :param entity: The entity that contains this component.
        :param animation_sequences: A dictionary with Entity states as keys
                                    and animation sequences as values.
        :param frames_per_update: The speed of the animation.
        """

        super().__init__()
        self.animation_sequences = animation_sequences
        self.entity = entity

        self.current_state = entity.get_state()
        self.current_animation = self.animation_sequences[self.current_state]

        self.current_index = 0
        self.frame_counter = 0
        self.frames_per_update = frames_per_update
        self.animation_length = len(self.current_animation)

    def get_current_image(self):
        return self.current_animation[self.current_index]

    def update(self):
        # Update current animation sequence if entity changed it state
        new_state = self.entity.get_state()
        if new_state is not self.current_state:
            self.current_state = new_state
            self.current_animation = self.animation_sequences[self.current_state]
            self.frame_counter = 0
            self.current_index = 0
            self.animation_length = len(self.current_animation)
        elif new_state is self.current_state:
            self.frame_counter = (self.frame_counter + 1) % self.frames_per_update

        if self.frame_counter is 0:
            self.current_index = (self.current_index + 1) % self.animation_length
            self.entity.image = self.get_current_image()