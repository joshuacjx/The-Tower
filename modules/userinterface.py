import pygame as pg
import pygame.freetype as ft

from modules.entitystate import GameEvent

ft.init()
freetype = ft.Font("assets/fonts/pixChicago.ttf")
freetype.antialiased = False


class MenuButton:
    def __init__(self, text, action, position, fontsize = 8, color = (235, 235, 235)):
        self.text = freetype.render(text, color, None, 0, 0, fontsize)
        self.action = action
        self.rect = pg.Rect(position, (self.text[0].get_width(),
                                       self.text[0].get_height()))

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

    def on_click(self):
        return self.action()

    def render(self, surface):
        surface.blit(self.text[0], self.rect.topleft)


class Menu:
    def __init__(self, fontsize, color, *entries):
        # entries is a 3-tuple: text, action, position
        self.fontsize = fontsize
        self.button_list = []
        for entry in entries:
            self.button_list.append(MenuButton(entry[0], entry[1], entry[2], fontsize, color))
        self.length = len(self.button_list)
        self.current_index = 0

        self.caret = freetype.render(">>>", color, None, 0, 0, fontsize)
        self.current_caret_position = [self.button_list[self.current_index].rect.left
                                       - self.caret[0].get_width()
                                       - self.fontsize,
                                       self.button_list[self.current_index].rect.top +
                                       ((self.button_list[self.current_index].rect.height - self.caret[0].get_height())
                                        / 2)]

    def scroll_up(self):
        self.current_index = max(self.current_index - 1, 0)
        self.current_caret_position = [self.button_list[self.current_index].rect.left
                                       - self.caret[0].get_width()
                                       - self.fontsize,
                                       self.button_list[self.current_index].rect.top +
                                       ((self.button_list[self.current_index].rect.height - self.caret[0].get_height())
                                        / 2)]

    def scroll_down(self):
        self.current_index = min(self.current_index + 1, self.length - 1)
        self.current_caret_position = [self.button_list[self.current_index].rect.left
                                       - self.caret[0].get_width()
                                       - self.fontsize,
                                       self.button_list[self.current_index].rect.top +
                                       ((self.button_list[self.current_index].rect.height - self.caret[0].get_height())
                                        / 2)]

    def click(self, point):
        for button in self.button_list:
            if button.collidepoint(point):
                button.on_click()
                break

    def activate_current_button(self):
        self.button_list[self.current_index].on_click()

    def render(self, surface):
        for button in self.button_list:
            button.render(surface)
        surface.blit(self.caret[0], self.current_caret_position)


class LevelSelectButton:
    def __init__(self, text, level_num, position, fontsize = 8, color = (235, 235, 235)):
        self.text = freetype.render(text, color, None, 0, 0, fontsize)
        self.level_num = level_num
        self.rect = pg.Rect(position, (self.text[0].get_width(),
                                       self.text[0].get_height()))

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

    def on_click(self):
        pg.event.post(pg.event.Event(GameEvent.GAME_LOAD_LEVEL.value,
                      {"code": self.level_num}))

    def render(self, surface):
        surface.blit(self.text[0], self.rect.topleft)