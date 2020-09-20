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

    def get_reverse(self):
        if self is Direction.LEFT:
            return Direction.RIGHT
        if self is Direction.RIGHT:
            return Direction.LEFT


class Action(Enum):
    WALK = 0
    STOP = 1
    JUMP = 2
    LAND = 3


class EntityMessage(Enum):
    """Components of Entities communicate with one another via message-passing.
    The entity receiving the message would carry out the action in the message
    if it has a Component that is able to carry it out."""

    PLAY_JUMP_SOUND = 0
    PLAY_DAMAGE_SOUND = 1
    TAKE_ENEMY_DAMAGE = 2
    TAKE_SPIKE_DAMAGE = 3
    DIE = 4
    AI_TURN_RIGHT = 5
    AI_TURN_LEFT = 6
    GAIN_HEALTH_FROM_COIN = 7


class GameEvent(Enum):
    SWITCH_LEVEL = pg.USEREVENT + 0
    GAME_OVER = pg.USEREVENT + 1
    GAME_COMPLETE = pg.USEREVENT + 2
    GAME_RESUME = pg.USEREVENT + 3
    GAME_RESTART = pg.USEREVENT + 4
    GAME_RETURN_TO_TITLE_SCREEN = pg.USEREVENT + 5
    GAME_LOAD_LEVEL = pg.USEREVENT + 6
