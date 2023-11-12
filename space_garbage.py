import asyncio
import uuid

from curses_tools import draw_frame, get_frame_size
from explosion import explode
from obstacles import Obstacle, obstacles, obstacles_in_last_collisions


async def fly_garbage(canvas, column, garbage_frame, coroutines, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    uid = uuid.uuid4()
    obstacle = Obstacle(row, column, frame_rows, frame_columns, uid=uid)
    obstacles.append(obstacle)

    while row < rows_number:
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            coroutines.append(explode(canvas, row, column))
            break

        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

    obstacles.remove(obstacle)
