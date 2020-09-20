import pygame as pg
from .spritesheet import SpriteSheet
from .animation import Animation
from .entitystate import EntityState
pg.mixer.init()


class Library:

    adventurer_sprite_sheets = {
        "IDLE": SpriteSheet("assets/textures/player/adventurer-idle.png", 1, 4),
        "WALKING": SpriteSheet("assets/textures/player/adventurer-run.png", 1, 6),
        "JUMPING": SpriteSheet("assets/textures/player/adventurer-jump.png", 1, 1),
        "CLIMBING": SpriteSheet("assets/textures/player/adventurer-climb.png", 1, 4)
    }

    player_animations = {
        EntityState.IDLE: Animation.of_entire_sheet(adventurer_sprite_sheets["IDLE"]),
        EntityState.WALKING: Animation.of_entire_sheet(adventurer_sprite_sheets["WALKING"]),
        EntityState.JUMPING: Animation.of_entire_sheet(adventurer_sprite_sheets["JUMPING"]),
        EntityState.HANGING: Animation.of_selected_images(adventurer_sprite_sheets["CLIMBING"], 0, 0),
        EntityState.CLIMBING: Animation.of_entire_sheet(adventurer_sprite_sheets["CLIMBING"])
    }

    entity_sounds = {
        "JUMP": pg.mixer.Sound("assets/sound/sfx/jump.ogg"),
        "DECREMENT_HEALTH": pg.mixer.Sound("assets/sound/sfx/hitdamage.ogg")
    }

    pink_guy_sprite_sheets = {
        "IDLE": SpriteSheet("assets/textures/enemies/Pink Guy/Idle.png", 1, 11),
        "WALKING": SpriteSheet("assets/textures/enemies/Pink Guy/Run.png", 1, 12),
        "JUMPING": SpriteSheet("assets/textures/enemies/Pink Guy/Jump.png", 1, 1)
    }

    pink_guy_animations = {
        EntityState.IDLE: Animation.of_entire_sheet(pink_guy_sprite_sheets["IDLE"]),
        EntityState.WALKING: Animation.of_entire_sheet(pink_guy_sprite_sheets["WALKING"]),
        EntityState.JUMPING: Animation.of_entire_sheet(pink_guy_sprite_sheets["JUMPING"]),
        EntityState.DEAD: Animation.of_selected_images(pink_guy_sprite_sheets["IDLE"], 0, 0)
    }

    trash_monster_sprite_sheets = {
        "IDLE": SpriteSheet("assets/textures/enemies/Trash Monster/Trash Monster-Idle.png", 1, 6).scale(44, 32),
        "WALKING": SpriteSheet("assets/textures/enemies/Trash Monster/Trash Monster-Run.png", 1, 6).scale(44, 32),
        "JUMPING": SpriteSheet("assets/textures/enemies/Trash Monster/Trash Monster-Jump.png", 1, 1).scale(44, 32)
    }

    trash_monster_animations = {
        EntityState.IDLE: Animation.of_entire_sheet(trash_monster_sprite_sheets["IDLE"], flip=True),
        EntityState.WALKING: Animation.of_entire_sheet(trash_monster_sprite_sheets["WALKING"], flip=True),
        EntityState.JUMPING: Animation.of_entire_sheet(trash_monster_sprite_sheets["JUMPING"], flip=True),
        EntityState.DEAD: Animation.of_selected_images(trash_monster_sprite_sheets["IDLE"], 0, 0, flip=True)
    }

    tooth_walker_sprite_sheets = {
        "WALKING": SpriteSheet("assets/textures/enemies/Tooth Walker/tooth walker walk.png", 1, 6).scale(100, 65),
        "DEAD": SpriteSheet("assets/textures/enemies/Tooth Walker/tooth walker dead.png", 1, 1).scale(100, 65)
    }

    tooth_walker_animations = {
        EntityState.IDLE: Animation.of_selected_images(tooth_walker_sprite_sheets["WALKING"], 0, 0),
        EntityState.WALKING: Animation.of_entire_sheet(tooth_walker_sprite_sheets["WALKING"]),
        EntityState.JUMPING: Animation.of_selected_images(tooth_walker_sprite_sheets["WALKING"], 0, 0),
        EntityState.DEAD: Animation.of_entire_sheet(tooth_walker_sprite_sheets["DEAD"])
    }
