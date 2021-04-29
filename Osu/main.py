import ctypes
import sys
import pygame as pg
import sdl2
import sdl2.ext
import os
from PIL import Image
from sys import path
from sdl2.test.sdlgfx_test import sdlgfx

NUMBERS = []
factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
for i in range(10):
    NUMBERS.append(sdl2.ext.load_image(f"templates/score-{i}.png"))


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)


class song(sdl2.ext.Applicator):
    def __init__(self, ar, combo, score, timer):
        super().__init__()
        self.componenttypes = combo_sprite, sdl2.ext.Sprite
        self.ar, self.combo, self.score = ar, combo, score
        self.timer = timer
        self.combo_un = None
        self.combo_doz = None
        self.status = True

    def process(self, world, componentsets):
        if self.status:
            self.combo_un.sprite.surface = NUMBERS[self.combo % 10]
            self.combo_doz.sprite.surface = NUMBERS[self.combo // 10]


class note_sprite(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=100, posy=100):
        self.sprite = sprite
        self.sprite.position = posx, posy


class Timer(object):
    def __init__(self):
        super().__init__()
        self.status = True
        self.paused = False
        self.startTicks = sdl2.timer.SDL_GetTicks()

    def stop(self):
        self.status = False
        self.paused = False

    def get_ticks(self):
        return round((sdl2.timer.SDL_GetTicks() - self.startTicks) / 1000, 2)


class Note(sdl2.ext.Applicator):
    def __init__(self, time, ar, index):
        super().__init__()
        self.componenttypes = Timer, note_sprite, sdl2.ext.Sprite
        self.note = None
        self.note2 = None
        self.time = time
        self.is_active = False
        self.ar = ar
        self.index = index
        self.flag, self.wasnt_pressed  = True, True
        self.f = [True, True, True, True]
        self.circle_im = self.draw_circle()


    def check(self, x, y):
        rx = x - (self.note.sprite.x + 70)
        ry = y - (self.note.sprite.y + 70)
        if (rx ** 2 + ry ** 2) < 1400:
            self.note.sprite.surface = sdl2.ext.load_image("templates/hit300.png")
            self.ar = (self.note.timer.get_ticks() + 1) - self.time
            self.wasnt_pressed = False

    def animation(self):
        if self.time + round(self.ar * 0.25, 2) == self.note.timer.get_ticks() and self.f[0]:
            self.note2.sprite.surface = sdl2.ext.load_image(self.circle_im[2])
            self.note2.sprite.x += 17
            self.note2.sprite.y += 17
            self.f[0] = False
        if self.time + round(self.ar * 0.5, 2) == self.note.timer.get_ticks() and self.f[1]:
            self.note2.sprite.surface = sdl2.ext.load_image(self.circle_im[3])
            self.note2.sprite.x += 18
            self.note2.sprite.y += 18
            self.f[1] = False
        if self.time + round(self.ar * 0.75, 2) == self.note.timer.get_ticks() and self.f[2]:
            self.note2.sprite.surface = sdl2.ext.load_image(self.circle_im[4])
            self.note2.sprite.x += 17
            self.note2.sprite.y += 17
            self.f[2] = False
        if self.time + self.ar == self.note.timer.get_ticks() and self.f[3]:
            self.note2.world.delete(self.note2)
            self.f[3] = False

    def process(self, world, componentsets):
        if self.flag:
            if self.time == self.note.timer.get_ticks() and not self.is_active:
                self.is_active = True
                self.note.sprite.surface = sdl2.ext.load_image(self.circle_im[0])
                self.note2.sprite.surface = sdl2.ext.load_image(self.circle_im[1])
            self.animation()
            if self.time + self.ar + 0.5 == self.note.timer.get_ticks():
                if self.wasnt_pressed:
                    self.ar += 1
                    self.wasnt_pressed = False
                    self.note.sprite.surface = sdl2.ext.load_image("templates/hit0-0.png")
                    self.note.sprite.x += 60
                    self.note.sprite.y += 60
                else:
                    self.is_active = False
                    self.note.world.delete(self.note)
                    self.flag = False


    def update(self, x, y, notes):
        if self.wasnt_pressed:
            # for i in notes:
                # if i[1] == True:
                #     if self.index == i[0]:
            self.check(x, y)
            if not self.wasnt_pressed:
                return not self.wasnt_pressed
        else:
            return "tr"

    def draw_circle(self):
        sp = []
        image = Image.open('templates/approachcircle.png')
        size = image.size
        pix = image.load()
        image2 = Image.new("RGB", size)
        for x in range(size[0]):
            for y in range(size[1]):
                image2.putpixel([x, y], pix[x, y])
        image2.save("templates/approachcircle2.png")
        return ["templates/approachcircle.png",
                "templates/approachcircle3.png",
                "templates/approachcircle4.png",
                "templates/approachcircle5.png",
                "templates/approachcircle6.png"]


class Menu_app(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = Menu_sp, sdl2.ext.Sprite

    def process(self, world, componentsets):
        pass


class Menu_sp(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy):
        self.sprite = sprite
        self.sprite.position = posx, posy


class combo_sprite(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx, posy):
        self.sprite = sprite
        self.sprite.position = posx, posy


class score_process():
    def __init__(self, world, score):
        timer1 = Timer()
        game = song(2, 0, 0, timer1)
        world.add_system(game)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        scor = combo_sprite(world, factory.from_surface(
            sdl2.ext.load_image("templates/Total.png")), 90, 500)
        combo_sp_units = combo_sprite(world, factory.from_surface(NUMBERS[0]), 500, 500)
        combo_sp_dozens = combo_sprite(world, factory.from_surface(NUMBERS[0]), 477, 500)
        game.combo_un = combo_sp_units
        game.combo_doz = combo_sp_dozens
        game.scr = scor
        image2 = Image.new("RGB", (1, 1), (0, 0, 0))
        image2.save("templates/pix.png")
        game.combo = int(str(score)[:2])
        running = True
        while running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.key.keysym.sym == sdl2.SDLK_r or \
                        event.type == sdl2.SDL_QUIT:
                    world.delete(game.combo_doz)
                    world.delete(game.combo_un)
                    game.status = False
                    running = False
                    break
            world.process()

class game_process():
    def __init__(self, world):
        f = open("templates/lvl_1.txt").read().split("\n")
        del f[0]
        for i in range(len(f)):
            f[i] = f[i].split()
            f[i][2] = round(float(f[i][2]), 1)
            f[i][1] = int(f[i][1])
            f[i][0] = int(f[i][0])
        timer1 = Timer()
        game = song(2, 0, 0, timer1)
        world.add_system(game)
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        combo_sp_units = combo_sprite(world, factory.from_surface(NUMBERS[0]), 100, 1000)
        combo_sp_dozens = combo_sprite(world, factory.from_surface(NUMBERS[0]), 77, 1000)
        game.combo_un = combo_sp_units
        game.combo_doz = combo_sp_dozens
        image2 = Image.new("RGB", (1, 1), (0, 0, 0))
        image2.save("templates/pix.png")
        space = []
        n = 0
        for i in f:
            note = Note(i[2], game.ar, n)
            world.add_system(note)
            texture = sdl2.ext.load_image("templates/pix.png")
            texture2 =sdl2.ext.load_image("templates/pix.png")
            note_pic = factory.from_surface(texture)
            note_pic2 = factory.from_surface(texture)
            note_sp = note_sprite(world, note_pic, posx=i[0], posy=i[1])
            note_sp2 = note_sprite(world, note_pic2, posx=i[0] - 70, posy=i[1] - 70)
            note_sp.timer = timer1
            note_sp2.timer = timer1
            note.note = note_sp
            note.note2 = note_sp2
            space.append(note)
            n += 1



        pg.mixer.music.play()
        pg.mixer.music.set_volume(0.1)
        running = True
        while running:
            events = sdl2.ext.get_events()
            for event in events:
                motion = None
                if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    motion = event.motion
                    active_notes = []
                    for note_ob in space:
                        if note_ob.is_active:
                            active_notes.append([note_ob.index, note_ob.wasnt_pressed])
                            if motion:
                                stat = note_ob.update(motion.x, motion.y, active_notes)
                                if stat:
                                    if stat == "tr":
                                        game.combo = 0
                                    else:
                                        game.combo += 1
                                        game.score += 300 + (300 * (game.combo - 1) // 10)

                        elif active_notes and not note_ob.is_active:
                            break
                if event.key.keysym.sym == sdl2.SDLK_r or \
                        event.type == sdl2.SDL_QUIT:
                    for i in space:
                        i.flag = False
                        world.delete(i.note)
                        world.delete(i.note2)
                    world.delete(game.combo_doz)
                    world.delete(game.combo_un)
                    game.status = False
                    pg.mixer.music.stop()
                    running = False
                    break
                if int(game.timer.get_ticks()) == 40:
                    for i in space:
                        i.flag = False
                        world.delete(i.note)
                        world.delete(i.note2)
                    world.delete(game.combo_doz)
                    world.delete(game.combo_un)
                    game.status = False
                    pg.mixer.music.stop()
                    score_process(world, game.score)
                    running = False
                    break
            world.process()


def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("Osu", size=(1920, 1080))
    menu = sdl2.ext.World()
    gameplay = sdl2.ext.World()

    spriterenderer = SoftwareRenderer(window)
    menu.add_system(spriterenderer)
    gameplay.add_system(spriterenderer)
    window.show()
    running = True

    lvl_1 = Menu_app()
    lvl_2 = Menu_app()
    menu.add_system(lvl_1)
    menu.add_system(lvl_2)
    texture = sdl2.ext.load_image("templates/1.png")
    escape = sdl2.ext.load_image("templates/escape.png")
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    menu_pic = factory.from_surface(texture)
    escape_pic = factory.from_surface(escape)
    escape_sp = note_sprite(menu, escape_pic, 0, 0)
    Menu_sp = note_sprite(menu, menu_pic, 538, 144)
    lvl_2.sp = escape_pic
    lvl_1.sp = Menu_sp
    pg.init()
    pg.mixer.music.load('templates/audio.wav')

    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                motion = event.motion
                if motion.x >= 354 and motion.x <= 1382 and motion.y >= 134 and motion.y <= 538:
                    game_process(gameplay)
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        menu.process()
    return 0


if __name__ == "__main__":
    sys.exit(run())
