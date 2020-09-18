import pygame as pg
from pygame.surface import Surface
from modules.entitystate import Direction


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
        if message is "JUMP":
            self.sounds["JUMP"].play()
        elif message is "HIT":
            self.sounds["HIT"].play()


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
                # TODO: Abstract all player damage logic into a Component
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
