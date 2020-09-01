import pygame as pg
from .entitystate import GameEvent, EntityState, Direction
from .spritesheet import Spritesheet
from .components import PlayerInputComponent, PlayerAnimationComponent, PlayerPhysicsComponent, \
                        SoundComponent, RenderComponent, EnemyDamageCollisionComponent, \
                        EnemyDamageCrushComponent

"""
* =============================================================== *
* This module contains all relevant classes required for the      *
* instantiation of the Player and Enemies.                        *
* =============================================================== *

HOW TO MAKE A NEW ENEMY VARIANT
-------------------------
1.  Make a new EnemyType object with the following public attributes:
        health: int                 ->      Maximum health of the Enemy
        animation_library: dict     ->      Dictionary containing the different 
                                            animation sequences to be played 
                                            for each state
        sound_library: dict         ->      Dictionary containing the different
                                            sounds to be played for each state
2.  Conduct manual inspection to determine the best width, height and hit_rect 
    attribute for the EnemyType.
3.  Pass this EnemyType object to the Enemy constructor to instantiate a new variant 
    of Enemy
"""


class Entity(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Defines the hitbox of the Entity. Must be redefined in the subclass.
        self.rect = None                   

        # Velocities
        self.x_velocity = 0              
        self.y_velocity = 0

        # Direction which the Entity is facing
        self.direction = Direction.RIGHT

        # State of the entity  
        self.state = EntityState.IDLE

    def update(self, *args):
        raise NotImplementedError


class Player(Entity):
    """Represents the player character"""
    def __init__(self):
        super().__init__()
        self.health = 100
        self.rect = pg.Rect(10, 10, 20, 30)
        # blit rect x coord changed from 50 to 30
        self.blit_rect = pg.Rect(15, 3.5, 20, 30)
        self.last_collide_time = 0

        # Spritesheets
        idle_spritesheet = Spritesheet("assets/textures/player/adventurer-idle.png", 1, 4)
        run_spritesheet = Spritesheet("assets/textures/player/adventurer-run.png", 1, 6)
        jump_spritesheet = Spritesheet("assets/textures/player/adventurer-jump.png", 1, 1)
        climb_spritesheet = Spritesheet("assets/textures/player/adventurer-climb.png", 1, 4)

        # Animations
        animation_library = {
                            EntityState.IDLE: idle_spritesheet.get_images_at(0, 1, 2, 3),
                            EntityState.WALKING: run_spritesheet.get_images_at(0, 1, 2, 3, 4, 5),
                            EntityState.JUMPING: jump_spritesheet.get_images_at(0),
                            EntityState.HANGING: climb_spritesheet.get_images_at(0),
                            EntityState.CLIMBING: climb_spritesheet.get_images_at(0, 1, 2, 3)
                            }

        # Sounds
        jump_sound = pg.mixer.Sound("assets/sound/sfx/jump.ogg")
        hit_sound = pg.mixer.Sound("assets/sound/sfx/hitdamage.ogg")

        sound_library = {
                         "JUMP": jump_sound,
                         "HIT": hit_sound
                        }

        # Components
        self.input_component = PlayerInputComponent()
        self.animation_component = PlayerAnimationComponent(animation_library, self.state)
        self.physics_component = PlayerPhysicsComponent()
        self.sound_component = SoundComponent(sound_library)
        self.render_component = RenderComponent()

        # Current Image
        self.image = self.animation_component.get_current_image()

    # ---------- DIRTY METHODS ---------- #
    # These will be placed here until I can find a way to wrap them in a component nicely
    def take_damage(self, damage):
        """Decreases the health of the player by the specified amount"""
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
        # Apart from sound, can force animation to receive animations too
        # But it is too much work to do animation, so we will not do that
        self.sound_component.receive(message)

    def handle_input(self):
        self.input_component.update(self)

    def update(self, delta_time, map):
        if self.rect.top > map.rect.bottom:
            self.state = EntityState.DEAD
            pg.event.post(
                pg.event.Event(
                    GameEvent.GAME_OVER.value
                )
            )
        else:
            self.physics_component.update(delta_time, self, map)
            self.animation_component.update(self)

    def render(self, camera, surface):
        self.render_component.update(self, camera, surface)


class Enemy(Entity):
    """Base class for all enemies"""
    def __init__(self,
                 type_object,
                 ai_component,
                 physics_component,
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
        self.physics_component = physics_component
        self.render_component = render_component

        self.damage_collide_component = EnemyDamageCollisionComponent()
        self.damage_crush_component = EnemyDamageCrushComponent()

        # Animation and sound are taken from a type object
        self.animation_component = PlayerAnimationComponent(type_object.animation_library, self.state)
        self.sound_component = SoundComponent(type_object.sound_library)

        # Define starting position
        # index 0 is x position, index 1 is y position, index 2 is patrol range
        self.rect = type_object.rect
        self.rect.x = starting_position[0]
        self.rect.y = starting_position[1]
        self.blit_rect = type_object.blit_rect

        self.image = self.animation_component.get_current_image()

    def take_damage(self, damage):
        """Instantly kills the enemy"""
        # TODO: Properly handle animations for dying
        self.state = EntityState.DEAD

    def message(self, message):
        pass
    
    def update(self,delta_time, map, player):
        self.input_component.update(self, map)
        self.physics_component.update(delta_time, self, map)
        self.damage_collide_component.update(self, player)
        self.damage_crush_component.update(self, map)
        self.animation_component.update(self)

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
            EntityState.IDLE: idle_spritesheet.get_images_at(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            EntityState.WALKING: run_spritesheet.get_images_at(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
            EntityState.JUMPING: jump_spritesheet.get_images_at(0),
            EntityState.DEAD: idle_spritesheet.get_images_at(0)
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
            EntityState.IDLE: idle_spritesheet.get_images_and_flip(0, 1, 2, 3, 4, 5),
            EntityState.WALKING: run_spritesheet.get_images_and_flip(0, 1, 2, 3, 4, 5),
            EntityState.JUMPING: jump_spritesheet.get_images_and_flip(0),
            EntityState.DEAD: idle_spritesheet.get_images_and_flip(0)
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

        self.animation_library = {
            EntityState.IDLE: walk_spritesheet.get_images_at(0),
            EntityState.WALKING: walk_spritesheet.get_images_at(0, 1, 2, 3, 4, 5),
            EntityState.JUMPING: walk_spritesheet.get_images_at(0),
            EntityState.DEAD: dead_spritesheet.get_images_at(0)
        }
