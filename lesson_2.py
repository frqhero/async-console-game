import asyncio
import curses
import logging
import time
from itertools import cycle
from random import choice, randint

from curses_tools import draw_frame, get_frame_size
from game_scenario import PHRASES, get_garbage_delay_tics
from obstacles import obstacles, show_obstacles, obstacles_in_last_collisions
from physics import update_speed
from space_garbage import fly_garbage

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


year = 2010
game_speed = 15


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


async def fire(
    canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0
):
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
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                if obstacle not in obstacles_in_last_collisions:
                    obstacles_in_last_collisions.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def load_frame_from_file(filename):
    with open(filename, 'r') as fd:
        return fd.read()


def has_collided(row, column, obj_size_rows, obj_size_columns):
    for obstacle in obstacles:
        if obstacle.has_collision(row, column, obj_size_rows, obj_size_columns):
            return True


async def show_gameover(canvas):
    frame = load_frame_from_file('frames/game_over.txt')
    max_height, max_width = canvas.getmaxyx()
    while True:
        draw_frame(canvas, max_height / 2, max_width / 2, frame)
        await go_to_sleep(0.1)


async def animate_spaceship(
    canvas, start_row, start_column, frames, coroutines
):
    frames_gen = cycle(frames)
    row, column = start_row, start_column
    max_height, max_width = canvas.getmaxyx()
    row_speed = column_speed = 0

    while True:
        current_frame = next(frames_gen)
        obj_size_rows, obj_size_columns = get_frame_size(current_frame)

        vertical, horizon, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, vertical, horizon
        )

        border_space = 1

        reached_bottom = row + obj_size_rows >= max_height - border_space
        reached_top = row <= 1
        reached_right = column + obj_size_columns == max_width - border_space
        reached_left = column <= 1

        if (
            vertical == 1
            and not reached_bottom
            or vertical == -1
            and not reached_top
        ):
            row += vertical + row_speed

        if (
            horizon == 1
            and not reached_right
            or horizon == -1
            and not reached_left
        ):
            column += horizon + column_speed

        if space_pressed and year >= 2020:
            fire_coro = fire(canvas, row, column + 1)
            coroutines.append(fire_coro)

        if has_collided(row, column, obj_size_rows, obj_size_columns):
            coroutines.append(show_gameover(canvas))
            return

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
        garbage_delay = get_garbage_delay_tics(year)

        if not garbage_delay:
            await go_to_sleep(0.1)
            continue

        await go_to_sleep(garbage_delay / 10)

        new_coroutine = fly_garbage(
            canvas, randint(0, width), choice(garbage_frames), coroutines
        )
        coroutines.append(new_coroutine)
        await go_to_sleep(1)


async def print_info(canvas):
    phrase = ''
    while True:
        der = canvas.derwin(1, 1)
        der.addstr(0, 0, '{}'.format(len(obstacles)))
        der.addstr(1, 0, '{}'.format(len(obstacles_in_last_collisions)))
        der.addstr(2, 0, '{}'.format(year))
        phrase = PHRASES.get(year) or phrase
        der.addstr(3, 0, '{}'.format(' ' * 40))
        der.addstr(3, 0, '{}'.format(phrase))
        await go_to_sleep(0.1)


def draw(canvas):
    curses.curs_set(False)
    
    canvas.nodelay(True)

    height, width = canvas.getmaxyx()
    symbols = '+*.:'

    coroutines = [
        blink(
            canvas,
            randint(1, height - 2),
            randint(1, width - 2),
            choice(symbols),
            randint(0, 3),
        )
        for _ in range(1)
    ]

    frames = get_frames()

    rocket_frames = (
        frames['rocket_frame_1'],
        frames['rocket_frame_1'],
        frames['rocket_frame_2'],
        frames['rocket_frame_2'],
    )

    coroutines.extend(
        [
            animate_spaceship(canvas, 1, 150, rocket_frames, coroutines),
            fill_orbit_with_garbage(canvas, frames, coroutines),
            # show_obstacles(canvas, obstacles),
            print_info(canvas),
        ]
    )

    while True:
        canvas.border()

        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()

        global year, game_speed
        game_speed += 1
        if not game_speed % 15:
            year += 1
        time.sleep(0.1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    curses.update_lines_cols()
    curses.wrapper(draw)
