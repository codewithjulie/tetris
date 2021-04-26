"""
File: tetris_3.0.py
----------------
TODO: Fix rotating clipping objects and floor
TODO: Show preview (spawn tetromino above the canvas, move once previous tetromino is placed)
TODO: Legal move for rotating pieces
TODO: Could I make the line flash before it disappears?
TODO: Decompose objects_left, objects_right, objects_below
TODO: Create levels with squares in the way
TODO: Pause the game
"""

import tkinter
import random
import time
import math
from playsound import playsound

# Constants for canvas
CANVAS_WIDTH = 900
GAME_BOARD_WIDTH = 500      # Width of drawing canvas in pixels
CANVAS_HEIGHT = 1000    # Height of drawing canvas in pixels
CANVAS_MID = GAME_BOARD_WIDTH // 2
SQUARE_LENGTH = 50          # Size of unit square within tetromino
Y_SPEED = SQUARE_LENGTH
X_SPEED = SQUARE_LENGTH


# Vertices for individual squares, created above the canvas, o and l are spawned in middle
# The rest of the tetrominos are spawned middle left
SHAPES = {
    'SQUARE_1_POINTS' : [CANVAS_MID - SQUARE_LENGTH * 2, -SQUARE_LENGTH * 3, CANVAS_MID - SQUARE_LENGTH, -SQUARE_LENGTH * 2],
    'SQUARE_2_POINTS' : [CANVAS_MID - SQUARE_LENGTH, -SQUARE_LENGTH * 3, CANVAS_MID, -SQUARE_LENGTH * 2],
    'SQUARE_3_POINTS' : [CANVAS_MID, -SQUARE_LENGTH * 3, CANVAS_MID + SQUARE_LENGTH, -SQUARE_LENGTH * 2],
    'SQUARE_4_POINTS' : [CANVAS_MID + SQUARE_LENGTH, -SQUARE_LENGTH * 3, CANVAS_MID + SQUARE_LENGTH * 2, -SQUARE_LENGTH * 2],
    'SQUARE_5_POINTS' : [CANVAS_MID - SQUARE_LENGTH * 2, -SQUARE_LENGTH * 2, CANVAS_MID - SQUARE_LENGTH, -SQUARE_LENGTH],
    'SQUARE_6_POINTS' : [CANVAS_MID - SQUARE_LENGTH, -SQUARE_LENGTH * 2, CANVAS_MID, -SQUARE_LENGTH],
    'SQUARE_7_POINTS' : [CANVAS_MID, -SQUARE_LENGTH * 2, CANVAS_MID + SQUARE_LENGTH, -SQUARE_LENGTH],
    'SQUARE_8_POINTS' : [CANVAS_MID + SQUARE_LENGTH, -SQUARE_LENGTH * 2, CANVAS_MID + SQUARE_LENGTH * 2, -SQUARE_LENGTH],
}


def create_game_board():
    canvas = make_canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Tetris 3.0')
    draw_grid(canvas)
    return canvas


def create_summary_board(canvas):
    # Covers the whole summary board
    canvas.create_rectangle(
        GAME_BOARD_WIDTH, 0, CANVAS_WIDTH, CANVAS_HEIGHT,
        fill='grey50',
    )
    # Next tetromino board and text label
    canvas.create_rectangle(
        GAME_BOARD_WIDTH + SQUARE_LENGTH, SQUARE_LENGTH, CANVAS_WIDTH - SQUARE_LENGTH, SQUARE_LENGTH * 6,
        fill='black'
    )
    canvas.create_text(
        GAME_BOARD_WIDTH + (CANVAS_WIDTH - GAME_BOARD_WIDTH) // 2, SQUARE_LENGTH * 1.5,
        fill='white', 
        font='Times 26 bold', 
        text='Next Block'
    )

    # Creates level board and text label
    canvas.create_rectangle(
        GAME_BOARD_WIDTH + SQUARE_LENGTH, SQUARE_LENGTH * 8.5, CANVAS_WIDTH - SQUARE_LENGTH, SQUARE_LENGTH * 12.5,
        fill='black'
    )
    canvas.create_text(
        GAME_BOARD_WIDTH + (CANVAS_WIDTH - GAME_BOARD_WIDTH) // 2, SQUARE_LENGTH * 9,
        fill='white', 
        font='Times 26 bold', 
        text='Level'
    )

    # Creates score board and text label
    canvas.create_rectangle(
        GAME_BOARD_WIDTH + SQUARE_LENGTH, SQUARE_LENGTH * 15, CANVAS_WIDTH - SQUARE_LENGTH, CANVAS_HEIGHT - SQUARE_LENGTH,
        fill='black'
    )
    canvas.create_text(
        GAME_BOARD_WIDTH + (CANVAS_WIDTH - GAME_BOARD_WIDTH) // 2, CANVAS_HEIGHT - SQUARE_LENGTH * 4.5,
        fill='white', 
        font='Times 26 bold', 
        text='Score'
    )


def create_score_label(canvas, total_score):
    return canvas.create_text(
        GAME_BOARD_WIDTH + (CANVAS_WIDTH - GAME_BOARD_WIDTH) // 2, CANVAS_HEIGHT - SQUARE_LENGTH * 3,
        fill='white', 
        font='Times 24', 
        text=f'{total_score}'
    )


def create_level_label(canvas, level):
    return canvas.create_text(
        GAME_BOARD_WIDTH + (CANVAS_WIDTH - GAME_BOARD_WIDTH) // 2, CANVAS_HEIGHT - SQUARE_LENGTH * 9.5,
        fill='white', 
        font='Times 24', 
        text=f'{level}'
    )


def move_tetromino(canvas, tetromino, x, y):  # Tetrominos are made of 4 squares, must move all 4 squares in tandem
    for i in range(4):
        canvas.move(tetromino[i], x, y)


def make_tetromino_fall(canvas, tetromino, level):
    while not touching_game_floor(canvas, tetromino) and not objects_below(canvas, tetromino):
        move_tetromino(canvas, tetromino, 0, Y_SPEED)

        canvas.update()
        time.sleep(1 / (level / 2 + 3))  # Calculation for fall speed based on level


def touching_game_floor(canvas, tetromino):
    return get_bottom_y(canvas, tetromino) >= CANVAS_HEIGHT


def objects_below(canvas, tetromino):
    coords = get_tetromino_coords(canvas, tetromino)  # Returns list of 4 lists
    for coord in coords:
        bottom_y, right_x, left_x, top_y = get_coord_sides(canvas, tetromino, coord)

        for neighbor in bottom_y:
            if 'tetromino' in canvas.gettags(neighbor) and not is_self(canvas, tetromino, neighbor):
                if neighbor in right_x and neighbor in left_x:
                    return True
    return False


def objects_below_down_arrow(canvas, tetromino):
    coords = get_tetromino_coords(canvas, tetromino)  # Returns list of 4 lists
    for coord in coords:
        bottom_y, right_x, left_x, top_y = get_coord_sides(canvas, tetromino, coord)
        for neighbor in bottom_y:
            if 'tetromino' in canvas.gettags(neighbor) and not is_self(canvas, tetromino, neighbor):
                if neighbor in right_x and neighbor in left_x:
                    return True
    return False


def is_self(canvas, tetromino, object_num):
    """
    This function detects if an object number is itself.
    Note: each tetromino is made of 4 squares, each with its own object number
    """
    if object_num < tetromino[0] or object_num > tetromino[3]:
        return False
    return True


def get_coord_sides(canvas, tetromino, coord):
    x1, y1, x2, y2 = coord[0], coord[1], coord[2], coord[3]
    coord_bottom_y = canvas.find_overlapping(x1, y2, x2, y2)
    coord_right_x = canvas.find_overlapping(x2, y1, x2, y2)
    coord_left_x = canvas.find_overlapping(x1, y1, x1, y2)
    coord_top_y = canvas.find_overlapping(x1, y1, x2, y1)
    return (coord_bottom_y, coord_right_x, coord_left_x, coord_top_y)


def objects_left(canvas, tetromino):
    coords = get_tetromino_coords(canvas, tetromino)
    for coord in coords:
        bottom_y, right_x, left_x, top_y = get_coord_sides(canvas, tetromino, coord)
        for neighbor in left_x:
            if 'tetromino' in canvas.gettags(neighbor) and not is_self(canvas, tetromino, neighbor):
                if neighbor in top_y and neighbor in bottom_y:
                    return True
    return False


def objects_right(canvas, tetromino):
    coords = get_tetromino_coords(canvas, tetromino)
    for coord in coords:
        bottom_y, right_x, left_x, top_y = get_coord_sides(canvas, tetromino, coord)
        for neighbor in right_x:
            if 'tetromino' in canvas.gettags(neighbor) and not is_self(canvas, tetromino, neighbor):
                if neighbor in top_y and neighbor in bottom_y:
                    return True
    return False


def valid_move(canvas, tetromino):
    if get_left_x(canvas, tetromino) <= 0:
        return False
    if get_right_x(canvas, tetromino) >= GAME_BOARD_WIDTH:
        return False
    return True

    
# Get position functions
def get_all_x_y_coords(canvas, tetromino):
    tetromino_coords = get_tetromino_coords(canvas, tetromino)
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    for tetra_coord in tetromino_coords:
        x1.append(tetra_coord[0])
        y1.append(tetra_coord[1])
        x2.append(tetra_coord[2])
        y2.append(tetra_coord[3])
    return tuple([x1, y1, x2, y2])


def get_left_x(canvas, tetromino):
    coords = get_all_x_y_coords(canvas, tetromino)
    return min(coords[0])


def get_top_y(canvas, tetromino):
    coords = get_all_x_y_coords(canvas, tetromino)
    return min(coords[1])


def get_right_x(canvas, tetromino):
    coords = get_all_x_y_coords(canvas, tetromino)
    return max(coords[2])


def get_bottom_y(canvas, tetromino):
    coords = (get_all_x_y_coords(canvas, tetromino))
    return max(coords[3])


def make_randomized_tetromino(canvas):
    num = random.randint(1, 7)
    if num == 1:
        return make_z_tetromino(canvas)
    elif num == 2:
        return make_s_tetromino(canvas)
    elif num == 3:
        return make_t_tetromino(canvas)
    elif num == 4:
        return make_l_tetromino(canvas)
    elif num == 5:
        return make_j_tetromino(canvas)
    elif num == 6:
        return make_long_rect(canvas)
    elif num == 7:
        return make_square_tetromino(canvas)


# Create tetromino functions
def make_z_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_7_POINTS'], 'red', tags='zee')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'red', tags='zee')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_2_POINTS'], 'red', tags='zee')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_1_POINTS'], 'red', tags='zee')

    canvas.addtag_withtag('tetromino', 'zee')

    return [square1, square2, square3, square4]


def make_s_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_5_POINTS'], 'green', tags='es')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'green', tags='es')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_2_POINTS'], 'green', tags='es')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_3_POINTS'], 'green', tags='es')

    canvas.addtag_withtag('tetromino', 'es')

    return [square1, square2, square3, square4]


def make_t_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_2_POINTS'], 'purple', tags='tee')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_5_POINTS'], 'purple', tags='tee')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'purple', tags='tee')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_7_POINTS'], 'purple', tags='tee')

    canvas.addtag_withtag('tetromino', 'tee')

    return [square1, square2, square3, square4]


def make_l_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_3_POINTS'], 'orange', tags='el')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_7_POINTS'], 'orange', tags='el')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'orange', tags='el')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_5_POINTS'], 'orange', tags='el')

    canvas.addtag_withtag('tetromino', 'el')

    return [square1, square2, square3, square4]


def make_j_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_1_POINTS'], 'blue', tags='jay')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_5_POINTS'], 'blue', tags='jay')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'blue', tags='jay')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_7_POINTS'], 'blue', tags='jay')

    canvas.addtag_withtag('tetromino', 'jay')

    return [square1, square2, square3, square4]


def make_long_rect(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_1_POINTS'], 'cyan', tags='long_rect')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_2_POINTS'], 'cyan', tags='long_rect')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_3_POINTS'], 'cyan', tags='long_rect')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_4_POINTS'], 'cyan', tags='long_rect')

    canvas.addtag_withtag('tetromino', 'long_rect')

    return [square1, square2, square3, square4]


def make_square_tetromino(canvas):
    square1 = make_unit_square(canvas, SHAPES['SQUARE_2_POINTS'], 'yellow', tags='square')
    square2 = make_unit_square(canvas, SHAPES['SQUARE_3_POINTS'], 'yellow', tags='square')
    square3 = make_unit_square(canvas, SHAPES['SQUARE_6_POINTS'], 'yellow', tags='square')
    square4 = make_unit_square(canvas, SHAPES['SQUARE_7_POINTS'], 'yellow', tags='square')

    canvas.addtag_withtag('tetromino', 'square')

    return [square1, square2, square3, square4]


def make_unit_square(canvas, square, color, tags):
    return canvas.create_rectangle(square[0], square[1], square[2], square[3], outline='grey30', fill=color, tags=tags)


def make_canvas(width, height, title):
    """
    Create a canvas with specified dimension
    """
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1, bg='black')
    canvas.pack()
    return canvas


def draw_grid(canvas):
    for i in range(0, CANVAS_HEIGHT + 1, SQUARE_LENGTH):
        canvas.create_line(0, i, GAME_BOARD_WIDTH, i, fill='grey10')
    for i in range(SQUARE_LENGTH, GAME_BOARD_WIDTH, SQUARE_LENGTH):
        canvas.create_line(i, 0, i, CANVAS_HEIGHT, fill='grey10')


def remove_completed_row(canvas):
    rows_removed = 0
    for y in range(-1, CANVAS_HEIGHT - SQUARE_LENGTH, SQUARE_LENGTH):
        overlap = canvas.find_enclosed(-1, y, GAME_BOARD_WIDTH + 1, y + 52)
        if len(overlap) > 11:
            for item in overlap:
                if 'tetromino' in canvas.gettags(item):
                    canvas.delete(item)
                    rows_removed += 1
            squares_above_line = canvas.find_enclosed(-1, -1, GAME_BOARD_WIDTH + 1, overlap[0] * SQUARE_LENGTH)
            time.sleep(1/5)
            for square in squares_above_line:
                if 'tetromino' in canvas.gettags(square):
                    canvas.move(square, 0, SQUARE_LENGTH)
    return rows_removed // 10
    

def rotate(canvas, tetromino):
    """
    Pivot = Obtain the coordinates for the square that will not be moving
    All the other squares will move around this square
    In this game, this square will always be the third square in 'tetromino'
    """
    pivot = (get_tetromino_coords(canvas, tetromino)[2])
    px1 = pivot[0]
    py1 = pivot[1]
    px2 = pivot[2]
    py2 = pivot[3]
    lst = tetromino.copy()
    lst.pop(2)

    # Something to add to not rotate a square
    overlap = canvas.find_overlapping(px2, py1, px2, py1)
    count = 0
    for item in overlap:
        if 'tetromino' in canvas.gettags(item):
            count += 1
    if count == 4:
        return

    for square in lst:
        coord = canvas.coords(square)
        bx1 = coord[0]
        by1 = coord[1]
        bx2 = coord[2]
        by2 = coord[3]
        
        x_diff = bx1 - px1
        y_diff = by1 - py1

        x_move = -x_diff + y_diff
        y_move = -x_diff - y_diff

        canvas.move(square, x_move, y_move)


def move_left(canvas, tetromino):
    if get_left_x(canvas, tetromino) >= 0 + SQUARE_LENGTH and not objects_left(canvas, tetromino):
        move_tetromino(canvas, tetromino, -SQUARE_LENGTH, 0)


def move_right(canvas, tetromino):
    if get_right_x(canvas, tetromino) <= GAME_BOARD_WIDTH - SQUARE_LENGTH and not objects_right(canvas, tetromino):
        move_tetromino(canvas, tetromino, SQUARE_LENGTH, 0)


def rotate_tetromino(canvas, tetromino):
    rotate(canvas, tetromino)
    while get_left_x(canvas, tetromino) < 0:
        move_tetromino(canvas, tetromino, SQUARE_LENGTH, 0)
    while get_right_x(canvas, tetromino) > GAME_BOARD_WIDTH:
        move_tetromino(canvas, tetromino, -SQUARE_LENGTH, 0)


def move_down(canvas, tetromino):
    if get_bottom_y(canvas, tetromino) <= CANVAS_HEIGHT - SQUARE_LENGTH * 2 and not objects_below_down_arrow(canvas, tetromino):
        move_tetromino(canvas, tetromino, 0, SQUARE_LENGTH)


def hard_drop(canvas, tetromino):
    while not touching_game_floor(canvas, tetromino) and not objects_below(canvas, tetromino):
        move_tetromino(canvas, tetromino, 0, Y_SPEED)
        canvas.update()
        time.sleep(1 / 3000)


def key_pressed(event, canvas, tetromino, level):
    """
    Respond to different arrow keys
    This was written with the help of Code In Place Section Leader
    """
    sym = event.keysym.lower()
    if sym == 'left':
        move_left(canvas, tetromino)
    elif sym == 'right':
        move_right(canvas, tetromino)
    elif sym == 'up':
        rotate_tetromino(canvas, tetromino)
    elif sym == 'down':
        move_down(canvas, tetromino)
    elif sym == 'space':
        hard_drop(canvas, tetromino)
    while sym == 'p':
        canvas.config(state='disabled')
        canvas.update()
        if sym == 'r':
            canvas.config(state='normal')
            canvas.update()
    while sym == 'r':
        canvas.config(state='normal')
        canvas.update()


def get_tetromino_coords(canvas, tetromino):
    """ Gets the coordinates of all the squares as a list of lists """
    tetromino_coords = []
    for tetra in tetromino:
        tetromino_coords.append(canvas.coords(tetra))
    return tetromino_coords


def game_over(canvas):
    return len(canvas.find_enclosed(-1, -1, GAME_BOARD_WIDTH + 1, SQUARE_LENGTH + 1)) > 4


def get_score(rows_removed, level):
    update_score = 0
    if rows_removed == 1:
        update_score += 40 * (level + 1)
    elif rows_removed == 2:
        update_score += 100 * (level + 1)
    elif rows_removed == 3:
        update_score += 300 * (level + 1)
    elif rows_removed == 4:
        update_score += 1200 * (level + 1)
    return update_score


def play_tetromino(canvas, level, tetromino):
    """ Plays one tetromino until it is placed """
    canvas.bind('<Key>', lambda event: key_pressed(event, canvas, tetromino, level))
    canvas.focus_set()  # Canvas now has the keyboard focus
    make_tetromino_fall(canvas, tetromino, level)


def display_game_over(canvas, level, total_score, total_rows_removed):
    # Create gray 'transparent' overlay
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill='grey25', stipple='gray75')

    # Create text - GAME OVER, final level, final score, and total rows cleared
    canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 3, font='Times 40 bold', text='GAME OVER!', fill='white')
    canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, font='Times 25 bold', text=f"You reached level {level}!", fill='white')
    canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT - CANVAS_HEIGHT // 3, font='Times 25 bold', text=f"Your score: {total_score}", fill='white')
    canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT - CANVAS_HEIGHT // 4, font='Times 25 bold', text=f"Rows cleared: {total_rows_removed}", fill='white')


def create_preview(canvas, next_tetromino):
    """
    Using tags, map the tag shape to the function name to create the preview
    """
    function_mapping = {
        'square' : make_square_tetromino(canvas),
        'long_rect' : make_long_rect(canvas),
        'zee' : make_z_tetromino(canvas),
        'es' : make_s_tetromino(canvas),
        'jay' : make_j_tetromino(canvas),
        'el' : make_l_tetromino(canvas),
        'tee' : make_t_tetromino(canvas),
    }
    tags = canvas.gettags(next_tetromino[0])
    tetromino = function_mapping[tags[0]]

    move_tetromino(canvas, tetromino, GAME_BOARD_WIDTH - SQUARE_LENGTH, SQUARE_LENGTH * 6)

    return tetromino


def reveal_tetromino(canvas, tetromino):
    """ 
    Needed in order to spawn next_tetromino with no errors
    Drops tetromino to the top of game_board
    """
    move_tetromino(canvas, tetromino, 0, SQUARE_LENGTH * 2)


def main():
    canvas = create_game_board()  # Includes canvas and grid lines
    create_summary_board(canvas)

    total_score = total_rows_removed = level = 0

    score_label = create_score_label(canvas, total_score)
    level_label = create_level_label(canvas, level)
    tetromino = make_randomized_tetromino(canvas)  # Spawned above the game board
    playsound("tetris_theme_song.mp3", block=False)

    while not game_over(canvas):

        reveal_tetromino(canvas, tetromino)

        next_tetromino = make_randomized_tetromino(canvas)
        preview = create_preview(canvas, next_tetromino)

        play_tetromino(canvas, level, tetromino)

        rows_removed = remove_completed_row(canvas)
        total_rows_removed += rows_removed
        level = (total_rows_removed // 10)  # For every 10 rows removed, level increases by 1

        total_score += get_score(rows_removed, level)

        if get_score(rows_removed, level) > 0:  # Update the score if rows were removed
            canvas.delete(score_label)
            score_label = create_score_label(canvas, total_score)

        canvas.delete(level_label)  # Currently updates every play, change to increase level
        level_label = create_level_label(canvas, level)
        tetromino = next_tetromino
        for i in range(4):
            canvas.delete(preview[i])


    display_game_over(canvas, level, total_score, total_rows_removed)
    canvas.mainloop()


if __name__ == '__main__':
    main()
