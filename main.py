"""Ponto de entrada. Loop async (exigido pelo pygbag) com passo fixo de 60 Hz."""
import asyncio
import time

import pygame

from src import config
from src.display import Display
from src.input import Input
from src.states.manager import StateManager
from src.states.title import Title
from src.touch import TouchControls


async def main():
    pygame.init()
    display = Display()
    inp = Input()
    display.touch = TouchControls()
    states = StateManager(Title())
    clock = pygame.time.Clock()

    running = True
    accumulator = 0.0
    last = time.perf_counter()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            inp.handle_event(event)
            display.touch.handle_event(event, display, inp)

        now = time.perf_counter()
        accumulator += min(now - last, config.MAX_FRAME_TIME)
        last = now

        while accumulator >= config.DT:
            states.update(config.DT, inp)
            inp.end_tick()
            accumulator -= config.DT

        states.draw(display.canvas)
        display.present()

        clock.tick(config.UPDATE_HZ)
        await asyncio.sleep(0)  # cede o controle ao navegador (pygbag)

    pygame.quit()


asyncio.run(main())
