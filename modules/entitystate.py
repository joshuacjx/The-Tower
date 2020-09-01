import pygame as pg
from enum import Enum

"""
* =============================================================== *
* This module contains various enumerations related to the game.  *
* =============================================================== *
"""


class EntityState(Enum):
    IDLE = 0
    WALKING = 1
    JUMPING = 2
    DEAD = 3
    HANGING = 4
    CLIMBING = 5


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Action(Enum):
    WALK = 0
    STOP = 1
    JUMP = 2
    LAND = 3


class GameEvent(Enum):
    SWITCH_LEVEL = pg.USEREVENT + 0
    GAME_OVER = pg.USEREVENT + 1
    GAME_COMPLETE = pg.USEREVENT + 2
    GAME_RESUME = pg.USEREVENT + 3
    GAME_RESTART = pg.USEREVENT + 4
    GAME_RETURN_TO_TITLE_SCREEN = pg.USEREVENT + 5
    GAME_LOAD_LEVEL = pg.USEREVENT + 6
