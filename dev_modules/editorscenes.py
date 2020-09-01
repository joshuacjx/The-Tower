import pygame as pg
import pygame.freetype as ft
import json
from dev_modules.events import EditorEvents
from dev_modules.editorpanels import PalettePanel, MapPanel

ft.init()
freetype = ft.Font("assets/fonts/pixChicago.ttf", 12)
freetype.antialiased = False


class Scene:
    """Represents a scene in the program, which is analogous to the state of the game"""
    def __init__(self):
        self.manager = SceneManager(self)
        self.game_display = pg.Surface((525, 300))

    def handle_events(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self, surface: pg.Surface):
        raise NotImplementedError


class SceneManager:
    """Handles scene transitions from one scene to another"""
    def __init__(self, scene: Scene):
        # TODO: Implement previous_scene as stack without dictionary
        self.scene = scene
        self.scene.manager = self
        self.previous_scene = None

    def switch_to_scene(self, scene: Scene):
        self.previous_scene = self.scene
        self.scene = scene
        self.scene.manager = self

    def go_to_previous_scene(self):
        self.scene = self.previous_scene
        self.scene.manager = self


class MapEditorScene(Scene):
    def __init__(self, filepath=None, dimensions=None):
        super().__init__()
        self.palette_display = pg.Surface((125, 300))
        self.map_display = pg.Surface((400, 300))

        self.palette_panel = PalettePanel()
        self.map_panel = MapPanel(filepath, dimensions)

    def handle_events(self):
        # use events to coordinate the current selected block
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == EditorEvents.BLOCK_SWITCH:
                print(event.code)
                self.map_panel.current_code = event.code
            elif event.type == EditorEvents.LOAD_FILE:
                self.manager.switch_to_scene(MapLoadScene())
            elif event.type == EditorEvents.SAVE_FILE:
                self.manager.switch_to_scene(MapSaveScene(self.map_panel.level))
            elif event.type == EditorEvents.NEW_FILE:
                self.manager.switch_to_scene(NewMapScene())
            elif event.type == pg.MOUSEBUTTONDOWN:
                point = [event.pos[0] / 2, event.pos[1] / 2]
                if point[0] < 125:
                    self.palette_panel.click(point)
                else:
                    point[0] -= 125
                    self.map_panel.click(point)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.mod & pg.KMOD_SHIFT:
                    # Enables and disables display of the corresponding layers
                    if event.key == pg.K_1:
                        self.map_panel.level.map.bg_on = not self.map_panel.level.map.bg_on
                    elif event.key == pg.K_2:
                        self.map_panel.level.map.decorations_on = not self.map_panel.level.map.decorations_on
                    elif event.key == pg.K_3:
                        self.map_panel.level.map.terrain_on = not self.map_panel.level.map.terrain_on
                    elif event.key == pg.K_4:
                        self.map_panel.level.draw_enemies = not self.map_panel.level.draw_enemies
                    elif event.key == pg.K_5:
                        self.map_panel.level.draw_player_starting_position = not self.map_panel.level.draw_player_starting_position
                else:
                    # Sets the current active layer
                    if event.key == pg.K_1:
                        self.map_panel.current_layer = 1
                    elif event.key == pg.K_2:
                        self.map_panel.current_layer = 2
                    elif event.key == pg.K_3:
                        self.map_panel.current_layer = 3
                    elif event.key == pg.K_4:
                        self.map_panel.current_layer = 4
                    elif event.key == pg.K_5:
                        self.map_panel.current_layer = 5
                    elif event.key == pg.K_a:
                        self.map_panel.add_mode = True
                    elif event.key == pg.K_d:
                        self.map_panel.add_mode = False
                    elif event.key == pg.K_q:
                        self.palette_panel.texture_selector_sub_panel.on_texture_menu = True
                    elif event.key == pg.K_e:
                        self.palette_panel.texture_selector_sub_panel.on_texture_menu = False

    def update(self):
        current_keys = pg.key.get_pressed()
        self.palette_panel.update(current_keys)
        self.map_panel.update(current_keys)

    def render(self, surface: pg.Surface):
        self.palette_panel.render(self.palette_display)
        self.map_panel.render(self.map_display)

        self.game_display.blit(self.palette_display, (0, 0))
        self.game_display.blit(self.map_display, (125, 0))

        surface.blit(pg.transform.scale(self.game_display, (1050, 600)), (0, 0))


class MapLoadScene(Scene):
    def __init__(self):
        super().__init__()
        self.filepath = "assets/levels/"
        self.load_text = freetype.render("Load the file from the following path:", (235, 235, 235))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_RETURN:
                    try:
                        self.manager.switch_to_scene(MapEditorScene(self.filepath))
                    except FileNotFoundError:
                        self.manager.switch_to_scene(MapLoadAgainScene())
                elif event.key == pg.K_ESCAPE:
                    self.manager.go_to_previous_scene()
                elif event.key == pg.K_BACKSPACE:
                    # array slicing is safe from null pointers
                    self.filepath = self.filepath[:-1]
                else:
                    self.filepath += event.unicode

    def update(self):
        pass

    def render(self, surface):
        # for visuals only
        self.game_display = self.manager.previous_scene.game_display

        gui_window = pg.Surface((400, 100))
        gui_window.fill((42, 82, 92))
        filepath_display = freetype.render(self.filepath, (235, 235, 235))

        self.game_display.blit(gui_window,
                               (int((self.game_display.get_width() - gui_window.get_width()) / 2),
                                int((self.game_display.get_height() - gui_window.get_height()) / 2)))

        self.game_display.blit(filepath_display[0],
                               (int((self.game_display.get_width() - filepath_display[0].get_width()) / 2),
                                int((self.game_display.get_height() - filepath_display[0].get_height()) / 2) + 18))

        self.game_display.blit(self.load_text[0],
                               (int((self.game_display.get_width() - self.load_text[0].get_width()) / 2),
                                int((self.game_display.get_height() - self.load_text[0].get_height()) / 2) - 18))

        surface.blit(pg.transform.scale(self.game_display, (1050, 600)), (0, 0))


class MapLoadAgainScene(MapLoadScene):
    def __init__(self):
        super().__init__()
        self.filepath = "assets/levels/"
        self.load_text = freetype.render("File not found! Try again:", (235, 235, 235))


class MapSaveScene(Scene):
    def __init__(self, level):
        super().__init__()
        self.filepath = "assets/levels/"
        self.save_text = freetype.render("Saves the file the following path:", (235, 235, 235))
        self.level = level

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_RETURN:
                    # makes the dict
                    level_dict = self.level.serialise_to_dict()
                    # writes the file
                    with open(self.filepath, 'w') as outfile:
                        json.dump(level_dict, outfile, indent=4)

                    self.manager.go_to_previous_scene()
                elif event.key == pg.K_ESCAPE:
                    self.manager.go_to_previous_scene()
                elif event.key == pg.K_BACKSPACE:
                    # array slicing is safe from null pointers
                    self.filepath = self.filepath[:-1]
                else:
                    self.filepath += event.unicode

    def update(self):
        pass

    def render(self, surface):
        # for visuals only
        self.game_display = self.manager.previous_scene.game_display

        gui_window = pg.Surface((400, 100))
        gui_window.fill((42, 82, 92))
        filepath_display = freetype.render(self.filepath, (235, 235, 235))

        self.game_display.blit(gui_window,
                               (int((self.game_display.get_width() - gui_window.get_width()) / 2),
                                int((self.game_display.get_height() - gui_window.get_height()) / 2)))

        self.game_display.blit(filepath_display[0],
                               (int((self.game_display.get_width() - filepath_display[0].get_width()) / 2),
                                int((self.game_display.get_height() - filepath_display[0].get_height()) / 2) + 18))

        self.game_display.blit(self.save_text[0],
                               (int((self.game_display.get_width() - self.save_text[0].get_width()) / 2),
                                int((self.game_display.get_height() - self.save_text[0].get_height()) / 2) - 18))

        surface.blit(pg.transform.scale(self.game_display, (1050, 600)), (0, 0))


class NewMapScene(Scene):
    def __init__(self):
        super().__init__()
        self.new_map_text = freetype.render("Enter the dimensions of the map:", (235, 235, 235))
        self.width_text = freetype.render("width: ", (235, 235, 235))
        self.height_text = freetype.render("height: ", (235, 235, 235))
        self.caret = freetype.render("<==", (235, 235, 235))
        self.width = ""
        self.height = ""
        self.width_focus = True     # If False, then focus on height

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_RETURN:
                    self.manager.switch_to_scene(MapEditorScene(None, (self.width, self.height)))
                elif event.key == pg.K_ESCAPE:
                    self.manager.go_to_previous_scene()
                elif event.key == pg.K_TAB:
                    self.width_focus = not self.width_focus
                elif event.key == pg.K_UP:
                    self.width_focus = True
                elif event.key == pg.K_DOWN:
                    self.width_focus = False
                elif event.key == pg.K_BACKSPACE:
                    if self.width_focus is True:
                        self.width = self.width[:-1]
                    else:
                        self.height = self.height[:-1]
                else:
                    if self.width_focus is True:
                        self.width += event.unicode
                    else:
                        self.height += event.unicode

    def update(self):
        pass

    def render(self, surface):
        # for visuals only
        self.game_display = self.manager.previous_scene.game_display

        gui_window = pg.Surface((400, 120))
        gui_window.fill((42, 82, 92))
        width_display = freetype.render(self.width, (235, 235, 235))
        height_display = freetype.render(self.height, (235, 235, 235))

        self.game_display.blit(gui_window,
                               (int((self.game_display.get_width() - gui_window.get_width()) / 2),
                                int((self.game_display.get_height() - gui_window.get_height()) / 2)))

        self.game_display.blit(self.new_map_text[0],
                               (int((self.game_display.get_width() - self.new_map_text[0].get_width()) / 2),
                                int((self.game_display.get_height() - self.new_map_text[0].get_height()) / 2) - 30))

        self.game_display.blit(width_display[0],
                               (int(self.game_display.get_width() / 2),
                                int(self.game_display.get_height() / 2) - 10))

        self.game_display.blit(height_display[0],
                               (int(self.game_display.get_width() / 2),
                                int(self.game_display.get_height() / 2) + 30 - 10))

        self.game_display.blit(self.width_text[0],
                               (int((self.game_display.get_width() / 2) - self.width_text[0].get_width() - 10),
                                int(self.game_display.get_height() / 2) - 10))

        self.game_display.blit(self.height_text[0],
                               (int((self.game_display.get_width() / 2) - self.height_text[0].get_width() - 10),
                                int(self.game_display.get_height() / 2) + 30 - 10))

        self.game_display.blit(self.caret[0],
                               (int(self.game_display.get_width() / 2) + 30,
                                int(self.game_display.get_height() / 2) + (0 if self.width_focus is True else 30) - 10))

        surface.blit(pg.transform.scale(self.game_display, (1050, 600)), (0, 0))
