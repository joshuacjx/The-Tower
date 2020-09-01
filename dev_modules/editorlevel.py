import pygame as pg
import json
from modules.block import Block
from modules.textureset import TextureSet
from modules.leveljson import Map
from modules.entities import Player, PinkGuy, TrashMonster, ToothWalker
from modules.entitystate import EntityState


class EditorLevel:
    """Level class with additional methods for customising the level"""
    def __init__(self, filepath: str, dimensions):
        # loads the json file from the specified filepath
        if filepath is None:
            cols = int(dimensions[0])
            rows = int(dimensions[1])
            data = {
                "enemies": [],
                "map": {"background": [["  "] * cols] * rows,
                        "decorations": [["  "] * cols] * rows,
                        "terrain": [["  "] * cols] * rows
                        },
                "starting_position": [rows * Block.BLOCK_SIZE / 2,
                                      cols * Block.BLOCK_SIZE / 2]
            }
        else:
            with open(filepath) as f:
                data = json.load(f)

        self.enemies = EditorEnemyManager(data["enemies"])
        self.map = EditorMap(data["map"])
        starting_position = data["starting_position"]
        self.player = EditorPlayer(starting_position)

        # TOGGLES
        self.draw_enemies = True
        self.draw_player_starting_position = True

    def add(self, coordinates, layer, code):
        # validation only
        if layer == 5:
            self.player.rect.topleft = coordinates
        else:
            if layer == 4:
                self.enemies.add(coordinates, code)
            else:
                if len(code) == 2:
                    self.map.add(coordinates, layer, code)

    def delete(self, coordinates, layer):
        if layer != 5:
            if layer != 4:
                self.map.delete(coordinates, layer)
            else:
                self.enemies.delete(coordinates)

    def serialise_to_dict(self):
        starting_position = self.player.rect.topleft
        map = {
            "background": self.map.bg_array,
            "decorations": self.map.decorations_array,
            "terrain": self.map.terrain_array
        }
        enemies = self.enemies.serialise_to_list()

        return {"enemies": enemies,
                "map": map,
                "starting_position": starting_position
                }

    def render(self, camera, surface):
        self.map.render(camera, surface)
        if self.draw_enemies is True:
            self.enemies.render(camera, surface)
        if self.draw_player_starting_position is True:
            self.player.render(camera, surface)


class EditorMap(Map):
    """Essentially the same as the original Map, but Update() has been reworked to use different arguments"""
    def __init__(self, map_dict):
        super().__init__(map_dict)
        self.bg_array = map_dict["background"]
        self.decorations_array = map_dict["decorations"]
        self.terrain_array = map_dict["terrain"]

        self.bg_on = True
        self.decorations_on = True
        self.terrain_on = True

        self.texture_set = TextureSet()

        # basically layer 0 is bg, layer 1 is decorations, and layer 2 is terrain array.
        # bg controls the bg terrain group, deco controls the mg terrain group, and terrain controls the
        # collideable and interactive terrain groups

    def add(self, coordinates, layer, code: str):
        # input has already been validated
        row = int(coordinates[1] / Block.BLOCK_SIZE)
        col = int(coordinates[0] / Block.BLOCK_SIZE)

        if layer == 1:
            self.bg_array[row][col] = code
            # kill the sprite
            for sprite in self.background_terrain_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break
            # then add the new sprite in
            if code != "  ":
                self.background_terrain_group.add(Block(self.texture_set.get_texture_from_code(code),
                                                        col * Block.BLOCK_SIZE,
                                                        row * Block.BLOCK_SIZE))
        elif layer == 2:
            self.decorations_array[row][col] = code
            for sprite in self.middle_ground_terrain_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break

            if code != "  ":
                self.middle_ground_terrain_group.add(Block(self.texture_set.get_texture_from_code(code),
                                                           col * Block.BLOCK_SIZE,
                                                           row * Block.BLOCK_SIZE))
        elif layer == 3:
            self.terrain_array[row][col] = code
            for sprite in self.collideable_terrain_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break
            for sprite in self.interactive_objects_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break

            if code != "  ":
                # By right the group you add into doesnt matter here bc you cant update anyway lmao get rekt
                # so ill just add them all to collideable terrain
                # ffs you serialise from the array anyway
                new_block = Block(self.texture_set.get_texture_from_code(code),
                                  col * Block.BLOCK_SIZE,
                                  row * Block.BLOCK_SIZE)
                self.collideable_terrain_group.add(new_block)

    def delete(self, coordinates, layer):
        # replace both array and group
        row = int(coordinates[1] / Block.BLOCK_SIZE)
        col = int(coordinates[0] / Block.BLOCK_SIZE)

        if layer == 1:
            self.bg_array[row][col] = "  "
            for sprite in self.background_terrain_group:
                # Must click the starting locationn of the object before it can be deleted
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break
        elif layer == 2:
            self.decorations_array[row][col] = "  "
            for sprite in self.middle_ground_terrain_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break
        elif layer == 3:
            self.terrain_array[row][col] = "  "
            for sprite in self.collideable_terrain_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break
            for sprite in self.interactive_objects_group:
                if sprite.rect.collidepoint(coordinates):
                    sprite.kill()
                    break

    def render(self, camera, surface):
        if self.bg_on:
            for sprite in self.background_terrain_group:
                if camera.rect.colliderect(sprite.rect):
                    surface.blit(sprite.image,
                                 (sprite.rect.x - camera.rect.x, sprite.rect.y - camera.rect.y))

        if self.decorations_on:
            for sprite in self.middle_ground_terrain_group:
                if camera.rect.colliderect(sprite.rect):
                    surface.blit(sprite.image,
                                 (sprite.rect.x - camera.rect.x, sprite.rect.y - camera.rect.y))

        if self.terrain_on:
            for sprite in self.collideable_terrain_group:
                if camera.rect.colliderect(sprite.rect):
                    surface.blit(sprite.image,
                                 (sprite.rect.x - camera.rect.x, sprite.rect.y - camera.rect.y))

            for sprite in self.interactive_objects_group:
                if camera.rect.colliderect(sprite.rect):
                    surface.blit(sprite.image,
                                 (sprite.rect.x - camera.rect.x, sprite.rect.y - camera.rect.y))


class EditorEnemyManager:
    """Stripped-down enemy manager"""
    def __init__(self, enemies_list):
        # serialise from this list
        self.enemies_list = []
        self.enemy_type = {"Pink Guy": PinkGuy(),
                           "Trash Monster": TrashMonster(),
                           "Tooth Walker": ToothWalker()
                           }

        for enemy_dict in enemies_list:
            self.enemies_list.append(EditorEnemy(enemy_dict["type"],
                                                 self.enemy_type[enemy_dict["type"]],
                                                 enemy_dict["coordinates"]))

    def add(self, coordinates, code):
        # This line prevents the program from crashing if you accidentally add a block in the enemies layer
        if code == "Pink Guy" or code == "Trash Monster" or code == "Tooth Walker":
            self.enemies_list.append(EditorEnemy(code,
                                                 self.enemy_type[code],
                                                 coordinates))

    def delete(self, coordinates):
        for enemy in self.enemies_list:
            if enemy.rect.collidepoint(coordinates):
                self.enemies_list.remove(enemy)

    def serialise_to_list(self):
        """Converts the state of the manager to a JSON array equivalent in python (aka a list)"""
        output_list = []
        for enemy in self.enemies_list:
            output_list.append({"type": enemy.code,
                                "coordinates": [enemy.rect.x, enemy.rect.y]
                                }
                               )
        return output_list

    def render(self, camera, surface):
        for enemy in self.enemies_list:
            enemy.render(camera, surface)


class EditorPlayer:
    """Stripped-down player for use in the map editor"""
    def __init__(self, coordinates):
        player = Player()
        self.image = player.image
        self.rect = player.rect.copy()
        self.blit_rect = player.blit_rect
        self.rect.topleft = coordinates

    def render(self, camera, surface):
        if camera.rect.colliderect(self.rect):
            surface.blit(self.image,
                         (self.rect.x - camera.rect.x, self.rect.y - camera.rect.y),
                         self.blit_rect)


class EditorEnemy:
    """Stripped-down enemy for use in the map editor"""
    def __init__(self, code, type_object, coordinates):
        self.code = code
        self.image = type_object.animation_library[EntityState.IDLE][0]
        self.rect = type_object.rect.copy()
        self.blit_rect = type_object.blit_rect
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]

    def render(self, camera, surface):
        if camera.rect.colliderect(self.rect):
            surface.blit(self.image,
                         (self.rect.x - camera.rect.x, self.rect.y - camera.rect.y),
                         self.blit_rect)
