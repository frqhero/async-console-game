import asyncio
import time
import curses


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()

    coroutines = [
        blink(canvas, row, counter)
        for counter in range(20, 30, 2)
    ]

    while True:
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(2)
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(0.5)
        for my_coroutine in coroutines:
            my_coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)

  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
