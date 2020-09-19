import pygame as pg
from pygame.surface import Surface
from .entitystate import Direction, GameEvent, EntityState, EntityMessage


class Component:
    """Components determine the behavior of the Entity
    which contains it. Most Components are reusable, as
    they do not contain information on state."""

    def __init__(self):
        pass

    def update(self, *args):
        # TODO: All update methods should have no arguments as all
        #  the relevant information should be stored as attributes.
        pass

    def receive(self, *args):
        pass


class RenderComponent(Component):
    def __init__(self):
        super().__init__()

    def update(self, entity, camera, game_display: Surface):
        # TODO: Abstract away all the blit_rect logic
        rendered_image = entity.image.subsurface(entity.blit_rect)
        if entity.get_direction() is Direction.LEFT:
            # Flip image if Player is moving backward
            rendered_image = pg.transform.flip(rendered_image, True, False)
        blit_destination = (entity.rect.x - camera.rect.x, entity.rect.y - camera.rect.y)
        game_display.blit(rendered_image, blit_destination)


class SoundComponent(Component):
    def __init__(self, sounds):
        super().__init__()
        self.sounds = sounds

    def receive(self, message):
        if message is EntityMessage.JUMP:
            self.sounds["JUMP"].play()
        elif message is EntityMessage.HIT:
            self.sounds["HIT"].play()


class DamageComponent(Component):

    def __init__(self, entity, immunity_time=500, enemy_damage=20):
        super().__init__()
        self.entity = entity
        self.last_collide_time = 0
        self.IMMUNITY_TIME = immunity_time
        self.ENEMY_DAMAGE = enemy_damage

    def is_immune(self):
        return self.last_collide_time > pg.time.get_ticks() - self.IMMUNITY_TIME

    def inflict_damage(self):
        self.entity.health -= self.ENEMY_DAMAGE
        self.last_collide_time = pg.time.get_ticks()
        self.entity.message(EntityMessage.HIT)
        self.entity.y_velocity = -2
        if self.entity.health <= 0:
            self.entity.set_state(EntityState.DEAD)
            pg.event.post(pg.event.Event(GameEvent.GAME_OVER.value))

    def receive(self, message):
        if message is EntityMessage.HIT:
            if not self.is_immune():
                self.inflict_damage()


class EnemyDamageComponent(Component):
    """Handles the situations in which the enemy would take damage in health."""

    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def update(self, player, map):
        self.take_damage_if_stomped_by_player(player)
        self.take_damage_if_crushed_by_terrain(map)

    def take_damage_if_stomped_by_player(self, player):
        has_collided_with_player = self.enemy.rect.colliderect(player.rect)
        if has_collided_with_player:
            is_stomped_by_player = player.rect.bottom < self.enemy.rect.centery \
                                   and player.y_velocity > 0
            if is_stomped_by_player:
                self.enemy.take_damage(100)
            else:
                player.take_damage(20)

    def take_damage_if_crushed_by_terrain(self, map):
        colliding_sprites = pg.sprite.spritecollide(
            self.enemy, map.collideable_terrain_group, False)
        for colliding_sprite in colliding_sprites:
            is_crushed_by_terrain = \
                colliding_sprite.rect.bottom \
                < self.enemy.rect.centery
            if is_crushed_by_terrain:
                self.enemy.take_damage(100)
