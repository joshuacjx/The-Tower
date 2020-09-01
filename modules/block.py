import pygame as pg
from .components import SimpleAnimationComponent
from .entitystate import GameEvent, EntityState, Direction
from .spritesheet import Spritesheet, TerrainType

"""
* =============================================================== *
* This module contains Blocks, which are representations of the   *
* individual tiles of the game map.								  *
* =============================================================== *

"""


class Block(pg.sprite.Sprite):
    BLOCK_SIZE = 25

    def __init__(self, type_object: TerrainType, x, y):
        super().__init__()
        self.image = pg.transform.scale(type_object.image.convert_alpha(),
                                        (int(type_object.block_width * Block.BLOCK_SIZE),
                                         int(type_object.block_height * Block.BLOCK_SIZE))
                                        )
        self.rect = pg.Rect(x + int(type_object.block_pos_x * Block.BLOCK_SIZE),
                            y + int(type_object.block_pos_y * Block.BLOCK_SIZE),
                            int(type_object.block_width * Block.BLOCK_SIZE),
                            int(type_object.block_height * Block.BLOCK_SIZE))
        self.is_spike = False


class SpikeBlock(Block):
    """Represents a block that damages the player if the player comes into contact with it"""

    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        self.is_spike = True

    def update(self, entity, *args):
        """Checks for collision between the player and the Hazardous Block, and damages the player upon colliding"""

        if self.rect.colliderect(entity.rect):
            # Since spikes are always at the bottom, the player must always come from the top
            entity.rect.bottom = self.rect.top

        if (self.rect.left < entity.rect.left < self.rect.right or self.rect.left < entity.rect.right < self.rect.right) \
                and self.rect.top == entity.rect.bottom:
            entity.take_damage(20)



class GatewayBlock(Block):
    """Represents the endpoint of the level"""

    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)

    def update(self, player, terrain_group):
        """Checks if the player has collided with itself, and initiates a level transition if there is a collision"""
        if player.rect.collidepoint(self.rect.centerx, self.rect.centery):
            pg.event.post(
                pg.event.Event(
                    GameEvent.SWITCH_LEVEL.value
                )
            )


# Has potential for many variations
class FallingBlock(Block):
    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        self.vel = 1
        self.fallen = False

    def update(self, player, terrain_group):
        if (self.rect.top == player.rect.bottom) and not self.fallen \
                and (self.rect.left < player.rect.left < self.rect.right
                     or self.rect.left < player.rect.right < self.rect.right):
            self.rect.y += self.vel

            # This is necessary - or else, player will fluctuate between the IDLE and JUMPING state
            # causing it to flash
            player.rect.bottom = self.rect.top

        # If the FallingBlock falls on a Block
        for colliding_sprite in pg.sprite.spritecollide(self, terrain_group, False):
                if colliding_sprite.rect.top < self.rect.bottom < colliding_sprite.rect.bottom:
                    self.rect.bottom = colliding_sprite.rect.top
                    self.fallen = True

        # Block should also fall when a pushable block falls on it
        # Commented this out because it is still buggy - player's state will fluctuate rapidly

        # for pushable in pushable_group:
        # 	if (self.rect.top == pushable.rect.bottom)\
        # 		and (self.rect.left < pushable.rect.left < self.rect.right\
        # 			or self.rect.left < pushable.rect.right < self.rect.right\
        # 				or self.rect.left < pushable.rect.centerx < self.rect.right):
        # 		self.blit_rect.y += self.vel
        # 		self.rect.y = self.blit_rect.y
        # 		pushable.rect.bottom = self.rect.top
        # 		pushable.blit_rect.bottom = pushable.rect.bottom


class MovingBlock(Block):
    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        self.vel = 1

    def update(self, player, *args):
        if ((self.rect.top == player.rect.bottom) \
            and (self.rect.left < player.rect.left < self.rect.right \
                 or self.rect.left < player.rect.right < self.rect.right)) \
                and (player.state != EntityState.HANGING and player.state != EntityState.CLIMBING):

            if player.direction == Direction.LEFT:
                self.rect.x -= self.vel
                player.rect.x = self.rect.x

            if player.direction == Direction.RIGHT:
                self.rect.x += self.vel
                player.rect.x = self.rect.x

            if pg.key.get_pressed()[pg.K_UP]:
                self.rect.y -= self.vel
                player.rect.bottom = self.rect.top

            elif pg.key.get_pressed()[pg.K_DOWN]:
                self.rect.y += self.vel
                player.rect.bottom = self.rect.top


class Coin(Block):
    """Represents a coin which heals the player when picked up"""

    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        spritesheet = Spritesheet("assets/textures/environment/animated/ruby.png", 1, 16)
        coin_animation = spritesheet.get_images_at(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        self.animation_component = SimpleAnimationComponent(coin_animation)
        self.coin_sound = pg.mixer.Sound("assets/sound/sfx/coin.ogg")

    def update(self, entity, *args):
        """Checks if the player has collided with the coin, healing the player if there is a collision,
        and updates the animation of the coin"""
        if pg.sprite.collide_rect(self, entity):
            if entity.health < 100:
                entity.health += 20
            self.coin_sound.play()
            self.kill()

        self.animation_component.update(self)


class LadderBlock(Block):
    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        self.mid_rect = pg.Rect(self.rect.centerx - 0.5, self.rect.top, 1, self.rect.height)

    def update(self, entity, *args):
        current_keys = pg.key.get_pressed()
        if self.mid_rect.colliderect(entity.rect) and entity.state != EntityState.JUMPING:
            if current_keys[pg.K_UP] or current_keys[pg.K_DOWN]:
                # Snap player to middle of ladder when entering HANGING state
                entity.rect.centerx = self.mid_rect.centerx
                entity.state = EntityState.HANGING


class PushableBlock(Block):
    def __init__(self, type_object, x, y):
        super().__init__(type_object, x, y)
        self.y_velocity = 1
        self.gravity = 1

    # A pushable block reacts to gravity, hence it interacts with both the player and terrain group
    # In future, possible to make one superclass for all blocks that are affected by gravity and collides with other
    # blocks
    def update(self, player, terrain_group):

        # If player is pushing the block
        if (self.rect.left == player.rect.right or self.rect.right == player.rect.left) \
                and player.state == EntityState.WALKING \
                and player.rect.bottom == self.rect.bottom:
            # FIXME: Block movement speed varies with FPS
            # Reason is bc the block is in the collideable terrain group
            # Hence every update cycle, the colliding player will be at the same distance from the block
            # and the speed therefore depends on the rate of update
            # The ideal solution is to add a delta_time field to the arguments, but nah
            # The hack is to let the block handle its own collision separately
            # The broke method is to ignore this since it is slightly discernible at normal speeds of 30 - 60 fps
            self.rect.x += (self.rect.centerx - player.rect.centerx) / 20

        for colliding_sprite in pg.sprite.spritecollide(self, terrain_group, False):
            if colliding_sprite.rect.left < self.rect.left < colliding_sprite.rect.right:
                self.rect.left = colliding_sprite.rect.right
            if colliding_sprite.rect.left < self.rect.right < colliding_sprite.rect.right:
                self.rect.right = colliding_sprite.rect.left

        self.y_velocity += self.gravity
        self.rect.y += self.y_velocity
        isFloating = True
        for colliding_sprite in pg.sprite.spritecollide(self, terrain_group, False):
            if colliding_sprite.rect.top < self.rect.top < colliding_sprite.rect.bottom:
                self.rect.top = colliding_sprite.rect.bottom
                self.y_velocity = 0
            if colliding_sprite.rect.top < self.rect.bottom < colliding_sprite.rect.bottom:
                isFloating = False
                self.rect.bottom = colliding_sprite.rect.top
                self.y_velocity = 0
