import pygame as pg
import pygame.freetype as ft
from .camera import Camera
from .leveljson import LevelManager
from .entities import Player
from .background import StaticBackground
from .headsupdisplay import HeadsUpDisplay
from .entitystate import GameEvent
from .userinterface import Menu, MenuButton, LevelSelectButton
import os
import json
import requests
from Crypto.Cipher import AES

"""
* =============================================================== *
* This module contains all the different scenes that make up the  *
* game.															  *
* A scene is effectively analogous to the state of the game.	  *
*	e.g. There is a scene to represent the Title Screen, the Game *
*		 screen, the Game Over screen, etc.						  *
* =============================================================== *

SCENES
-------------------------
All scenes must support the following methods, which are invoked on every cycle of the game loop:
    handle_events()		->		Processes all events currently waiting in the event queue
                                Event queue must be regularly emptied, otherwise new events 
                                will be dropped if the queue is full
    update()			->		Updates the state of the elements in the scene
    render()			->		Renders the elements of the scene onto the surface
    
Additionally, all scenes will have a manager attribute, which contains a SceneManager object to facilitate 
transitions between scenes.

SCENE MANAGER
-------------------------
- TO BE COMPLETED -
"""

# Size tuples
WINDOW_SIZE = (800, 600)
SURFACE_SIZE = (400, 300)

# Temporarily put this here so that code runs in Joshua's computer
# Will comment this out when I push
pg.init()

# Initialise sound
pg.mixer.init(44100, 16, 2, 512)

# Freetype font
# Initialise the FreeType font system
ft.init()
freetype = ft.Font("assets/fonts/pixChicago.ttf", 8)
freetype.antialiased = False


class Scene:
    """Represents a scene in the program, which is analogous to the state of the game"""
    sound_library = {"Scroll": pg.mixer.Sound("assets/sound/sfx/confirm.ogg"),
                     "Confirm": pg.mixer.Sound("assets/sound/sfx/confirm.ogg")
                     }

    def __init__(self):
        self.manager = SceneManager(self)
        self.game_display = pg.Surface(SURFACE_SIZE)

    def handle_events(self):
        raise NotImplementedError

    def update(self, *args):
        raise NotImplementedError

    def render(self, surface: pg.Surface):
        raise NotImplementedError


class SceneManager:
    """Handles scene transitions from one scene to another"""
    def __init__(self, scene: Scene):
        # TODO: Implement previous_scene as stack without dictionary
        self.scene_stack = []           # Lists can also act as stacks

        self.scene_stack.append(scene)
        self.scene = scene
        self.scene.manager = self

    def switch_to_scene(self, scene: Scene):
        self.scene_stack.append(scene)
        self.scene = scene
        self.scene.manager = self

    def go_to_previous_scene(self):
        self.scene_stack.pop()
        self.scene = self.scene_stack[-1]
        self.scene.manager = self


class TitleScene(Scene):
    """Represents the title screen"""

    def __init__(self):
        super().__init__()

        # Backgrounds
        self.backgrounds = (StaticBackground("assets/textures/background/01_background.png", self.game_display),
                            StaticBackground("assets/textures/background/03 background B.png", self.game_display),
                            StaticBackground("assets/textures/background/04 background.png", self.game_display))

        # Initialize title text
        self.title = freetype.render("THE TOWER", (70, 35, 35), None, 0, 0, 32)
        self.title_blit_position = (int((self.game_display.get_width() - self.title[0].get_width()) / 2), 100)

        # Initialise menu
        self.menu = Menu(8,
                         (200, 200, 200),
                         ("New Game", lambda: self.manager.switch_to_scene(GameScene()), (165, 180)),
                         ("Level Select", lambda: self.manager.switch_to_scene(LevelSelectionScene()), (165, 200)),
                         ("Quit Game", lambda: pg.quit(), (165, 220))
                         )

        # Play BGM
        pg.mixer.music.load("assets/sound/music/Debris of the Lost.ogg")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

    def handle_events(self):
        # Clears the event queue and processes the events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_UP:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_up()
                elif event.key == pg.K_DOWN:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_down()
                elif event.key == pg.K_RETURN:
                    self.sound_library["Confirm"].play()
                    self.menu.activate_current_button()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.sound_library["Confirm"].play()
                self.menu.click((event.pos[0] / 2, event.pos[1] / 2))

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        # Blit backgrounds on game_display
        for background in self.backgrounds:
            background.render()

        # Blit text on game_display
        self.game_display.blit(self.title[0], self.title_blit_position)
        # self.game_display.blit(self.text[0], self.text_blit_position)

        # TODO: render menu
        self.menu.render(self.game_display)

        # Blit game_display on window surface
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class LevelSelectionScene(Scene):
    def __init__(self):
        super().__init__()
        # Get the count of items in the directory
        levelcount = 0
        for i in range(1, 100):
            if os.path.exists("assets/levels/level" + str(i) + ".json"):
                levelcount += 1
            else:
                break

        # assign buttons based on the number of items in the directory

        self.pages_list = []
        # making the array of buttons
        current_limit = 12
        column_count = 0
        row_count = 0
        current_button_list = []
        for i in range(1, levelcount + 1):
            current_level = i
            current_button_list.append(LevelSelectButton(str(i) if i > 9 else ("0" + str(i)),
                                                  i,
                                                  (60 + column_count * 80, 100 + row_count * 60),
                                                  25,
                                                  (235, 235, 235)
                                                  )
                                       )
            column_count += 1
            if column_count > 3:
                column_count = 0
                row_count += 1

            if row_count > 2:
                column_count = 0
                row_count = 0
                self.pages_list.append(current_button_list)
                current_button_list = []

        self.pages_list.append(current_button_list)

        self.current_index = 0

        # additional text
        self.level_select_title = freetype.render("Level Select", (235, 235, 235), None, 0, 0, 24)
        self.title_blit_position = (int((self.game_display.get_width() - self.level_select_title[0].get_width()) / 2),
                                    35)

        # TODO: add two buttons for scrolling
        # this is hardcoded
        back_button_text = freetype.render("<", (235, 235, 235), None, 0, 0, 24)
        self.back_button = back_button_text[0]
        self.back_button_rect = pg.Rect(13, 100, 20, 150)

        self.forward_button = pg.transform.flip(self.back_button.copy(), True, False)
        self.forward_button_rect = pg.Rect(363, 100, 20, 150)

        # backgrounds
        self.backgrounds = (StaticBackground("assets/textures/background/01_background.png", self.game_display),
                            StaticBackground("assets/textures/background/03 background B.png", self.game_display),
                            StaticBackground("assets/textures/background/04 background.png", self.game_display))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_ESCAPE:
                    self.manager.go_to_previous_scene()
            elif event.type == pg.MOUSEBUTTONDOWN:
                coordinates = [int(event.pos[0] / 2), int(event.pos[1] / 2)]
                if self.forward_button_rect.collidepoint(coordinates):
                    if not self.current_index >= len(self.pages_list) - 1:
                        self.current_index += 1
                elif self.back_button_rect.collidepoint(coordinates):
                    if not self.current_index <= 0:
                        self.current_index -= 1
                for button in self.pages_list[self.current_index]:
                    if button.collidepoint(coordinates):
                        button.on_click()
                        break
            elif event.type == GameEvent.GAME_LOAD_LEVEL.value:
                print(event.code)
                self.manager.go_to_previous_scene()
                self.manager.switch_to_scene(GameScene())
                self.manager.scene.level_manager.load_level(event.code,
                                                            self.manager.scene.player,
                                                            self.manager.scene.camera)
                # prevents the user from submitting scores to leaderboard
                self.manager.scene.can_submit_leaderboard = False

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        for background in self.backgrounds:
            background.render()

        self.game_display.blit(self.level_select_title[0], self.title_blit_position)

        self.game_display.blit(self.forward_button,
                               (365, 150))
        self.game_display.blit(self.back_button,
                               (15, 150))

        for button in self.pages_list[self.current_index]:
            button.render(self.game_display)

        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class GameScene(Scene):
    """Represents the actual game screen"""

    def __init__(self):
        super().__init__()

        # Initialise the level manager
        self.level_manager = LevelManager()

        # Initialize camera
        self.camera = Camera(SURFACE_SIZE, self.level_manager.level.map.rect)

        # Initialize player
        self.player = Player()
        self.player_sprite_group = pg.sprite.GroupSingle(self.player)

        self.player.rect.x = self.level_manager.level.starting_position[0]
        self.player.rect.y = self.level_manager.level.starting_position[1]

        # Initialize GUI
        self.hud = HeadsUpDisplay()

        # TODO: Delegate background handling to Map, since Maps should know their background
        # Initialize backgrounds
        self.backgrounds = (StaticBackground("assets/textures/background/01_background.png", self.game_display),
                            StaticBackground("assets/textures/background/03 background B.png", self.game_display),
                            StaticBackground("assets/textures/background/04 background.png", self.game_display))

        # Play BGM
        pg.mixer.music.load("assets/sound/music/Deep Dream.ogg")
        pg.mixer.music.set_volume(0.8)
        pg.mixer.music.play(-1)

        # Track the time passed since the game started
        self.score_timer = pg.time.Clock()
        self.score_timer.tick()

        # hack to control ability to submit leaderboard
        self.can_submit_leaderboard = True

    def handle_events(self):
        # Clears the event queue and processes the events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_ESCAPE:
                    pg.mixer.music.pause()
                    self.manager.switch_to_scene(PauseScene())
            elif event.type == GameEvent.SWITCH_LEVEL.value:
                self.manager.switch_to_scene(FadeOutScene())
            elif event.type == GameEvent.GAME_OVER.value:
                self.manager.switch_to_scene(GameOverScene())
            elif event.type == GameEvent.GAME_COMPLETE.value:
                # FIXME: this is unnecessary, check and remove
                self.manager.switch_to_scene(GameBeatenScene(self.score_timer.tick() / 1000))
                if not self.can_submit_leaderboard:
                    self.manager.scene.submitted = True

        # Processes the input for the player
        self.player.handle_input()

    def update(self, delta_time):
        self.player.update(delta_time, self.level_manager.level.map)
        self.level_manager.level.update(delta_time, self.player)
        self.hud.update(delta_time, self.player, self.camera)

        # Move camera to player's position
        self.camera.follow_target(self.player)

    def render(self, surface):
        # Blit backgrounds on game_display
        for background in self.backgrounds:
            background.render()

        # Draws the map and enemies
        self.level_manager.level.render(self.camera, self.game_display)

        # Draw player on game_display wrt camera position
        self.player.render(self.camera, self.game_display)

        # Draw GUI
        self.hud.render(self.game_display)

        # Blit game_display on window surface
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class GameOverScene(Scene):
    """Represents the "Game Over" screen"""

    def __init__(self):
        super().__init__()

        # Initialize title
        self.title = freetype.render("GAME OVER", (235, 235, 235), None, 0, 0, 32)
        self.title_blit_position = (int((self.game_display.get_width() - self.title[0].get_width()) / 2), 100)

        self.menu = Menu(8,
                         (235, 235, 235),
                         ("Restart", lambda: pg.event.post(pg.event.Event(GameEvent.GAME_RESTART.value)), (182, 180)),
                         ("Main Menu",
                          lambda: pg.event.post(pg.event.Event(GameEvent.GAME_RETURN_TO_TITLE_SCREEN.value)),
                          (182, 200)),
                         ("Quit", lambda: pg.event.post(pg.event.Event(pg.QUIT)), (182, 220)))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == GameEvent.GAME_RESTART.value:
                self.manager.go_to_previous_scene()
                self.manager.go_to_previous_scene()
                self.manager.switch_to_scene(GameScene())
            elif event.type == GameEvent.GAME_RETURN_TO_TITLE_SCREEN.value:
                self.manager.go_to_previous_scene()
                self.manager.go_to_previous_scene()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_UP:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_up()
                elif event.key == pg.K_DOWN:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_down()
                elif event.key == pg.K_RETURN:
                    self.sound_library["Confirm"].play()
                    self.menu.activate_current_button()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.sound_library["Confirm"].play()
                self.menu.click((event.pos[0] / 2, event.pos[1] / 2))

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        # Fill game_display with black
        self.game_display.fill((0, 0, 0))

        # Blit title and subtitle on game_display
        self.game_display.blit(self.title[0], self.title_blit_position)
        self.menu.render(self.game_display)

        # Blit game_display on window surface
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class GameBeatenScene(Scene):
    def __init__(self, time: float):
        super().__init__()
        self.time = time
        # Initialize title
        self.title = freetype.render("VICTORY", (0, 0, 0), None, 0, 0, 32)
        self.title_blit_position = (int((self.game_display.get_width() - self.title[0].get_width()) / 2), 100)

        self.menu = Menu(8,
                         (80, 80, 80),
                         ("Restart", lambda: pg.event.post(pg.event.Event(GameEvent.GAME_RESTART.value)), (182, 180)),
                         ("Main Menu",
                          lambda: pg.event.post(pg.event.Event(GameEvent.GAME_RETURN_TO_TITLE_SCREEN.value)),
                          (182, 200)),
                         ("Leaderboard", lambda: self.manager.switch_to_scene(LeaderboardScene(self.time, self.submitted)), (182, 220)),
                         ("Quit", lambda: pg.event.post(pg.event.Event(pg.QUIT)), (182, 240)))

        self.submitted = False          # This is the last place to change this

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == GameEvent.GAME_RESTART.value:
                self.manager.go_to_previous_scene()
                self.manager.go_to_previous_scene()
                self.manager.switch_to_scene(GameScene())
            elif event.type == GameEvent.GAME_RETURN_TO_TITLE_SCREEN.value:
                self.manager.go_to_previous_scene()
                self.manager.go_to_previous_scene()
                self.manager.go_to_previous_scene()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_UP:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_up()
                elif event.key == pg.K_DOWN:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_down()
                elif event.key == pg.K_RETURN:
                    self.sound_library["Confirm"].play()
                    self.menu.activate_current_button()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.sound_library["Confirm"].play()
                self.menu.click((event.pos[0] / 2, event.pos[1] / 2))

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        # Fill game_display with black
        self.game_display.fill((235, 235, 235))

        # Blit title and subtitle on game_display
        self.game_display.blit(self.title[0], self.title_blit_position)
        self.menu.render(self.game_display)

        # Blit game_display on window surface
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class LeaderboardScene(Scene):
    def __init__(self, time: float, submitted = False):
        super().__init__()
        self.time = time
        # First list the top ten
        # then list your score
        # then have submit and back buttons
        self.title = freetype.render("Your timing: " + ('%.1f' % self.time) + 's', (0, 0, 0), None, 0, 0, 18)
        self.title_blit_position = (int((self.game_display.get_width() - self.title[0].get_width()) / 2), 25)

        self.leaderboard_names_list = []
        self.leaderboard_timings_list = []
        self.render_heights = []

        self.render_error = False
        self.fetch_error = freetype.render("There was an error in fetching the leaderboard", (150, 0, 0), None, 0, 0, 8)

        try:
            self.fetch_leaderboard()
        except Exception:
            pass

        self.submitted = submitted
        if submitted:
            self.menu = Menu(8,
                             (80, 80, 80),
                             ("Back", lambda: self.manager.go_to_previous_scene(), (180, 250))
                             )
        else:
            self.menu = Menu(8,
                             (80, 80, 80),
                             ("Submit Score", lambda: self.manager.switch_to_scene(LeaderboardSubmissionScene(self.time)),
                              (90, 250)),
                             ("Back", lambda: self.manager.go_to_previous_scene(), (280, 250))
                             )

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_LEFT:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_up()
                elif event.key == pg.K_RIGHT:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_down()
                elif event.key == pg.K_RETURN:
                    self.sound_library["Confirm"].play()
                    self.menu.activate_current_button()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.sound_library["Confirm"].play()
                self.menu.click((event.pos[0] / 2, event.pos[1] / 2))
        # TODO: when posting the request, make a new get request from the server and update the list again 

    def update(self, *args):
        if self.submitted:
            self.manager.scene_stack[-2].submitted = True

    def render(self, surface: pg.Surface):
        # TODO: render all elements on the screen
        self.game_display.fill((235, 235, 235))
        self.game_display.blit(self.title[0], self.title_blit_position)
        if self.render_error is True:
            self.game_display.blit(self.fetch_error[0],
                                   (int((self.game_display.get_width() - self.fetch_error[0].get_width()) / 2),
                                    int((self.game_display.get_height() - self.fetch_error[0].get_height()) / 2) - 18))
        else:
            for i in range (0, len(self.leaderboard_names_list)):
                self.game_display.blit(self.leaderboard_names_list[i][0][0], self.leaderboard_names_list[i][1])
                self.game_display.blit(self.leaderboard_timings_list[i][0][0], self.leaderboard_timings_list[i][1])
        self.menu.render(self.game_display)


        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))

    def fetch_leaderboard(self):
        # Get the json from the remote server and parse
        leaderboard_json_response = requests.get('https://recursivesandwich-api.herokuapp.com/highscores').text
        leaderboard_json_dict = json.loads(leaderboard_json_response)

        # Generate text based on the results of json parse
        # TODO: these must contain names and blit positions
        self.leaderboard_names_list = []
        self.leaderboard_timings_list = []
        self.render_heights = []

        name_x = 50
        time_x = 300
        starting_y = 60

        for i in range(0, 10):
            # get key, if key not valid break immediately
            try:
                user = leaderboard_json_dict[i]["user"]
                user = user if len(user) <= 20 else user[0:20] + "..."
                self.leaderboard_names_list.append((freetype.render(user,
                                                                    (0, 0, 0),
                                                                    None,
                                                                    0,
                                                                    0,
                                                                    12),
                                                    (name_x, starting_y)))
                self.leaderboard_timings_list.append((freetype.render(('%.1f' % leaderboard_json_dict[i]["time"]) + "s",
                                                                      (0, 0, 0),
                                                                      None,
                                                                      0,
                                                                      0,
                                                                      12),
                                                      (time_x, starting_y)))
                starting_y += 18
            except IndexError:
                break

    def change_menu_upon_successful_submission(self):
        """Call this to restrict the ability to resubmit scores"""
        self.menu = Menu(8,
                         (80, 80, 80),
                         ("Back", lambda: self.manager.go_to_previous_scene(), (180, 250))
                         )


class LeaderboardSubmissionScene(Scene):
    def __init__(self, time: float):
        super().__init__()
        self.player_name = ""
        self.time = time
        self.render_length_warning = False
        self.render_fail_warning = False
        self.length_warning = freetype.render("Name cannot be empty!", (150, 0, 0), None, 0, 0, 12)
        self.fail_warning = freetype.render("A problem occurred with the request", (150, 0, 0), None, 0, 0, 12)
        self.success_notification = freetype.render("Your highscore has been submitted!", (0, 150, 0), None, 0, 0, 12)
        self.input_instructions = freetype.render("Enter your name below:", (50, 50, 50), None, 0, 0, 12)
        self.submission_instructions = freetype.render("Press Enter to submit or Esc to go back", (50, 50, 50), None, 0, 0, 8)
        self.request_posted_successfully = False

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
                    if len(self.player_name) <= 0 or self.player_name.isspace():
                        self.render_length_warning = True
                    else:
                        self.render_length_warning = False
                        # Useragent is here to validate requests
                        if not self.request_posted_successfully:
                            def pad(string_or_number):
                                pad_length = (16 - (len(str(string_or_number)) % 16)) % 16
                                output = (str(string_or_number) + (str(chr(pad_length)) * pad_length)).encode("utf-8")
                                return output
                            
                            try:
                                encryptor = AES.new("u8x/A?D(G+KaPdSgVkYp3s6v9y$B&E)H".encode("utf-8"),
                                                    AES.MODE_CBC,
                                                    "LoremIpsumDolorS".encode("utf-8"))
                                post_request = requests.post('https://recursivesandwich-api.herokuapp.com/highscores',
                                                             headers = {"User-Agent": "The Tower - Game Client"},
                                                             data = {"user": encryptor.encrypt(pad(self.player_name)),
                                                                     "time": encryptor.encrypt(pad(self.time))
                                                                     }
                                                             )
                                if post_request.status_code == 201:
                                    self.request_posted_successfully = True
                                    self.render_fail_warning = False
                                else:
                                    self.render_fail_warning = True
                            except requests.RequestException:
                                self.render_fail_warning = True
                elif event.key == pg.K_ESCAPE:
                    self.manager.go_to_previous_scene()
                    if self.request_posted_successfully:
                        # TODO: modify previous state
                        self.manager.scene.change_menu_upon_successful_submission()
                        self.manager.scene.fetch_leaderboard()
                        self.manager.scene.submitted = True
                elif event.key == pg.K_BACKSPACE:
                    # array slicing is safe from null pointers
                    self.player_name = self.player_name[:-1]
                else:
                    self.player_name += event.unicode

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        name_display = freetype.render(self.player_name, (0, 0, 0), None, 0, 0, 24)

        self.game_display.fill((235, 235, 235))

        # Render name
        self.game_display.blit(name_display[0],
                               (int((self.game_display.get_width() - name_display[0].get_width()) / 2),
                                int((self.game_display.get_height() - name_display[0].get_height()) / 2))
                               )

        # Render instructions
        self.game_display.blit(self.input_instructions[0],
                               (int((self.game_display.get_width() - self.input_instructions[0].get_width()) / 2),
                                int((self.game_display.get_height() - self.input_instructions[0].get_height()) / 2) - 30)
                               )

        self.game_display.blit(self.submission_instructions[0],
                               (int((self.game_display.get_width() - self.submission_instructions[0].get_width()) / 2),
                                int((self.game_display.get_height() - self.submission_instructions[0].get_height()) / 2) + 30)
                               )

        # Render warnings
        if self.render_fail_warning:
            self.game_display.blit(self.fail_warning[0],
                                   (int((self.game_display.get_width() - self.fail_warning[0].get_width()) / 2),
                                    int((self.game_display.get_height() - self.fail_warning[0].get_height()) / 2) + 50)
                                   )
        elif self.render_length_warning:
            self.game_display.blit(self.length_warning[0],
                                   (int((self.game_display.get_width() - self.length_warning[0].get_width()) / 2),
                                    int((self.game_display.get_height() - self.length_warning[0].get_height()) / 2) + 50)
                                   )
        elif self.request_posted_successfully:
            self.game_display.blit(self.success_notification[0],
                                   (int((self.game_display.get_width() - self.success_notification[0].get_width()) / 2),
                                    int((self.game_display.get_height() - self.success_notification[0].get_height()) / 2) + 50)
                                   )

        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class PauseScene(Scene):
    def __init__(self):
        super().__init__()
        self.menu = Menu(20,
                         (235, 235, 235),
                         ("RESUME", lambda: pg.event.post(pg.event.Event(GameEvent.GAME_RESUME.value)), (170, 120)),
                         ("QUIT", lambda: pg.event.post(pg.event.Event(pg.QUIT)), (170, 160)))

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == GameEvent.GAME_RESUME.value:
                pg.mixer.music.unpause()
                self.manager.go_to_previous_scene()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
                elif event.key == pg.K_UP:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_up()
                elif event.key == pg.K_DOWN:
                    self.sound_library["Scroll"].play()
                    self.menu.scroll_down()
                elif event.key == pg.K_RETURN:
                    self.sound_library["Confirm"].play()
                    self.menu.activate_current_button()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.sound_library["Confirm"].play()
                self.menu.click((event.pos[0] / 2, event.pos[1] / 2))

    def update(self, *args):
        pass

    def render(self, surface: pg.Surface):
        self.game_display.fill((20, 20, 20))
        self.menu.render(self.game_display)
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


# -------------------- LEVEL TRANSITION SCENES -------------------- #
class FadeOutScene(Scene):
    def __init__(self):
        super().__init__()
        self.counter = 30
        self.game_display.fill((0, 0, 0))
        self.game_display.set_alpha(50)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()

    def update(self, delta_time):
        if self.counter > 0:
            self.counter -= 1
        else:
            self.manager.go_to_previous_scene()
            # at this point the scene is definitely GameScene
            # to ensure correctness can push a "FADE OUT" Event
            # FIXME: This is super hacky and ideally should be resolved, but other methods are more complicated
            self.manager.scene.level_manager.load_next_level(self.manager.scene.player,
                                                             self.manager.scene.camera)

            if not self.manager.scene.level_manager.is_game_complete():
                self.manager.switch_to_scene(LoadingScene())

    def render(self, surface: pg.Surface):
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class LoadingScene(Scene):
    def __init__(self):
        super().__init__()
        self.text = freetype.render("Loading...", (255, 255, 255))
        self.text_blit_position = (int((self.game_display.get_width() - self.text[0].get_width()) / 2), 200)
        self.wait_frames = 90

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()
            elif event.type == GameEvent.GAME_COMPLETE.value:
                self.manager.switch_to_scene(GameBeatenScene())

    def update(self, delta_time):
        if self.wait_frames > 0:
            self.wait_frames -= 1
        else:
            self.manager.go_to_previous_scene()
            self.manager.switch_to_scene(FadeInScene(self.manager.scene))

    def render(self, surface: pg.Surface):
        self.game_display.fill((0, 0, 0))

        self.game_display.blit(self.text[0], self.text_blit_position)
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))


class FadeInScene(Scene):
    def __init__(self, previous_scene):
        super().__init__()
        self.counter = 15
        self.game_display.fill((0, 0, 0))
        self.game_display.set_alpha(255)
        self.previous_scene = previous_scene

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F4 and (event.mod & pg.KMOD_ALT):
                    pg.quit()
                    quit()

    def update(self, delta_time):
        if self.counter > 0:
            self.counter -= 1
            self.game_display.set_alpha(17 * self.counter)
        else:
            self.manager.go_to_previous_scene()

    def render(self, surface: pg.Surface):
        # Basically render the previous scene and then render the overlay over it
        self.previous_scene.render(surface)
        surface.blit(pg.transform.scale(self.game_display, WINDOW_SIZE), (0, 0))
