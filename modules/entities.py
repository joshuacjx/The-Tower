import pygame as pg
from .entitystate import GameEvent, EntityState, Direction, EntityMessage
from .animation import EntityAnimationComponent
from .component import SoundComponent, RenderComponent, EnemyDamageComponent, DamageComponent
from .physics import UserControlComponent, EntityGravityComponent, EntityRigidBodyComponent, EnemyRigidBodyComponent
from .libraries import Library


class Entity(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.rect = None
        self.x_velocity = 0              
        self.y_velocity = 0
        self.direction = Direction.RIGHT
        self.state = EntityState.IDLE

    def update(self, *args):
        raise NotImplementedError

    def message(self, message):
        raise NotImplementedError

    def set_x_velocity(self, new_x_velocity):
        self.x_velocity = new_x_velocity

    def reverse_x_velocity(self):
        self.x_velocity = -self.x_velocity

    def set_y_velocity(self, new_y_velocity):
        self.y_velocity = new_y_velocity

    def get_direction(self):
        return self.direction

    def set_direction(self, new_direction: Direction):
        self.direction = new_direction

    def reverse_direction(self):
        self.set_direction(self.get_direction().get_reverse())

    def get_state(self):
        return self.state

    def set_state(self, new_state: EntityState):
        self.state = new_state


class Player(Entity):

    def __init__(self):
        super().__init__()
        self.health = 100
        self.rect = pg.Rect(10, 10, 20, 30)
        self.blit_rect = pg.Rect(15, 3.5, 20, 30)

        self.input_component = UserControlComponent(self)
        self.animation_component = EntityAnimationComponent(self, Library.player_animations)
        self.sound_component = SoundComponent(Library.entity_sounds)
        self.render_component = RenderComponent()
        self.damage_component = DamageComponent(self)
        self.gravity_component = EntityGravityComponent()
        self.rigid_body_component = EntityRigidBodyComponent()
        self.image = self.animation_component.get_initial_image()

    def message(self, message: EntityMessage):
        self.sound_component.receive(message)
        self.damage_component.receive(message)

    def update(self, delta_time, map):
        if self.rect.top > map.rect.bottom:
            self.state = EntityState.DEAD
            pg.event.post(
                pg.event.Event(
                    GameEvent.GAME_OVER.value
                )
            )
        else:
            self.input_component.update()
            self.animation_component.update()
            self.gravity_component.update(self, delta_time)
            self.rigid_body_component.update(self, delta_time, map)

    def render(self, camera, surface):
        self.render_component.update(self, camera, surface)


class Enemy(Entity):

    def __init__(self,
                 type_object,
                 ai_component,
                 render_component,
                 starting_position,
                 patrol_radius=25
                 ):
        super().__init__()

        self.health = 100

        # Boundaries for patrol
        self.left_bound = starting_position[0] - patrol_radius
        self.right_bound = starting_position[0] + patrol_radius

        self.input_component = ai_component
        self.render_component = render_component
        self.damage_component = EnemyDamageComponent(self)
        self.gravity_component = EntityGravityComponent()
        self.rigid_body_component = EnemyRigidBodyComponent()
        self.animation_component = EntityAnimationComponent(self, type_object.animation_library)
        self.sound_component = SoundComponent(type_object.sound_library)

        # Define starting position
        # index 0 is x position, index 1 is y position, index 2 is patrol range
        self.rect = type_object.rect
        self.rect.x = starting_position[0]
        self.rect.y = starting_position[1]
        self.blit_rect = type_object.blit_rect

        self.image = self.animation_component.get_initial_image()

    def take_damage(self, damage):
        """Instantly kills the enemy"""
        # TODO: Properly handle animations for dying
        self.state = EntityState.DEAD

    def message(self, message):
        pass
    
    def update(self, delta_time, map, player):
        self.input_component.update(self, map)
        self.gravity_component.update(self, delta_time)
        self.rigid_body_component.update(self, delta_time, map)
        self.damage_component.update(player, map)
        self.animation_component.update()

    def render(self, camera, surface):
        self.render_component.update(self, camera, surface)


class EnemyType:
    """Template object representing the type of enemy, which
    is passed into the Enemy constructor to instantiate an
    Enemy with the corresponding visuals, health and sounds."""

    def __init__(self):
        self.health = 100
        self.animation_library = {}
        self.sound_library = Library.entity_sounds


class PinkGuy(EnemyType):
    def __init__(self):
        super().__init__()
        width = 32
        height = 32
        self.rect = pg.Rect(0, 0, width, height)
        self.blit_rect = pg.Rect(0, 0, width, height)
        self.animation_library = Library.pink_guy_animations


class TrashMonster(EnemyType):
    def __init__(self):
        super().__init__()
        self.rect = pg.Rect(0, 0, 35, 32)
        self.blit_rect = pg.Rect(4, 0, 35, 32)
        self.animation_library = Library.trash_monster_animations


class ToothWalker(EnemyType):
    def __init__(self):
        super().__init__()
        self.rect = pg.Rect(0, 0, 30, 65)
        self.blit_rect = pg.Rect(40, 0, 30, 65)
        self.animation_library = Library.tooth_walker_animations
