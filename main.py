import time
import curses


def draw(canvas):
    curses.curs_set(0)

    while True:
        row, column  = 5, 20
        canvas.addch(row, column, '*', curses.A_DIM)
        canvas.refresh()
        time.sleep(2)
        canvas.addch(row, column, '*')
        canvas.refresh()
        time.sleep(0.3)
        canvas.addch(row, column, '*', curses.A_BOLD)
        canvas.refresh()
        time.sleep(0.5)
        canvas.addch(row, column, '*')
        canvas.refresh()
        time.sleep(0.3)

  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
