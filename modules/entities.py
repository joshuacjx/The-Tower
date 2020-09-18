import pygame as pg
from .entitystate import GameEvent, EntityState, Direction
from .spritesheet import Spritesheet
from .animation import Animation, EntityAnimationComponent
from modules.component import SoundComponent, RenderComponent, EnemyDamageComponent
from modules.physics import UserControlComponent, PhysicsComponent, EntityGravityComponent, EntityRigidBodyComponent


class Entity(pg.sprite.Sprite):
    """Players and Enemies are defined as Entities in the game. Entities have
    their position stored in their rect attribute, which is updated every frame
    according to its x- and y-velocities. They also have states enumerated in the
    class EntityState. The Entity class defines functions to access and modify
    the Entity's state, direction and velocities."""

    def __init__(self):
        # TODO: Make velocity, direction and state information private
        # TODO: Entities should have methods that support the modification
        #  of its attributes. Components should call these methods instead
        #  of directly accessing these attributes.

        super().__init__()

        self.rect = None
        """Defines the entity's position."""

        self.x_velocity = 0              
        self.y_velocity = 0
        self.direction = Direction.RIGHT
        self.state = EntityState.IDLE

    def update(self, *args):
        raise NotImplementedError

    def message(self, message):
        pass

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
        if self.direction is Direction.LEFT:
            self.direction = Direction.RIGHT
        elif self.direction is Direction.RIGHT:
            self.direction = Direction.LEFT

    def get_state(self):
        return self.state

    def set_state(self, new_state: EntityState):
        self.state = new_state


class Player(Entity):
    """Represents the player character"""

    def __init__(self):
        super().__init__()
        self.health = 100
        self.rect = pg.Rect(10, 10, 20, 30)
        # blit rect x coord changed from 50 to 30
        self.blit_rect = pg.Rect(15, 3.5, 20, 30)
        self.last_collide_time = 0

        idle_spritesheet = Spritesheet("assets/textures/player/adventurer-idle.png", 1, 4)
        run_spritesheet = Spritesheet("assets/textures/player/adventurer-run.png", 1, 6)
        jump_spritesheet = Spritesheet("assets/textures/player/adventurer-jump.png", 1, 1)
        climb_spritesheet = Spritesheet("assets/textures/player/adventurer-climb.png", 1, 4)
        animation_library = {
                            EntityState.IDLE: Animation(idle_spritesheet, 0, 3),
                            EntityState.WALKING: Animation(run_spritesheet, 0, 5),
                            EntityState.JUMPING: Animation(jump_spritesheet, 0, 0),
                            EntityState.HANGING: Animation(climb_spritesheet, 0, 0),
                            EntityState.CLIMBING: Animation(climb_spritesheet, 0, 3)
                            }

        # Sounds
        jump_sound = pg.mixer.Sound("assets/sound/sfx/jump.ogg")
        hit_sound = pg.mixer.Sound("assets/sound/sfx/hitdamage.ogg")

        sound_library = {
                         "JUMP": jump_sound,
                         "HIT": hit_sound
                        }

        # Components
        self.input_component = UserControlComponent(self)
        self.animation_component = EntityAnimationComponent(self, animation_library)
        self.sound_component = SoundComponent(sound_library)
        self.render_component = RenderComponent()
        self.gravity_component = EntityGravityComponent()
        self.rigid_body_component = EntityRigidBodyComponent()

        # Current Image
        self.image = self.animation_component.get_initial_image()

    def take_damage(self, damage):
        """Decreases the health of the player by the specified amount"""
        # TODO: Abstract the damage logic into a component
        if self.is_immune():
            return
        else:
            self.health -= damage
            self.last_collide_time = pg.time.get_ticks()
            self.message("HIT")
            self.y_velocity = -2

        if self.health <= 0:
            self.state = EntityState.DEAD
            pg.event.post(
                pg.event.Event(
                    GameEvent.GAME_OVER.value
                )
            )

    def is_immune(self):
        return self.last_collide_time > pg.time.get_ticks() - 500

    def message(self, message):
        self.sound_component.receive(message)

    def handle_input(self):
        self.input_component.update()

    def update(self, delta_time, map):
        if self.rect.top > map.rect.bottom:
            self.state = EntityState.DEAD
            pg.event.post(
                pg.event.Event(
                    GameEvent.GAME_OVER.value
                )
            )
        else:
            self.animation_component.update()
            self.gravity_component.update(self, delta_time)
            self.rigid_body_component.update(self, delta_time, map)

    def render(self, camera, surface):
        self.render_component.update(self, camera, surface)


class Enemy(Entity):
    """Base class for all enemies"""
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
        self.rigid_body_component = EntityRigidBodyComponent()
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
        self.input_component.update(self)
        self.gravity_component.update(self, delta_time)
        self.rigid_body_component.update(self, delta_time, map)
        self.damage_component.update(player, map)
        self.animation_component.update()

    def render(self, camera, surface):
        self.render_component.update(self, camera, surface)


class EnemyType:
    """Template object representing the type of enemy, which is passed into the Enemy constructor to
        instantiate an Enemy with the corresponding visuals, health and sounds"""
    def __init__(self):
        self.health = 100
        self.animation_library = {}

        jump_sound = pg.mixer.Sound("assets/sound/sfx/jump.ogg")
        self.sound_library = {
            "JUMP": jump_sound
        }


class PinkGuy(EnemyType):
    def __init__(self):
        super().__init__()

        # Figure out these attributes via inspection every time a new enemy type is implemented
        width = 32
        height = 32
        self.rect = pg.Rect(0, 0, width, height)
        self.blit_rect = pg.Rect(0, 0, width, height)

        idle_spritesheet = Spritesheet("assets/textures/enemies/Pink Guy/Idle.png", 1, 11)
        run_spritesheet = Spritesheet("assets/textures/enemies/Pink Guy/Run.png", 1, 12)
        jump_spritesheet = Spritesheet("assets/textures/enemies/Pink Guy/Jump.png", 1, 1)
        self.animation_library = {
            EntityState.IDLE: Animation(idle_spritesheet, 0, 10),
            EntityState.WALKING: Animation(run_spritesheet, 0, 11),
            EntityState.JUMPING: Animation(jump_spritesheet, 0, 0),
            EntityState.DEAD: Animation(idle_spritesheet, 0, 0)
        }


class TrashMonster(EnemyType):
    def __init__(self):
        super().__init__()
        image_width = 44
        image_height = 32
        self.rect = pg.Rect(0, 0, 35, 32)
        self.blit_rect = pg.Rect(4, 0, 35, 32)

        idle_spritesheet = Spritesheet("assets/textures/enemies/Trash Monster/Trash Monster-Idle.png", 1, 6)
        run_spritesheet = Spritesheet("assets/textures/enemies/Trash Monster/Trash Monster-Run.png", 1, 6)
        jump_spritesheet = Spritesheet("assets/textures/enemies/Trash Monster/Trash Monster-Jump.png", 1, 1)

        idle_spritesheet.scale_images_to_size(image_width, image_height)
        run_spritesheet.scale_images_to_size(image_width, image_height)
        jump_spritesheet.scale_images_to_size(image_width, image_height)

        self.animation_library = {
            EntityState.IDLE: Animation(idle_spritesheet, 0, 5, flip=True),
            EntityState.WALKING: Animation(run_spritesheet, 0, 5, flip=True),
            EntityState.JUMPING: Animation(jump_spritesheet, 0, 0, flip=True),
            EntityState.DEAD: Animation(idle_spritesheet, 0, 0, flip=True)
        }


class ToothWalker(EnemyType):
    def __init__(self):
        super().__init__()
        image_width = 100
        image_height = 65
        self.rect = pg.Rect(0, 0, 30, 65)
        self.blit_rect = pg.Rect(40, 0, 30, 65)

        walk_spritesheet = Spritesheet("assets/textures/enemies/Tooth Walker/tooth walker walk.png", 1, 6)
        dead_spritesheet = Spritesheet("assets/textures/enemies/Tooth Walker/tooth walker dead.png", 1, 1)

        walk_spritesheet.scale_images_to_size(image_width, image_height)
        dead_spritesheet.scale_images_to_size(image_width, image_height)

        self.animation_library = \
            {
            EntityState.IDLE: Animation(walk_spritesheet, 0, 0),
            EntityState.WALKING: Animation(walk_spritesheet, 0, 5),
            EntityState.JUMPING: Animation(walk_spritesheet, 0, 0),
            EntityState.DEAD: Animation(dead_spritesheet, 0, 0)
            }
