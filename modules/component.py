import pygame as pg
from pygame.surface import Surface
from .entitystate import GameEvent, EntityState, EntityMessage


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


class SoundComponent(Component):
    def __init__(self, sounds):
        super().__init__()
        self.sounds = sounds

    def receive(self, message):
        if message is EntityMessage.JUMP:
            self.sounds["JUMP"].play()
        if message is EntityMessage.DECREMENT_HEALTH:
            self.sounds["DECREMENT_HEALTH"].play()


class DeathComponent(Component):
    """Handles the situations in which an entity dies."""

    def __init__(self, entity, is_game_over=True):
        super().__init__()
        self.entity = entity
        self.is_game_over = is_game_over

    def die(self):
        self.entity.set_state(EntityState.DEAD)
        if self.is_game_over:
            pg.event.post(pg.event.Event(GameEvent.GAME_OVER.value))

    def update(self, map):
        has_fallen_out_of_map = self.entity.rect.top > map.rect.bottom
        if has_fallen_out_of_map:
            self.die()

    def receive(self, message):
        if message is EntityMessage.DIE:
            self.die()


class HealthComponent(Component):
    """Handles the situations in which a player would take damage in health."""

    def __init__(self, entity):
        super().__init__()
        self.entity = entity
        self.last_collide_time = 0
        self.MAX_HEALTH = 100
        self.health = self.MAX_HEALTH
        self.IMMUNITY_TIME = 500
        self.ENEMY_DAMAGE = 20
        self.SPIKE_DAMAGE = 20
        self.COIN_REPLENISHMENT = 20

    def update(self):
        if self.health <= 0:
            self.entity.message(EntityMessage.DIE)

    def receive(self, message):
        if message is EntityMessage.RECEIVE_COIN:
            self.take_replenishment(self.COIN_REPLENISHMENT)
        if message is EntityMessage.ENEMY_HIT:
            self.take_damage(self.ENEMY_DAMAGE)
        if message is EntityMessage.LAND_ON_SPIKE:
            self.take_damage(self.SPIKE_DAMAGE)

    def take_damage(self, damage):
        if not self.is_immune():
            self.health -= damage
            self.last_collide_time = pg.time.get_ticks()
            self.entity.message(EntityMessage.DECREMENT_HEALTH)

    def take_replenishment(self, replenishment):
        if self.health < self.MAX_HEALTH:
            self.health += replenishment

    def is_immune(self):
        return self.last_collide_time > pg.time.get_ticks() - self.IMMUNITY_TIME

    def get_current_health(self):
        return self.health

    def get_max_health(self):
        return self.MAX_HEALTH


class EnemyCombatComponent(Component):
    """Handles the interactions between a player and the enemy."""

    def __init__(self, enemy):
        self.enemy = enemy

    def update(self, player):
        has_collided_with_player = self.enemy.rect.colliderect(player.rect)
        if has_collided_with_player:
            is_stomped_by_player = player.rect.bottom < self.enemy.rect.centery \
                                   and player.y_velocity > 0
            if is_stomped_by_player:
                self.enemy.message(EntityMessage.DIE)
            else:
                player.message(EntityMessage.ENEMY_HIT)


class RenderComponent(Component):

    def __init__(self):
        super().__init__()

    def update(self, entity, camera, game_display: Surface):
        # rendered_image = entity.image
        rendered_image = entity.image.subsurface(entity.blit_rect)
        blit_destination = (entity.rect.x - camera.rect.x, entity.rect.y - camera.rect.y)
        game_display.blit(rendered_image, blit_destination)
