import pygame as pg
import pygame.freetype as ft
from dev_modules.editorscenes import *

"""
* =============================================================== *
* This is the entry point into the programme. Running the main()  *
* method will invoke all modules required to get the game up and  *
* running.                                                        *
* =============================================================== *
"""


def main() -> None:
    """Initialises PyGame and invokes all the necessary functions and modules to run the map editor"""

    # Initialise PyGame
    pg.init()

    # Initialise window
    window = pg.display.set_mode((1050, 600))
    pg.display.set_caption("Map Editor", "Map Editor")

    # Initialise clock
    clock = pg.time.Clock()

    # Initialise scene manager with TitleScene set as the initial scene
    manager = SceneManager(MapEditorScene("assets/levels/level1.json"))

    # Game loop runs when this is true
    run = True

    # -------------------- GAME LOOP -------------------- #
    while run:
        # Directs the scene to process events in the queue, update its state and render onto the window
        manager.scene.handle_events()
        manager.scene.update()
        manager.scene.render(window)

        # Updates the window to reflect the current rendered image
        pg.display.update()

        # Limits the game to 60 fps
        clock.tick(60)
    # -------------------- END GAME LOOP ---------------- #
    # Quit PyGame
    pg.quit()

    # Quit programme
    quit()


main()
