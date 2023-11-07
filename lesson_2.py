import asyncio
import logging
from random import choice, randint
from itertools import cycle
import time
import curses

from curses_tools import draw_frame
from space_garbage import fly_garbage


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


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
    

def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas, start_row, start_column, frames):
    frames_gen = cycle(frames)
    row, column = start_row, start_column
    max_height, max_width = canvas.getmaxyx()

    while True:
        current_frame = next(frames_gen)
        number_of_rows, number_of_columns = get_frame_size(current_frame)

        vertical, horizon, _ = read_controls(canvas)

        border_space = 1

        reached_bottom = row + number_of_rows >= max_height - border_space
        reached_top = row <= 1
        reached_right = column + number_of_columns == max_width - border_space
        reached_left = column <= 1

        if (vertical == 1 and not reached_bottom or
                vertical == -1 and not reached_top):
            row += vertical

        if (horizon == 1 and not reached_right or
                horizon == -1 and not reached_left):
            column += horizon

        draw_frame(canvas, row, column, current_frame)
        await go_to_sleep(0.1)
        draw_frame(canvas, row, column, current_frame, negative=True)


def get_frames():
    return {
        'duck': load_frame_from_file('frames/duck.txt'),
        'hubble': load_frame_from_file('frames/hubble.txt'),
        'lamp': load_frame_from_file('frames/lamp.txt'),
        's': load_frame_from_file('frames/s.txt'),
        'trash_large': load_frame_from_file('frames/trash_large.txt'),
        'trash_xl': load_frame_from_file('frames/trash_xl.txt'),
        'rocket_frame_1': load_frame_from_file('frames/rocket_frame_1.txt'),
        'rocket_frame_2': load_frame_from_file('frames/rocket_frame_2.txt'),
    }


def get_garbage_coroutines(canvas, frames):
    return [
        fly_garbage(canvas, 5, frames['s']),
        fly_garbage(canvas, 15, frames['trash_large']),
        fly_garbage(canvas, 35, frames['trash_xl']),
    ]


async def fill_orbit_with_garbage(canvas, frames, coroutines):
    _, width = canvas.getmaxyx()
    garbage_frames = [
        frames['s'],
        frames['trash_large'],
        frames['trash_xl'],
    ]
    while True:
        new_coroutine = fly_garbage(canvas, randint(0, width), choice(garbage_frames))
        coroutines.append(new_coroutine)
        await go_to_sleep(1)


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

    
    frames = get_frames()

    rocket_frames = (
        frames['rocket_frame_1'],
        frames['rocket_frame_1'],
        frames['rocket_frame_2'],
        frames['rocket_frame_2'],
    )

    rocket_coro = animate_spaceship(canvas, 1, 150, rocket_frames)
    coroutines.append(rocket_coro)

    garbage_coroutines = get_garbage_coroutines(canvas, frames)
    coroutines = coroutines + garbage_coroutines

    filling_garbage_coroutine = fill_orbit_with_garbage(canvas, frames, coroutines)
    coroutines.append(filling_garbage_coroutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    curses.update_lines_cols()
    curses.wrapper(draw)
