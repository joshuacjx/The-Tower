import pygame as pg
from .entitystate import EntityState, Direction

"""
* =============================================================== *
* This module contains Components, which determine the behavior   *
* of the entity which contains it.                                *
* Most of these Components are reusable, as they do not contain   *
* information on state.                                           *
* The only stateful Component in this module is the component     *
* controlling animations, as the state of the animation is unique *
* to each instance of an Entity.                                  *
* =============================================================== *

RATIONALE
-------------------------
Inheritance is a pain when dealing with complex objects, and runs the risk of 
creating so-called "God objects" - objects which know too much about everything.
This would result in a tightly-coupled system, which will be a pain to debug. 
This also produces rather complicated inheritance trees, as objects inherit 
from one another to determine its behaviour.

To resolve this, we will use composition to determine the behaviour of entities.
Behaviour code is now delegated to individual components held by the entity.

Entity behaviour is now determined by what components it contains - rather than 
what the entity is. This eliminates the need for complicated inheritance trees - 
leaving us with a rather flat and easy-to-understand inheritance structure. This 
also reduces the level of coupling - the Entity does not need to know how to do 
Physics, or animate itself, et cetera. All these behaviours will now be handled 
by resuable components.

In this model, the Entity only needs to know information regarding its state - 
where it is, what is its velocity, how much health it has left. It does not need 
to know how to move itself, or how to animate itself. In short, the role of the 
Entity is to act as a container for state.
"""


class Component:
    def __init__(self):
        pass

    def update(self, *args):
        raise NotImplementedError


# -------------------- PLAYER COMPONENTS -------------------- #
class PlayerInputComponent(Component):
    def __init__(self):
        super().__init__()

    def update(self, player, *args):
        current_keys = pg.key.get_pressed()

        if player.state == EntityState.IDLE:
            # Resolves the bug of player sliding along surface when idle
            player.x_velocity = 0
            player.y_velocity = 0

            if current_keys[pg.K_LEFT]:
                player.state = EntityState.WALKING
                player.direction = Direction.LEFT
                player.x_velocity = -180

            if current_keys[pg.K_RIGHT]:
                player.state = EntityState.WALKING
                player.direction = Direction.RIGHT
                player.x_velocity = 180

            if current_keys[pg.K_SPACE]:
                player.state = EntityState.JUMPING
                player.y_velocity = -750
                player.message("JUMP")

        elif player.state == EntityState.WALKING:
            if current_keys[pg.K_LEFT]:
                player.x_velocity = -180
                player.direction = Direction.LEFT

            if current_keys[pg.K_RIGHT]:
                player.x_velocity = 180
                player.direction = Direction.RIGHT

            if not (current_keys[pg.K_LEFT] or current_keys[pg.K_RIGHT]):
                player.state = EntityState.IDLE
                player.x_velocity = 0

            if current_keys[pg.K_SPACE]:
                player.state = EntityState.JUMPING
                player.y_velocity = -750
                player.message("JUMP")

        elif player.state == EntityState.JUMPING:
            if current_keys[pg.K_LEFT]:
                player.x_velocity = -180
                player.direction = Direction.LEFT

            if current_keys[pg.K_RIGHT]:
                player.x_velocity = 180
                player.direction = Direction.RIGHT

            if not (current_keys[pg.K_LEFT] or current_keys[pg.K_RIGHT]):
                player.x_velocity = 0

        elif player.state == EntityState.HANGING:
            player.x_velocity = 0
            player.y_velocity = 0

            if current_keys[pg.K_UP] or current_keys[pg.K_DOWN]:
                player.state = EntityState.CLIMBING

            if current_keys[pg.K_LEFT]:
                player.direction = Direction.RIGHT

            if current_keys[pg.K_RIGHT]:
                player.direction = Direction.LEFT

            if current_keys[pg.K_SPACE]:
                player.state = EntityState.JUMPING
                player.y_velocity = -750
                player.message("JUMP")

        if player.state == EntityState.CLIMBING:
            if current_keys[pg.K_UP]:
                player.y_velocity = -120

            if current_keys[pg.K_DOWN]:
                player.y_velocity = 180

            if not (current_keys[pg.K_UP] or current_keys[pg.K_DOWN]):
                player.state = EntityState.HANGING


class PlayerPhysicsComponent(Component):
    def __init__(self):
        super().__init__()
        self.gravity = 60           # because 60 * delta time gives 0 occasionally, which makes entity change state
                                    # due to the game thinking that it is jumping
        self.DISCRETE_TIMESTEP = 1 / 60      # This is important for framerate independence

    def update(self, delta_time, entity, game_map):
        # simulate multiple timesteps
        num_full_steps = int(delta_time / self.DISCRETE_TIMESTEP)
        remainder_time = delta_time % self.DISCRETE_TIMESTEP

        for i in range(0, num_full_steps):
            if entity.state != EntityState.CLIMBING and entity.state != EntityState.HANGING:
                entity.y_velocity += int(self.gravity * self.DISCRETE_TIMESTEP * 60)

            # Handle collisions in y-axis
            entity.rect.y += int(entity.y_velocity * self.DISCRETE_TIMESTEP)
            isJumping = True
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.top < entity.rect.top < colliding_sprite.rect.bottom:
                        entity.rect.top = colliding_sprite.rect.bottom
                        entity.y_velocity = 0
                if colliding_sprite.rect.top < entity.rect.bottom < colliding_sprite.rect.bottom:
                    isJumping = False
                    if entity.state == EntityState.JUMPING:
                        entity.state = EntityState.IDLE
                    entity.rect.bottom = colliding_sprite.rect.top
                    entity.y_velocity = 0
            if entity.state != EntityState.CLIMBING and entity.state != EntityState.HANGING:
                if isJumping:
                    entity.state = EntityState.JUMPING

            # Handle collisions in x-axis
            entity.rect.x += int(entity.x_velocity * self.DISCRETE_TIMESTEP)
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.left < entity.rect.left < colliding_sprite.rect.right:
                        entity.rect.left = colliding_sprite.rect.right
                    if colliding_sprite.rect.left < entity.rect.right < colliding_sprite.rect.right:
                        entity.rect.right = colliding_sprite.rect.left

        # lerps the remainder and run simulation one last time
        if entity.state != EntityState.CLIMBING and entity.state != EntityState.HANGING:
            entity.y_velocity += int(self.gravity * remainder_time * 60)

        # Handles collisions along the y axis next
        # Positions the entity at its future position
        entity.rect.y += int(entity.y_velocity * remainder_time)
        if int(entity.y_velocity * remainder_time) != 0:
            isJumping = True
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.top < entity.rect.top < colliding_sprite.rect.bottom:
                        entity.rect.top = colliding_sprite.rect.bottom
                        entity.y_velocity = 0
                if colliding_sprite.rect.top < entity.rect.bottom < colliding_sprite.rect.bottom:
                    isJumping = False
                    if entity.state == EntityState.JUMPING:
                        entity.state = EntityState.IDLE
                    entity.rect.bottom = colliding_sprite.rect.top
                    entity.y_velocity = 0
            # This is a hack to ensure that people fall properly
            if entity.state != EntityState.CLIMBING and entity.state != EntityState.HANGING:
                if isJumping:
                    entity.state = EntityState.JUMPING

        # Handle collisions along x-axis next
        entity.rect.x += int(entity.x_velocity * remainder_time)
        for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
            if not colliding_sprite.is_spike:
                if colliding_sprite.rect.left < entity.rect.left < colliding_sprite.rect.right:
                    entity.rect.left = colliding_sprite.rect.right
                if colliding_sprite.rect.left < entity.rect.right < colliding_sprite.rect.right:
                    entity.rect.right = colliding_sprite.rect.left

        # Then keeps everything within map boundaries
        map_width = game_map.rect.width
        if entity.rect.top < 0:
            entity.rect.top = 0
        if entity.rect.left < 0:
            entity.rect.left = 0
        elif entity.rect.right > map_width:
            entity.rect.right = map_width


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
        self.state = None
        self.sounds = sounds

    def update(self, *args):
        pass

    def receive(self, message):
        if message == "JUMP":
            # also stop walking sound playback
            self.sounds["JUMP"].play()
        elif message == "HIT":
            self.sounds["HIT"].play()


# -------------------- ENEMY COMPONENTS -------------------- #
class EnemyAIInputComponent(Component):
    # This is a simple AI component that walks back and forth between two points
    def __init__(self):
        super().__init__()

    def update(self, entity, map):
        entity.state = EntityState.WALKING
        if entity.direction == Direction.LEFT:
            if entity.rect.x > entity.left_bound:
                entity.x_velocity = -90
            else:
                entity.direction = Direction.RIGHT
                entity.x_velocity = 90
        else:
            if entity.rect.x < entity.right_bound:
                entity.x_velocity = 90
            else:
                entity.direction = Direction.LEFT
                entity.x_velocity = -90


class EnemyPhysicsComponent(Component):
    def __init__(self):
        super().__init__()
        self.gravity = 60           # because 60 * delta time gives 0 occasionally, which makes entity change state
                                    # due to the game thinking that it is jumping
        self.DISCRETE_TIMESTEP = 1 / 60      # This is important for framerate independence

    def update(self, delta_time, entity, game_map):
        # simulate multiple timesteps
        num_full_steps = int(delta_time / self.DISCRETE_TIMESTEP)
        remainder_time = delta_time % self.DISCRETE_TIMESTEP

        for i in range(0, num_full_steps):
            if entity.state != EntityState.CLIMBING and entity.state != EntityState.HANGING:
                entity.y_velocity += int(self.gravity * self.DISCRETE_TIMESTEP * 60)

            # Handle collisions in y-axis
            entity.rect.y += int(entity.y_velocity * self.DISCRETE_TIMESTEP)
            isJumping = True
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.top < entity.rect.top < colliding_sprite.rect.bottom:
                        entity.rect.top = colliding_sprite.rect.bottom
                        entity.y_velocity = 0
                if colliding_sprite.rect.top < entity.rect.bottom < colliding_sprite.rect.bottom:
                    isJumping = False
                    if entity.state == EntityState.JUMPING:
                        entity.state = EntityState.IDLE
                    entity.rect.bottom = colliding_sprite.rect.top
                    entity.y_velocity = 0
            if isJumping:
                entity.state = EntityState.JUMPING

            # Handle collisions in x-axis
            entity.rect.x += int(entity.x_velocity * self.DISCRETE_TIMESTEP)
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.left < entity.rect.left < colliding_sprite.rect.right:
                        entity.rect.left = colliding_sprite.rect.right
                        entity.direction = Direction.RIGHT
                        entity.x_velocity = -entity.x_velocity

                    if colliding_sprite.rect.left < entity.rect.right < colliding_sprite.rect.right:
                        entity.rect.right = colliding_sprite.rect.left
                        entity.direction = Direction.LEFT
                        entity.x_velocity = -entity.x_velocity

        # lerps the remainder and run simulation one last time
        entity.y_velocity += int(self.gravity * remainder_time * 60)

        # Handles collisions along the y axis next
        # Positions the entity at its future position
        entity.rect.y += int(entity.y_velocity * remainder_time)
        if int(entity.y_velocity * remainder_time) != 0:
            isJumping = True
            for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
                if not colliding_sprite.is_spike:
                    if colliding_sprite.rect.top < entity.rect.top < colliding_sprite.rect.bottom:
                        entity.rect.top = colliding_sprite.rect.bottom
                        entity.y_velocity = 0
                if colliding_sprite.rect.top < entity.rect.bottom < colliding_sprite.rect.bottom:
                    isJumping = False
                    if entity.state == EntityState.JUMPING:
                        entity.state = EntityState.IDLE
                    entity.rect.bottom = colliding_sprite.rect.top
                    entity.y_velocity = 0
            if isJumping:
                entity.state = EntityState.JUMPING

        # Handle collisions along x-axis next
        entity.rect.x += int(entity.x_velocity * remainder_time)
        for colliding_sprite in pg.sprite.spritecollide(entity, game_map.collideable_terrain_group, False):
            if not colliding_sprite.is_spike:
                if colliding_sprite.rect.left < entity.rect.left < colliding_sprite.rect.right:
                    entity.rect.left = colliding_sprite.rect.right
                if colliding_sprite.rect.left < entity.rect.right < colliding_sprite.rect.right:
                    entity.rect.right = colliding_sprite.rect.left

        # Then keeps everything within map boundaries
        map_width = game_map.rect.width
        if entity.rect.top < 0:
            entity.rect.top = 0
        if entity.rect.left < 0:
            entity.rect.left = 0
        elif entity.rect.right > map_width:
            entity.rect.right = map_width


class EnemyAdvancedAIInputComponent(Component):
    """Allows the enemy to chase the target within the boundaries of its own island."""
    def __init__(self):
        super().__init__()

    def update(self, entity, game_map):
        # Assume I have already generated the Floyd-Warshall array
        #
        pass


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


