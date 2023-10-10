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
    curses.curs_set(0)

    # while True:
    #     row, column  = 5, 20
    #     canvas.addch(row, column, '*', curses.A_DIM)
    #     canvas.refresh()
    #     time.sleep(2)
    #     canvas.addch(row, column, '*')
    #     canvas.refresh()
    #     time.sleep(0.3)
    #     canvas.addch(row, column, '*', curses.A_BOLD)
    #     canvas.refresh()
    #     time.sleep(0.5)
    #     canvas.addch(row, column, '*')
    #     canvas.refresh()
    #     time.sleep(0.3)
    row, column  = 5, 20
    coroutine = blink(canvas, row, column)

    coroutine.send(None)
    canvas.refresh()
    time.sleep(2)

    coroutine.send(None)
    canvas.refresh()
    time.sleep(0.3)

    coroutine.send(None)
    canvas.refresh()
    time.sleep(0.5)

    coroutine.send(None)
    canvas.refresh()
    time.sleep(0.3)

    time.sleep(1)


  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
