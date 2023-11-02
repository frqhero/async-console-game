import asyncio
from random import choice, randint
from itertools import cycle
import time
import curses


async def go_to_sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', offset=1):
    while True:
        if offset == 0:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await go_to_sleep(2)
            offset += 1

        if offset == 1:
            canvas.addstr(row, column, symbol)
            await go_to_sleep(0.3)
            offset += 1

        if offset == 2:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await go_to_sleep(0.5)
            offset += 1

        if offset == 3:
            canvas.addstr(row, column, symbol)
            await go_to_sleep(0.3)
            offset = 0


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def load_frame_from_file(filename):
    with open(filename, 'r') as fd:
        return fd.read()
    

def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_frames(canvas, start_row, start_column, frames):
    frames_gen = cycle(frames)

    while True:
        current_frame = next(frames_gen)
        draw_frame(canvas, start_row, start_column, current_frame)
        await go_to_sleep(0.3)
        draw_frame(canvas, start_row, start_column, current_frame, negative=True)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    symbols = '+*.:'

    coroutines = [
        blink(
            canvas,
            randint(1, height - 2),
            randint(1, width - 2),
            choice(symbols),
            randint(0, 3)
        )
        for _ in range(50)
    ]

    fire_coro = fire(canvas, height - 2, width / 2)
    coroutines.append(fire_coro)

    rocket_frame_1 = load_frame_from_file(
        'frames/rocket_frame_1.txt'
    )
    rocket_frame_2 = load_frame_from_file(
        'frames/rocket_frame_2.txt'
    )

    rocket_frames = (rocket_frame_1, rocket_frame_2)
    # draw_frame(canvas, 1, 10, rocket_frame_1)
    # canvas.refresh()

    rocket_coro = animate_frames(canvas, 1, 10, rocket_frames)
    coroutines.append(rocket_coro)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
