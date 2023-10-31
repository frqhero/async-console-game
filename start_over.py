import asyncio
from random import choice, randint
import time
import curses


async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await go_to_sleep(2)

        canvas.addstr(row, column, symbol)
        await go_to_sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await go_to_sleep(0.5)

        canvas.addstr(row, column, symbol)
        await go_to_sleep(0.3)


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()

    canvas_height, canvas_width = canvas.getmaxyx()
    print(canvas_height, canvas_width)
    symbols = '+*.:'

    coroutines = [
        blink(
            canvas,
            randint(1, canvas_height - 2),
            randint(1, canvas_width - 2),
            choice(symbols),
        )
        for _ in range(3)
    ]

    while True:
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
