import asyncio
import curses
import time


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


def main(canvas):
    height, width = canvas.getmaxyx()

    start_row = height - 2
    start_col = width / 2
    coro_shot = fire(canvas, start_row, start_col)
    coroutines = []
    coroutines.append(coro_shot)

    while True:
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
