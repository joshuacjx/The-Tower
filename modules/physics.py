import pygame as pg
from .component import Component
from .entitystate import EntityState, Direction, EntityMessage


class Physics:
    """A Physics object can be stored as an attribute to Entities and Blocks.
    They encapsulate all the data related to position, velocity and Direction."""

    def __init__(self, position, dimensions):
        self.rect = pg.Rect(position, dimensions)
        self.x_velocity = 0
        self.y_velocity = 0
        self.direction = Direction.RIGHT



class PhysicsComponent(Component):
    """A PhysicsComponent differs from other Components because they require a
    Physics object as one of their attributes. This dependence on solely a Physics
    object will mean that Components are no longer dependent on Entities themselves."""

    def __init__(self, physics):
        super().__init__()
        self.physics = physics


class UserControlComponent(PhysicsComponent):
    # TODO: Implement an EntityStateManager which handles the state changes.
    #  UserControlComponent and AIControlComponent should only handle the velocities.
    #  RigidBodyComponent should only handly collisions and should not be concerned with state.

    """Handles user input which modifies the state,
    velocity and direction of the Entity sprite."""

    def __init__(self, entity, physics):
        super().__init__(physics)
        self.entity = entity
        self.ZERO_VELOCITY = 0
        self.WALK_LEFT_VELOCITY = -180
        self.WALK_RIGHT_VELOCITY = 180
        self.JUMP_VELOCITY = -500
        self.CLIMB_UP_VELOCITY = -120
        self.CLIMB_DOWN_VELOCITY = 180

    def update(self):
        """Updates the state, direction and velocity
        of the entity based on the user input."""
        is_pressed = pg.key.get_pressed()
        state = self.entity.get_state()
        if state is EntityState.IDLE:
            self.handle_idle_entity(is_pressed)
        elif state is EntityState.WALKING:
            self.handle_walking_entity(is_pressed)
        elif state is EntityState.JUMPING:
            self.handle_jumping_entity(is_pressed)
        elif state is EntityState.HANGING:
            self.handle_hanging_entity(is_pressed)
        if self.entity.get_state() is EntityState.CLIMBING:
            self.handle_climbing_entity(is_pressed)

    def handle_idle_entity(self, is_pressed: dict):
        self.entity.set_x_velocity(self.ZERO_VELOCITY)
        if is_pressed[pg.K_LEFT]:
            self.entity.set_state(EntityState.WALKING)
            self.entity.set_direction(Direction.LEFT)
            self.entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
        if is_pressed[pg.K_RIGHT]:
            self.entity.set_state(EntityState.WALKING)
            self.entity.set_direction(Direction.RIGHT)
            self.entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
        if is_pressed[pg.K_SPACE]:
            self.entity.set_state(EntityState.JUMPING)
            self.entity.set_y_velocity(self.JUMP_VELOCITY)
            self.entity.message(EntityMessage.JUMP)

    def handle_walking_entity(self, is_pressed: dict):
        if is_pressed[pg.K_LEFT]:
            self.entity.set_direction(Direction.LEFT)
            self.entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
        if is_pressed[pg.K_RIGHT]:
            self.entity.set_direction(Direction.RIGHT)
            self.entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
        if not (is_pressed[pg.K_LEFT] or is_pressed[pg.K_RIGHT]):
            self.entity.set_state(EntityState.IDLE)
            self.entity.set_x_velocity(self.ZERO_VELOCITY)
        if is_pressed[pg.K_SPACE]:
            self.entity.set_state(EntityState.JUMPING)
            self.entity.set_y_velocity(self.JUMP_VELOCITY)
            self.entity.message(EntityMessage.JUMP)

    def handle_jumping_entity(self, is_pressed: dict):
        if is_pressed[pg.K_LEFT]:
            self.entity.set_x_velocity(self.WALK_LEFT_VELOCITY)
            self.entity.set_direction(Direction.LEFT)
        if is_pressed[pg.K_RIGHT]:
            self.entity.set_x_velocity(self.WALK_RIGHT_VELOCITY)
            self.entity.set_direction(Direction.RIGHT)
        if not (is_pressed[pg.K_LEFT] or is_pressed[pg.K_RIGHT]):
            self.entity.set_x_velocity(self.ZERO_VELOCITY)

    def handle_hanging_entity(self, is_pressed: dict):
        self.entity.set_x_velocity(self.ZERO_VELOCITY)
        self.entity.set_y_velocity(self.ZERO_VELOCITY)
        if is_pressed[pg.K_UP] or is_pressed[pg.K_DOWN]:
            self.entity.set_state(EntityState.CLIMBING)
        if is_pressed[pg.K_LEFT]:
            self.entity.set_direction(Direction.RIGHT)
        if is_pressed[pg.K_RIGHT]:
            self.entity.set_direction(Direction.LEFT)
        if is_pressed[pg.K_SPACE]:
            self.entity.set_state(EntityState.JUMPING)
            self.entity.set_y_velocity(self.JUMP_VELOCITY)
            self.entity.message(EntityMessage.JUMP)

    def handle_climbing_entity(self, is_pressed: dict):
        if is_pressed[pg.K_UP]:
            self.entity.set_y_velocity(self.CLIMB_UP_VELOCITY)
        if is_pressed[pg.K_DOWN]:
            self.entity.set_y_velocity(self.CLIMB_DOWN_VELOCITY)
        if not (is_pressed[pg.K_UP] or is_pressed[pg.K_DOWN]):
            self.entity.set_state(EntityState.HANGING)


class AIControlComponent(PhysicsComponent):
    """Handles the back and forth movement of
    the Enemy sprites between two points."""

    def __init__(self, physics, starting_position, walking_speed=90, patrol_radius=50):
        super().__init__(physics)
        self.WALKING_SPEED = walking_speed
        self.left_bound = starting_position[0] - patrol_radius
        self.right_bound = starting_position[0] + patrol_radius

    def update(self, enemy, map):
        enemy.set_state(EntityState.WALKING)
        if enemy.get_direction() is Direction.LEFT:
            if enemy.rect.x > self.left_bound:
                enemy.set_x_velocity(-self.WALKING_SPEED)
            else:
                enemy.reverse_direction()
        elif enemy.get_direction() is Direction.RIGHT:
            if enemy.rect.x < self.right_bound:
                enemy.set_x_velocity(self.WALKING_SPEED)
            else:
                enemy.reverse_direction()

    def receive(self, message, enemy):
        if message is EntityMessage.AI_TURN_RIGHT:
            enemy.set_direction(Direction.RIGHT)
            enemy.reverse_x_velocity()
        if message is EntityMessage.AI_TURN_LEFT:
            enemy.set_direction(Direction.LEFT)
            enemy.reverse_x_velocity()


class EntityGravityComponent(PhysicsComponent):
    """Enables the entity to respond to the force of gravity."""

    def __init__(self, physics, weight=30):
        super().__init__(physics)
        self.GRAVITY = weight
        self.DISCRETE_TIMESTEP = 1 / 60

    def update(self, entity, delta_time):
        num_full_steps = int(delta_time / self.DISCRETE_TIMESTEP)
        remainder_time = delta_time % self.DISCRETE_TIMESTEP
        is_on_chain = entity.get_state() is EntityState.CLIMBING \
                      or entity.get_state() is EntityState.HANGING
        for i in range(0, num_full_steps):
            if not is_on_chain:
                entity.y_velocity += int(self.GRAVITY * self.DISCRETE_TIMESTEP * 60)
        if not is_on_chain:
            entity.y_velocity += int(self.GRAVITY * remainder_time * 60)


class EntityRigidBodyComponent(PhysicsComponent):
    """Enables the entity to move based on its velocity
    and respond to collisions with other sprites."""

    def __init__(self, physics):
        super().__init__(physics)
        self.DISCRETE_TIMESTEP = 1 / 60

    def update(self, entity, delta_time, game_map):
        num_full_steps = int(delta_time / self.DISCRETE_TIMESTEP)
        remainder_time = delta_time % self.DISCRETE_TIMESTEP
        for i in range(0, num_full_steps):
            entity.rect.y += int(entity.y_velocity * self.DISCRETE_TIMESTEP)
            self.handle_y_collisions(entity, game_map)
            entity.rect.x += int(entity.x_velocity * self.DISCRETE_TIMESTEP)
            self.handle_x_collisions(entity, game_map)
        entity.rect.y += int(entity.y_velocity * remainder_time)
        if int(entity.y_velocity * remainder_time) != 0:
            self.handle_y_collisions(entity, game_map)
        entity.rect.x += int(entity.x_velocity * remainder_time)
        self.handle_x_collisions(entity, game_map)
        self.handle_map_boundary_collisions(entity, game_map)

    @staticmethod
    def handle_y_collisions(entity, map):
        """Handles collisions between entity and the terrain along the y-axis."""
        colliding_sprites = pg.sprite.spritecollide(
            entity, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            if is_colliding_from_below(entity, colliding_sprite):
                entity.rect.top = colliding_sprite.rect.bottom
                entity.set_y_velocity(0)
            if is_colliding_from_above(entity, colliding_sprite):
                is_crushed = colliding_sprite.rect.bottom < entity.rect.centery
                if is_crushed:
                    entity.message(EntityMessage.DIE)
                else:
                    if entity.get_state() is EntityState.JUMPING:
                        entity.set_state(EntityState.IDLE)
                    entity.rect.bottom = colliding_sprite.rect.top
                    entity.set_y_velocity(0)

    @staticmethod
    def handle_x_collisions(entity, map):
        """Handles collisions between entity and the terrain along the x-axis."""
        colliding_sprites = pg.sprite.spritecollide(
            entity, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            if not colliding_sprite.is_spike:
                if is_colliding_from_right(entity, colliding_sprite):
                    entity.rect.left = colliding_sprite.rect.right
                    entity.message(EntityMessage.AI_TURN_RIGHT)
                if is_colliding_from_left(entity, colliding_sprite):
                    entity.rect.right = colliding_sprite.rect.left
                    entity.message(EntityMessage.AI_TURN_LEFT)

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


def is_colliding_from_below(entity, colliding_sprite):
    return colliding_sprite.rect.top <= entity.rect.top <= colliding_sprite.rect.bottom


def is_colliding_from_above(entity, colliding_sprite):
    return colliding_sprite.rect.top <= entity.rect.bottom <= colliding_sprite.rect.bottom


def is_colliding_from_right(entity, colliding_sprite):
    return colliding_sprite.rect.left <= entity.rect.left <= colliding_sprite.rect.right


def is_colliding_from_left(entity, colliding_sprite):
    return colliding_sprite.rect.left <= entity.rect.right <= colliding_sprite.rect.right

