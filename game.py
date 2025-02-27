import json
import typing
from collections.abc import Callable
from enum import Enum

import pygame

from debris import Debris
from laser import Laser
from meteorite import Meteorite
from player import Player
from sound import Sound
from uielemnts import Button, Counter, Text, UpgradeCard
from upgrade import UpgradeManager

GameState = Enum("GameState", ["MAIN_MENU", "IN_GAME", "UPGRADE_MENU"])


class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption("Galactic Salvage")
        res = pygame.display.Info()
        self.screen_resolution: tuple[int, int] = (
            min(1600, res.current_w),
            min(900, res.current_h),
        )

        self.screen: pygame.Surface = pygame.display.set_mode(self.screen_resolution)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.player: Player = Player(
            self.screen_resolution[0] // 2, self.screen_resolution[1] // 2, 0
        )

        self.game_state: GameState = GameState["MAIN_MENU"]

        self.counter_font: pygame.font.Font = pygame.font.Font(None, 200)

        self.font80: pygame.font.Font = pygame.font.Font("font/Beyonders-6YoJM.ttf", 80)
        self.font40: pygame.font.Font = pygame.font.Font("font/Beyonders-6YoJM.ttf", 40)
        self.font30: pygame.font.Font = pygame.font.Font("font/Beyonders-6YoJM.ttf", 30)
        self.font20: pygame.font.Font = pygame.font.Font("font/Beyonders-6YoJM.ttf", 20)
        self.font15: pygame.font.Font = pygame.font.Font("font/Beyonders-6YoJM.ttf", 15)
        self.font_10: pygame.font.Font = pygame.font.Font("font/Anta-Regular.ttf", 25)

        self.font_color = pygame.Color(255, 87, 51)

        self.meteorite_spawn_rate: float = 0.5  # hány darab keletkezzen másodpercenként
        self.meteor_spawn_event: int = pygame.event.custom_type()
        Meteorite.create_random(self.screen_resolution)

        self.debris_spawn_rate: float = 0.2
        self.debris_spawn_event: int = pygame.event.custom_type()
        Debris.create_random(self.screen_resolution)
        # Lézerrel kapcsolatos dolgok
        self.laser: Laser = Laser(
            (
                self.screen_resolution[0] - 50,
                self.screen_resolution[1] + self.screen_resolution[1],
            ),
            self.screen,
        )
        self.laser_spawn: int = pygame.event.custom_type()
        self.laser_timer: int = pygame.event.custom_type()
        self.warning_spawn: int = pygame.event.custom_type()
        self.warning_timer: int = pygame.event.custom_type()
        self.laser_back: int = pygame.event.custom_type()
        self.can_count_laser: bool = True
        # Hang----------------------------------------------
        self.sound = Sound()
        self.current_points: int = 0
        self.points: int = 0
        self.point_multiplier: int = 10

        self.upgrade_manager: UpgradeManager = UpgradeManager({})

        self.player.load_upgrades(self.upgrade_manager.get_upgrade_values)

        self.screen_note: bool = False
        self.settings_screen: bool = False

        self.wasd: pygame.Surface = pygame.image.load("img/how to play elements/wasd.png").convert_alpha()
        self.wasd: pygame.Surface = pygame.transform.rotozoom(self.wasd, 0, 0.7)
        
        self.arrows: pygame.Surface = pygame.image.load("img/how to play elements/arrows1.png")
        self.arrows: pygame.Surface = pygame.transform.rotozoom(self.arrows, 0, 0.7)

        self.mouseleft: pygame.Surface = pygame.image.load("img/how to play elements/mouse_left.png")
        self.mouseleft: pygame.Surface = pygame.transform.rotozoom(self.mouseleft, 0, 0.17)
        
        self.mouseleft: pygame.Surface = pygame.image.load("img/how to play elements/mouse_left.png")
        self.mouseleft: pygame.Surface = pygame.transform.rotozoom(self.mouseleft, 0, 0.17)

        self.ss_debris: pygame.Surface = pygame.image.load("img/how to play elements/spaceship_and_debris.png")
        self.collision: pygame.Surface = pygame.image.load("img/how to play elements/collision.png")

        self.text1: Text = Text(
            "Irányítás",
            self.font30,
            (0, 0, 0),
            center=(350, 210)
        )
        self.text2: Text = Text(
            "vagy",
            self.font15,
            (0, 0, 0),
            center=(335, 540)
        )
        self.text3: Text = Text(
            "Játék menete",
            self.font30,
            (0, 0, 0),
            center=(900, 210)
        )
        self.text4: Text = Text(
            ">>   + pont",
            self.font30,
            (0, 0, 0),
            center=(1170, 370)
        )
        self.text5: Text = Text(
            ">>",
            self.font30,
            (0, 0, 0),
            center=(920, 590)
        )
        self.play_again_text: Text = Text(
            "Visszalépéshez nyomd meg szóközt!",
            self.font20,
            (255, 255, 255),
            center=(int(self.screen_resolution[0] / 2), 550),
        )
        self.title_text: Text = Text(
            "Galactic Salvage",
            self.font80,
            (255, 255, 255),
            center=(int(self.screen_resolution[0] / 2), 330),
        )
        self.run_text: Text = Text(
            "Nyomd meg a szóközt az indításhoz!",
            self.font40,
            (255, 255, 255),
            center=(int(self.screen_resolution[0] / 2), 470),
        )
        self.death_text: Text = Text(
            "Meghaltál!", self.font80, (255, 81, 81), center=(800, 450)
        )
        self.laser_button_text: Text = Text(
            "Lézerek ki- és bekapcsolása.\nA játék során plusz pontokat kaphatsz, \nha vállalod ezt a nehezítést.\nA 10. lézer után már egyszerre 2-vel találkozhatsz.",
            self.font15,
            (255, 255, 255),
            topleft=(575, 290),
        )
        self.sound_button_text: Text = Text(
            "Háttérzene kivételével minden hang ki- és bekapcsolása.",
            self.font15,
            (255, 255, 255),
            topleft=(575, 510),
        )
        self.music_button_text: Text = Text(
            "Háttérzene ki- és bekapcsolása.",
            self.font15,
            (255, 255, 255),
            topleft=(575, 685),
        )
        self.help_button: Button = Button(
            (100, 100),
            "?",
            self.font40,
            None,
            "white",
            lambda: self.toggle_screen_note(),
            lambda: self.game_state == GameState["MAIN_MENU"],
            center=(75, 75),
        )
        self.settings_button: Button = Button(
            (400, 100),
            "beállítások",
            self.font30,
            None,
            "white",
            lambda: self.toggle_settings_screen(),
            lambda: self.game_state == GameState["MAIN_MENU"],
            center=(self.screen_resolution[0] - 200, 75),
        )

        self.upgrade_button: Button = Button(
            (250, 100),
            "fejlesztés",
            self.font20,
            (63, 63, 63),
            "white",
            lambda: self.set_game_state(GameState["UPGRADE_MENU"]),
            lambda: self.game_state == GameState["MAIN_MENU"],
            center=(int(self.screen_resolution[0] / 2), 790),
        )
        self.back_button: Button = Button(
            (150, 100),
            "vissza",
            self.font20,
            (63, 63, 63),
            "white",
            lambda: self.set_game_state(GameState["MAIN_MENU"]),
            lambda: self.game_state == GameState["UPGRADE_MENU"],
            center=(100, 100),
        )

        self.laser_button: Button = Button(
            (500, 150),
            "lézer",
            self.font40,
            (255, 81, 81),
            "white",
            lambda: self.toggle_laser(),
            lambda: self.settings_screen,
            center=(300, 350),
        )
        self.sound_button: Button = Button(
            (500, 150),
            "hang",
            self.font40,
            (70, 150, 110),
            "white",
            lambda: self.toggle_sound(),
            lambda: self.settings_screen,
            center=(300, 525),
        )
        self.music_button: Button = Button(
            (500, 150),
            "zene",
            self.font40,
            (70, 150, 110),
            "white",
            lambda: self.toggle_music(),
            lambda: self.settings_screen,
            center=(300, 700),
        )
        self.point_counter: Counter = Counter(
            self.font40, "", (255, 255, 255), center=(300, 100)
        )
        self.in_game_counter: Counter = Counter(
            self.font30, "Jelenlegi pontszámod: ", (255, 255, 255), topleft=(20, 20)
        )

        self.default_background: pygame.Surface = pygame.image.load(
            "img/background/main_menu.png"
        ).convert()
        self.laser_background: pygame.Surface = pygame.image.load(
            "img/background/main_menu_laser.png"
        ).convert()
        self.current_background: pygame.Surface = self.default_background
        self.next_background: pygame.Surface = self.default_background
        self.background_opacity: float = 1

        self.load()

        self.upgrade_cards: list[UpgradeCard] = []
        self.new_upgrades()

    def run(self) -> None:
        # main menu
        bg_surf: pygame.Surface = self.background_generate()

        pygame.time.set_timer(
            self.meteor_spawn_event, int(1000 / self.meteorite_spawn_rate)
        )
        pygame.time.set_timer(
            self.debris_spawn_event, int(1000 / self.debris_spawn_rate)
        )

        pygame.mixer.music.load(self.sound.all_music[self.sound.music_index])
        self.sound.controll_volume()
        pygame.mixer.music.play(-1)

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_state == GameState["IN_GAME"]:
                        self.player.grabber.extend()
                    else:
                        Button.handle_clicks()

                if self.game_state == GameState["IN_GAME"]:
                    if event.type == self.meteor_spawn_event:
                        Meteorite.create_random(self.screen_resolution)
                    if event.type == self.debris_spawn_event:
                        Debris.create_random(self.screen_resolution)

                if self.laser.enabled:
                    if self.laser.all_laser >= 10:
                        self.laser.two_laser = True
                    else:
                        self.laser.two_laser = False
                    if event.type == self.warning_spawn:
                        self.laser.get_pos()
                        self.laser.show_warning = True
                        if self.game_state == GameState["IN_GAME"]:
                            self.sound.play_sound(self.sound.warning)
                        pygame.time.set_timer(self.warning_timer, int(2000), 1)
                    if event.type == self.warning_timer:
                        self.laser.show_warning = False
                        self.laser.laser_go = True
                        if self.game_state == GameState["IN_GAME"]:
                            self.sound.play_sound(self.sound.laser)
                        pygame.time.set_timer(self.laser_timer, int(700), 1)
                    if event.type == self.laser_timer:
                        self.laser.laser_go = False
                        self.laser.all_laser += 1
                # ------------------------------------------------
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.time.set_timer(
                            self.warning_spawn, int(9000)
                        )  # első lézer 9sec
                        if self.game_state == GameState["MAIN_MENU"]:
                            self.set_game_state(GameState["IN_GAME"])

                            pygame.mixer.music.stop()
                            self.sound.music_index += 1
                            self.sound.music_index_controll()
                            pygame.mixer.music.load(
                                self.sound.all_music[self.sound.music_index]
                            )
                            pygame.mixer.music.play(-1)
                        elif (
                            self.game_state == GameState["IN_GAME"] and self.player.dead
                        ):
                            self.reset()
                    if (
                        event.key == pygame.K_r
                        and self.game_state == GameState["UPGRADE_MENU"]
                    ):
                        self.new_upgrades()
            keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
            if self.game_state == GameState["IN_GAME"]:
                self.player.rotate(
                    (keys[pygame.K_LEFT] or keys[pygame.K_a])
                    - (keys[pygame.K_RIGHT] or keys[pygame.K_d])
                )

                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.player.accelerate()
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.player.slow_down()

                self.screen.blit(bg_surf, (0, 0))

                self.in_game_counter.update(self.current_points)
                self.in_game_counter.draw(self.screen)

                Meteorite.meteorites.update(screen=self.screen)  # type: ignore
                Debris.debris_group.update(screen=self.screen)  # type: ignore

                if self.player.dead:
                    self.play_again_text.draw(self.screen)
                    self.death_text.draw(self.screen)

                if self.laser.enabled:
                    self.point_multiplier = 15
                else:
                    self.point_multiplier = 10

                self.current_points += self.player.update() * self.point_multiplier
                self.player.grabber.check_collect(Debris.debris_group.sprites())  # type: ignore
                collision: bool = self.player.check_collision(Meteorite.meteorites.sprites())  # type: ignore

                if collision:
                    self.player.get_hit()
                self.player.draw(self.screen)

                if (
                    self.player.check_kill_collision(
                        self.laser.kill_rect,
                        self.laser.kill_rect_ver,
                        self.laser.direction,
                    )
                    and self.laser.laser_go
                ):
                    self.player.die()

                self.in_game_counter.update(self.current_points)
                self.in_game_counter.draw(self.screen)

                self.laser.update(self.screen)
            elif self.game_state == GameState["MAIN_MENU"]:
                self.change_background()
                self.screen.blit(self.current_background, (0, 0))
                self.help_button.draw(self.screen)
                self.settings_button.draw(self.screen)

                if self.screen_note:
                    pygame.draw.rect(self.screen, "white", (200, 150, 1200, 600), border_radius=50)
                    pygame.draw.rect(self.screen, "black", (500, 150, 10, 600))
                    pygame.draw.rect(self.screen, "black", (200, 250, 1200, 10))

                    self.screen.blit(self.mouseleft, [290, 270])
                    self.screen.blit(self.wasd, [250, 400])
                    self.screen.blit(self.arrows, [250, 570])
                    self.screen.blit(self.ss_debris, [550, 300])
                    self.screen.blit(self.collision, [670, 520])
                    
                    self.text1.draw(self.screen)
                    self.text2.draw(self.screen)
                    self.text3.draw(self.screen)
                    self.text4.draw(self.screen)
                    self.text5.draw(self.screen)


                elif self.settings_screen:
                    self.laser_button.draw(self.screen)
                    self.sound_button.draw(self.screen)
                    self.music_button.draw(self.screen)
                    self.laser_button_text.draw(self.screen)
                    self.sound_button_text.draw(self.screen)
                    self.music_button_text.draw(self.screen)
                else:
                    self.title_text.draw(self.screen)
                    self.run_text.draw(self.screen)

                    self.upgrade_button.draw(self.screen)
            elif self.game_state == GameState["UPGRADE_MENU"]:
                self.change_background()
                self.screen.blit(self.current_background, (0, 0))
                self.point_counter.update(self.points)
                self.point_counter.draw(self.screen)

                self.back_button.draw(self.screen)
                self.draw_upgrade_cards()

            pygame.display.update()
            self.clock.tick(60)

        self.save()
        pygame.quit()

    def reset(self) -> None:
        self.player.reset()

        self.new_upgrades()

        self.set_game_state(GameState["MAIN_MENU"])
        Meteorite.meteorites.empty()  # type: ignore
        Debris.debris_group.empty()  # type: ignore

        self.points += self.current_points * int(
            1 + self.upgrade_manager.get_upgrade_values["ee"]
        )
        self.current_points = 0

        self.laser.all_laser = 0
        pygame.time.set_timer(self.warning_spawn, 0)

        self.save()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.sound.all_music[self.sound.music_index])
        pygame.mixer.music.play(-1)

    def set_game_state(self, state: GameState) -> None:
        self.game_state = state

    def toggle_settings_screen(self) -> None:
        self.settings_screen = not self.settings_screen
        if self.screen_note:
            self.screen_note = False

    def toggle_screen_note(self) -> None:
        self.screen_note = not self.screen_note
        if self.settings_screen:
            self.settings_screen = False

    def draw_upgrade_cards(self) -> None:
        for card in self.upgrade_cards:
            card.draw(self.screen)

    def new_upgrades(self) -> None:
        for upgrade_card in self.upgrade_cards:
            upgrade_card.remove()

        rand_upgrades: list[tuple[str, int, int]] = (
            self.upgrade_manager.get_random_upgrades(3)
        )
        self.upgrade_cards = []

        for index, upgrade in enumerate(rand_upgrades):
            callables: tuple[Callable[[], typing.Any], Callable[[], bool]] = (
                self.create_callables(upgrade[0])
            )
            upgrade_display: tuple[str, str] = self.upgrade_manager.upgrade_display[
                upgrade[0]
            ]
            callables[1]()
            self.upgrade_cards.append(
                UpgradeCard(
                    (200, 300),
                    upgrade_display[0],
                    upgrade[2],
                    self.font20,
                    f"img/upgrades/{upgrade[0]}.png",
                    "black",
                    "white",
                    callables[0],
                    callables[1],
                    upgrade_display[1],
                    self.font_10,
                    center=(400 * (index + 1), 300),
                )
            )

    # don't know why this is needed, but doesn't work without it
    def create_callables(
        self, upgrade_name: str
    ) -> tuple[Callable[[], typing.Any], Callable[[], bool]]:
        return (
            lambda: self.try_buy(upgrade_name),
            lambda: self.upgrade_manager.can_buy(upgrade_name, self.points)
            and self.game_state == GameState["UPGRADE_MENU"],
        )

    def try_buy(self, upgrade_name: str) -> None:
        cost: int = self.upgrade_manager.try_buy(upgrade_name, self.points)
        self.points -= cost
        self.save()
        self.player.load_upgrades(self.upgrade_manager.get_upgrade_values)

    @staticmethod
    def background_generate():
        bg_surf = pygame.image.load("img/background/space.png").convert_alpha()
        return bg_surf

    def toggle_laser(self) -> None:
        self.laser.enabled = not self.laser.enabled
        if self.laser.enabled:
            self.laser_button.bg_color = (70, 150, 110)
            self.next_background = self.laser_background
        else:
            self.laser_button.bg_color = (255, 81, 81)
            self.next_background = self.default_background

    def toggle_sound(self) -> None:
        self.sound.enabled = not self.sound.enabled
        if self.sound.enabled:
            self.sound_button.bg_color = (70, 150, 110)
        else:
            self.sound_button.bg_color = (255, 81, 81)

    def toggle_music(self) -> None:
        self.sound.music_enabled = not self.sound.music_enabled
        if self.sound.music_enabled:
            self.music_button.bg_color = (70, 150, 110)
        else:
            self.music_button.bg_color = (255, 81, 81)

    def change_background(self) -> None:
        self.screen.fill("black")
        self.current_background.set_alpha(int(255 * self.background_opacity))
        if self.current_background == self.next_background:
            self.background_opacity += 0.3
            self.background_opacity = min(self.background_opacity, 1)
            return
        if self.background_opacity <= 0:
            self.current_background = self.next_background
            self.background_opacity = 0
        self.background_opacity -= 0.3

    def save(self) -> None:
        save_dict: dict[str, int | dict[str, int]] = {
            "points": self.points,
            "upgrades": self.upgrade_manager.upgrades,
            "settings": {
                "laser": self.laser.enabled,
                "sound": self.sound.enabled,
                "music": self.sound.music_enabled,
            },
        }
        with open("saves.json", "w", encoding="utf-8") as file:
            json.dump(save_dict, file)

    def load(self) -> None:
        try:
            with open("saves.json", "r", encoding="utf-8") as file:
                load_dict = json.load(file)
        except FileNotFoundError:
            return

        self.points = load_dict.get("points", 0)
        self.upgrade_manager = UpgradeManager(load_dict.get("upgrades", {}))
        self.player.load_upgrades(self.upgrade_manager.get_upgrade_values)

        settings: dict[str, bool] = load_dict.get("settings", {})
        self.laser.enabled = not settings.get("laser", False)
        self.toggle_laser()
        self.sound.enabled = not settings.get("sound", True)
        self.toggle_sound()
        self.sound.music_enabled = not settings.get("music", True)
        self.toggle_music()
