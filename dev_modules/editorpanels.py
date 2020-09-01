import pygame as pg
import pygame.freetype as ft
from modules.textureset import TextureSet
from modules.block import Block
from modules.entitystate import EntityState
from modules.entities import PinkGuy, TrashMonster, ToothWalker
from dev_modules.events import EditorEvents
from dev_modules.editorlevel import EditorLevel
from dev_modules.editorcamera import EditorCamera, PanelCamera

ft.init()
freetype = ft.Font("assets/fonts/pixChicago.ttf", 8)
freetype.antialiased = False


class MapPanel:
    """Displays the map in the Editor, and allows for the editing of objects"""
    def __init__(self, filepath, dimensions):
        self.camera = EditorCamera()
        self.level = EditorLevel(filepath, dimensions)
        if filepath is None:
            self.boundaries = (int(dimensions[0]) * Block.BLOCK_SIZE,
                               int(dimensions[1]) * Block.BLOCK_SIZE)
        else:
            self.boundaries = (len(self.level.map.bg_array[0]) * Block.BLOCK_SIZE,
                               len(self.level.map.bg_array) * Block.BLOCK_SIZE)
        self.current_code = "xx"            # Can be an enemy code or a block code
        self.add_mode = True            # if this is false, then this is erase mode
        self.current_layer = 1

        self.layer_to_string_repr = {1: "background",
                                     2: "decorations",
                                     3: "terrain",
                                     4: "enemies",
                                     5: "starting_position"
                                     }

    def click(self, coordinates):
        # Since the screen is scaled to 4x the original, we have to translate the coordinates from the game window
        # to the virtual screen
        virtual_coordinates = (coordinates[0] + self.camera.rect.x,
                               coordinates[1] + self.camera.rect.y)

        # Adds or deletes blocks at the clicked coordinate
        if self.add_mode is True:
            self.level.add(virtual_coordinates, self.current_layer, self.current_code)
        else:
            self.level.delete(virtual_coordinates, self.current_layer)

    def update(self, current_keys):
        # Scrolls the camera
        self.camera.update(current_keys[pg.K_UP],
                           current_keys[pg.K_DOWN],
                           current_keys[pg.K_LEFT],
                           current_keys[pg.K_RIGHT],
                           self.boundaries)

    def render(self, surface):
        surface.fill((100, 100, 100))
        self.level.render(self.camera, surface)

        current_code_display = freetype.render("current code: " + self.current_code, (235, 235, 235))
        layer_display = freetype.render("layer: " + self.layer_to_string_repr[self.current_layer],
                                        (235, 235, 235))
        add_mode_display = freetype.render("mode: add" if self.add_mode else "mode: delete",
                                           (235, 235, 235))

        # blit status bar
        surface.blit(current_code_display[0], (5, 5))
        surface.blit(layer_display[0], (150, 5))
        surface.blit(add_mode_display[0], (300, 5))


class PalettePanel:
    """Allows the user to select objects to place on the map, and also allows for load/save/create"""
    def __init__(self):
        self.load_save_sub_panel = LoadSaveSubPanel()
        self.load_save_sub_surface = pg.Surface((125, 60))

        self.texture_selector_sub_panel = TextureSelectorSubPanel()
        self.texture_selector_sub_surface = pg.Surface((125, 240))

    def click(self, point):
        """Translates clicks into virtual coordinates at each panel"""
        if point[1] < 60:
            self.load_save_sub_panel.click(point)
        else:
            self.texture_selector_sub_panel.click((point[0], point[1] - 60))

    def update(self, current_keys):
        self.texture_selector_sub_panel.update(current_keys)

    def render(self, surface):
        self.load_save_sub_panel.render(self.load_save_sub_surface)
        surface.blit(self.load_save_sub_surface, (0, 0))

        self.texture_selector_sub_panel.render(self.texture_selector_sub_surface)
        surface.blit(self.texture_selector_sub_surface, (0, 60))


class LoadSaveSubPanel:
    """Handles the loading, saving, and creation of Levels"""
    def __init__(self):
        self.load = freetype.render("load file", (235, 235, 235))
        self.save = freetype.render("save file", (235, 235, 235))
        self.new = freetype.render("new file", (235, 235, 235))

        self.load_rect = self.load[1]
        self.save_rect = self.save[1]
        self.new_rect = self.new[1]

        self.load_pos = (10, 10)
        self.save_pos = (10, 25)
        self.new_pos = (10, 40)

        self.load_rect.topleft = self.load_pos
        self.save_rect.topleft = self.save_pos
        self.new_rect.topleft = self.new_pos

        print(self.load_rect)
        print(self.save_rect)
        print(self.new_rect)

        self.colliding_rect_list = (self.load_rect,
                                    self.save_rect,
                                    self.new_rect)

    def click(self, coordinates):
        if self.load_rect.collidepoint(coordinates):
            pg.event.post(
                pg.event.Event(
                    EditorEvents.LOAD_FILE,
                )
            )
        elif self.save_rect.collidepoint(coordinates):
            pg.event.post(
                pg.event.Event(
                    EditorEvents.SAVE_FILE,
                )
            )
        elif self.new_rect.collidepoint(coordinates):
            pg.event.post(
                pg.event.Event(
                    EditorEvents.NEW_FILE,
                )
            )

    def render(self, surface):
        surface.fill((38, 73, 77))
        surface.blit(self.load[0], self.load_pos)
        surface.blit(self.save[0], self.save_pos)
        surface.blit(self.new[0], self.new_pos)


class TextureSelectorSubPanel:
    """Contains two sub-panels for selecting blocks and selecting enemies"""
    def __init__(self):
        textureset = TextureSet()
        next_x = 10
        next_y = 10

        self.on_texture_menu = True     # if False, selects enemies instead

        # Texture selection menu
        self.texture_button_array = []
        for code in textureset.code_to_texture_dictionary.keys():
            terraintype = textureset.get_texture_from_code(code)
            self.texture_button_array.append(TextureButton(code,
                                                           (next_x, next_y),
                                                           terraintype))
            next_y += terraintype.block_height * Block.BLOCK_SIZE + 10

        self.texture_panel_camera = PanelCamera(next_y)

        # Entity selection menu
        next_y = 10
        self.entity_button_array = []
        enemy_type = {"Pink Guy": PinkGuy(),
                      "Trash Monster": TrashMonster(),
                      "Tooth Walker": ToothWalker()
                      }
        for code in enemy_type.keys():
            enemytypeobject = enemy_type[code]
            self.entity_button_array.append(EntityButton(code,
                                                         (next_x, next_y),
                                                         enemytypeobject))
            next_y += enemytypeobject.rect.height + 10

        self.entity_panel_camera = PanelCamera(next_y)

    def click(self, coordinates):
        """Handles click events in the sub-panel"""
        # The if-else statement handles whether to select from the texture menu or the entity menu
        if self.on_texture_menu is True:
            virtual_coordinates = (coordinates[0], coordinates[1] + self.texture_panel_camera.rect.y)
            for button in self.texture_button_array:
                if button.collidepoint(virtual_coordinates):
                    button.on_click()
                    return
        else:
            virtual_coordinates = (coordinates[0], coordinates[1] + self.entity_panel_camera.rect.y)
            for button in self.entity_button_array:
                if button.collidepoint(virtual_coordinates):
                    button.on_click()
                    return

    def update(self, current_keys):
        """Scrolls the texture sub-panel"""
        if self.on_texture_menu is True:
            self.texture_panel_camera.scroll(current_keys[pg.K_w],
                                             current_keys[pg.K_s])
        else:
            self.entity_panel_camera.scroll(current_keys[pg.K_w],
                                            current_keys[pg.K_s])

    def render(self, surface):
        """Renders the sub-panel"""
        surface.fill((38, 73, 77))

        # Selects which sub-menu to render based on which menu is active
        if self.on_texture_menu is True:
            for button in self.texture_button_array:
                if self.texture_panel_camera.rect.colliderect(button.rect):
                    surface.blit(button.image,
                                 (button.rect.x - self.texture_panel_camera.rect.x,
                                  button.rect.y - self.texture_panel_camera.rect.y))
        else:
            for button in self.entity_button_array:
                if self.entity_panel_camera.rect.colliderect(button.rect):
                    surface.blit(button.image,
                                 (button.rect.x - self.entity_panel_camera.rect.x,
                                  button.rect.y - self.entity_panel_camera.rect.y))


class TextureButton:
    def __init__(self, code, coordinates, terraintype):
        self.code = code
        self.image = pg.transform.scale(terraintype.image.convert_alpha(),
                                        (int(terraintype.block_width * Block.BLOCK_SIZE),
                                         int(terraintype.block_height * Block.BLOCK_SIZE))
                                        )
        self.rect = pg.Rect(coordinates,
                            (int(terraintype.block_width * Block.BLOCK_SIZE),
                             int(terraintype.block_height * Block.BLOCK_SIZE))
                            )

    def collidepoint(self, coordinates):
        return self.rect.collidepoint(coordinates)

    def on_click(self):
        pg.event.post(
            pg.event.Event(
                EditorEvents.BLOCK_SWITCH,
                {"code": self.code}
            )
        )

class EntityButton:
    def __init__(self, code, coordinates, enemytype):
        self.code = code
        self.image = enemytype.animation_library[EntityState.IDLE][0].subsurface(enemytype.blit_rect)
        self.rect = enemytype.rect
        self.rect.topleft = coordinates

    def collidepoint(self, coordinates):
        return self.rect.collidepoint(coordinates)

    def on_click(self):
        pg.event.post(
            pg.event.Event(
                EditorEvents.BLOCK_SWITCH,
                {"code": self.code}
            )
        )




