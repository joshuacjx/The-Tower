import pygame as pg


class EditorEvents:
    BLOCK_SWITCH = pg.USEREVENT + 0
    BG_TOGGLE = pg.USEREVENT + 1
    DECORATIONS_TOGGLE = pg.USEREVENT + 2
    TERRAIN_TOGGLE = pg.USEREVENT + 3
    LOAD_FILE = pg.USEREVENT + 4
    SAVE_FILE = pg.USEREVENT + 5
    NEW_FILE = pg.USEREVENT + 6

