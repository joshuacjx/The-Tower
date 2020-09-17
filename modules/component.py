import pygame as pg
from modules.entitystate import EntityState, Direction


class Component:
    """Components determine the behavior of the Entity
    which contains it. Most Components are reusable, as
    they do not contain information on state."""

    def __init__(self):
        # TODO: All components should have information on the game map,
        #  entity etc. so that its update function needs no arguments.
        pass

    def update(self, *args):
        pass

    def receive(self, message):
        pass


class UserControlComponent(Component):
    """Handles user input which modifies the state,
    velocity and direction of the Entity sprite."""

    def __init__(self):
        super().__init__()
        self.ZERO_VELOCITY = 0
        self.WALK_LEFT_VELOCITY = -180
        self.WALK_RIGHT_VELOCITY = 180
        self.JUMP_VELOCITY = -750
        self.CLIMB_UP_VELOCITY = -120
        self.CLIMB_DOWN_VELOCITY = 180

    def update(self, entity):
        """Updates the state, direction and velocity
        of the entity based on the user input."""

        # Keyboard constants
        LEFT_KEY = pg.K_LEFT
        RIGHT_KEY = pg.K_RIGHT
        UP_KEY = pg.K_UP
        DOWN_KEY = pg.K_DOWN
        SPACE_KEY = pg.K_SPACE

        is_pressed = pg.key.get_pressed()
        state = entity.get_state()

        if state is EntityState.IDLE:
            entity.set_x_velocity(self.ZERO_VELOCITY)
            entity.set_y_velocity(self.ZERO_VELOCITY)
            if is_pressed[LEFT_KEY]:
                entity.set_state(EntityState.WALKING)
                entity.set_direction(Direction.LEFT)
                entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
            if is_pressed[RIGHT_KEY]:
                entity.set_state(EntityState.WALKING)
                entity.set_direction(Direction.RIGHT)
                entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
            if is_pressed[SPACE_KEY]:
                entity.set_state(EntityState.JUMPING)
                entity.set_y_velocity(self.JUMP_VELOCITY)
                entity.message("JUMP")

        elif state is EntityState.WALKING:
            if is_pressed[LEFT_KEY]:
                entity.set_direction(Direction.LEFT)
                entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
            if is_pressed[RIGHT_KEY]:
                entity.set_direction(Direction.RIGHT)
                entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
            if not (is_pressed[LEFT_KEY] or is_pressed[RIGHT_KEY]):
                entity.set_state(EntityState.IDLE)
                entity.set_x_velocity(self.ZERO_VELOCITY)
            if is_pressed[SPACE_KEY]:
                entity.set_state(EntityState.JUMPING)
                entity.set_y_velocity(self.JUMP_VELOCITY)
                entity.message("JUMP")

        elif state is EntityState.JUMPING:
            if is_pressed[LEFT_KEY]:
                entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
                entity.set_direction(Direction.LEFT)
            if is_pressed[RIGHT_KEY]:
                entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
                entity.set_direction(Direction.RIGHT)
            if not (is_pressed[LEFT_KEY] or is_pressed[RIGHT_KEY]):
                entity.set_x_velocity(self.ZERO_VELOCITY)

        elif state is EntityState.HANGING:
            entity.set_x_velocity(self.ZERO_VELOCITY)
            entity.set_y_velocity(self.ZERO_VELOCITY)
            if is_pressed[UP_KEY] or is_pressed[DOWN_KEY]:
                entity.set_state(EntityState.CLIMBING)
            if is_pressed[LEFT_KEY]:
                entity.set_direction(Direction.RIGHT)
            if is_pressed[RIGHT_KEY]:
                entity.set_direction(Direction.LEFT)
            if is_pressed[SPACE_KEY]:
                entity.set_state(EntityState.JUMPING)
                entity.set_y_velocity(self.JUMP_VELOCITY)
                entity.message("JUMP")

        # TODO: Find out why elif and state cannot be used here
        if entity.get_state() is EntityState.CLIMBING:
            if is_pressed[UP_KEY]:
                entity.set_y_velocity(self.CLIMB_UP_VELOCITY)
            if is_pressed[DOWN_KEY]:
                entity.set_y_velocity(self.CLIMB_DOWN_VELOCITY)
            if not (is_pressed[UP_KEY] or is_pressed[DOWN_KEY]):
                entity.set_state(EntityState.HANGING)


class PhysicsComponent(Component):
    """Handles the physics of the Entity, which comprises of its
    acceleration due to gravity, its movement due to its velocity,
    and its collisions with the terrain and map boundaries."""

    def __init__(self):
        super().__init__()
        self.GRAVITY = 60

    @staticmethod
    def handle_y_collisions(entity, map):
        """Handles collisions between entity and the terrain along the y-axis."""
        isJumping = True
        colliding_sprites = pg.sprite.spritecollide(
            entity, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            if entity.is_colliding_from_below(colliding_sprite):
                entity.rect.top = colliding_sprite.rect.bottom
                entity.set_y_velocity(0)
            if entity.is_colliding_from_above(colliding_sprite):
                isJumping = False
                if entity.get_state() is EntityState.JUMPING:
                    entity.set_state(EntityState.IDLE)
                entity.rect.bottom = colliding_sprite.rect.top
                entity.set_y_velocity(0)
        if entity.get_state() is not EntityState.CLIMBING \
                and entity.get_state() is not EntityState.HANGING:
            if isJumping:
                entity.set_state(EntityState.JUMPING)

    @staticmethod
    def handle_x_collisions(entity, map):
        """Handles collisions between entity and the terrain along the x-axis."""
        colliding_sprites = pg.sprite.spritecollide(
            entity, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            if not colliding_sprite.is_spike:
                if entity.is_colliding_from_right(colliding_sprite):
                    entity.rect.left = colliding_sprite.rect.right
                if entity.is_colliding_from_left(colliding_sprite):
                    entity.rect.right = colliding_sprite.rect.left

    @staticmethod
    def handle_map_boundary_collisions(entity, map):
        """Handles collisions between entity and the boundaries of the map."""
        map_width = map.rect.width
        if entity.rect.top < 0:
            entity.rect.top = 0
        if entity.rect.left < 0:
            entity.rect.left = 0
        elif entity.rect.right > map_width:
            entity.rect.right = map_width


    def update(self, delta_time, entity, game_map):
        """Positions the entity at its future position, and handles all
        collisions between the entity and other sprites."""

        # TODO: Make the discrete timestep logic more readable.
        DISCRETE_TIMESTEP = 1 / 60
        num_full_steps = int(delta_time / DISCRETE_TIMESTEP)
        remainder_time = delta_time % DISCRETE_TIMESTEP

        for i in range(0, num_full_steps):
            if entity.get_state() is not EntityState.CLIMBING \
                    and entity.get_state() is not EntityState.HANGING:
                entity.y_velocity += int(self.GRAVITY * DISCRETE_TIMESTEP * 60)
            entity.rect.y += int(entity.y_velocity * DISCRETE_TIMESTEP)
            self.handle_y_collisions(entity, game_map)
            entity.rect.x += int(entity.x_velocity * DISCRETE_TIMESTEP)
            self.handle_x_collisions(entity, game_map)

        if entity.get_state() is not EntityState.CLIMBING \
                and entity.get_state() is not EntityState.HANGING:
            entity.y_velocity += int(self.GRAVITY * remainder_time * 60)
        entity.rect.y += int(entity.y_velocity * remainder_time)
        if int(entity.y_velocity * remainder_time) != 0:
            self.handle_y_collisions(entity, game_map)
        entity.rect.x += int(entity.x_velocity * remainder_time)
        self.handle_x_collisions(entity, game_map)

        self.handle_map_boundary_collisions(entity, game_map)


# For simple and single animation of terrain, without any state
class SimpleAnimationComponent(Component):
    def __init__(self, animation_sequence):
        super().__init__()
        self.animation_sequence = animation_sequence
        self.frame_counter = 0
        self.frames_per_update = 5
        self.current_index = 0
        self.animation_length = len(self.animation_sequence)

    def update(self, entity):
        self.frame_counter = (self.frame_counter + 1) % self.frames_per_update
        if self.frame_counter == 0:
            # this will probably cause some anim bugs
            self.current_index = (self.current_index + 1) % self.animation_length
            entity.image = self.animation_sequence[self.current_index]

    def get_current_image(self):
        return self.animation_sequence[self.current_index]


class PlayerAnimationComponent(Component):
    """The only stateful Component in this module is the component
    controlling animations, as the state of the animation is unique
    to each instance of an Entity."""

    def __init__(self, animation_sequences, state: EntityState):
        super().__init__()

        # Save a dictionary of animations
        self.animation_sequences = animation_sequences

        # Current animation of entity will depend on its current_state
        self.current_state = state
        self.current_animation = self.animation_sequences[self.current_state]

        self.frame_counter = 0
        self.frames_per_update = 5
        self.current_index = 0
        self.animation_length = len(self.current_animation)

    def update(self, entity):
        # If entity has changed its state
        if entity.state != self.current_state:
            # Update current state of animation
            self.current_state = entity.state
            self.current_animation = self.animation_sequences[self.current_state]
            self.frame_counter = 0
            self.current_index = 0
            self.animation_length = len(self.current_animation)
        else:
            self.frame_counter = (self.frame_counter + 1) % self.frames_per_update

        if self.frame_counter == 0:
            # this will probably cause some anim bugs
            self.current_index = (self.current_index + 1) % self.animation_length
            entity.image = self.current_animation[self.current_index]

    def get_current_image(self):
        return self.current_animation[self.current_index]


class RenderComponent(Component):
    def __init__(self):
        super().__init__()

    def update(self, entity, camera, surface):
        # Flip image if Player is moving backward
        # TODO: Get the proper posiiton of the image before flipping
        rendered_image = entity.image.subsurface(entity.blit_rect)
        if entity.direction == Direction.LEFT:
            rendered_image = pg.transform.flip(rendered_image, True, False)
        surface.blit(rendered_image,
                     (entity.rect.x - camera.rect.x, entity.rect.y - camera.rect.y))


class SoundComponent(Component):
    def __init__(self, sounds):
        super().__init__()
        self.sounds = sounds

    def receive(self, message):
        if message is "JUMP":
            self.sounds["JUMP"].play()
        elif message is "HIT":
            self.sounds["HIT"].play()


class EnemyMovementComponent(Component):
    """Handles the back and forth movement of
    the Enemy sprites between two points."""

    def __init__(self, walking_speed=90):
        super().__init__()
        self.walking_speed = walking_speed

    def update(self, enemy):
        enemy.set_state(EntityState.WALKING)
        if enemy.get_direction() is Direction.LEFT:
            if enemy.rect.x > enemy.left_bound:
                enemy.set_x_velocity(-self.walking_speed)
            else:
                enemy.reverse_direction()
                enemy.set_x_velocity(self.walking_speed)
        elif enemy.get_direction() is Direction.RIGHT:
            if enemy.rect.x < enemy.right_bound:
                enemy.set_x_velocity(self.walking_speed)
            else:
                enemy.reverse_direction()
                enemy.set_x_velocity(-self.walking_speed)


class EnemyPhysicsComponent(PhysicsComponent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handle_x_collisions(enemy, map):
        """Handles collisions between the enemy and the terrain along the x-axis.
        Enemies would reverse its direction and velocity upon collision with a sprite."""
        colliding_sprites = pg.sprite.spritecollide(
            enemy, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            if enemy.is_colliding_from_right(colliding_sprite):
                enemy.rect.left = colliding_sprite.rect.right
                enemy.set_direction(Direction.RIGHT)
            if enemy.is_colliding_from_left(colliding_sprite):
                enemy.rect.right = colliding_sprite.rect.left
                enemy.set_direction(Direction.LEFT)
            enemy.reverse_x_velocity()


class EnemyDamageCollisionComponent(Component):
    def __init__(self):
        super().__init__()

    def update(self, entity, player):
        # Reverted changes, since rect is used in physics
        if entity.rect.colliderect(player.rect):
            if player.rect.bottom < entity.rect.centery and player.y_velocity > 0:
                entity.take_damage(100)
                player.take_damage(0)
                print("Player killed an enemy!")
            else:
                player.take_damage(20)


class EnemyDamageCrushComponent(Component):
    def __init__(self):
        super().__init__()

    def update(self, entity, map):
        for colliding_sprite in pg.sprite.spritecollide(entity, map.collideable_terrain_group, False):
            if colliding_sprite.rect.bottom < entity.rect.centery:
                entity.take_damage(100)
