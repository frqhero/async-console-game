import uuid
from curses_tools import draw_frame
import asyncio
from main import get_frame_size

from obstacles import Obstacle, obstacles


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    frame_rows, frame_columns = get_frame_size(garbage_frame)

    uid = uuid.uuid4()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    obstacle = Obstacle(row, column, frame_rows, frame_columns, uid=uid)
    obstacles.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, row, column, obstacle.get_bounding_box_frame())
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, obstacle.get_bounding_box_frame(), negative=True)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
    obstacles.remove(obstacle)
