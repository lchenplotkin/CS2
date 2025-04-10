import pygame
import numpy as np
import os

"""START LESSON PART"""
kernel = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # EASY METHOD

fps = 10
dim = (30, 30)
board = np.zeros(dim, dtype=int)
S = [2, 3]
B = [3]

def count_neighbors(x, y):
    neighbors = 0
    
    for delta_x, delta_y in kernel:
        # Edge wrapping: wrap around the board edges
        wrapped_x = x + delta_x
        wrapped_y = y + delta_y
        neighbors += board[wrapped_x, wrapped_y]

    return neighbors

x_range = range(1, dim[0]-1)
y_range = range(1, dim[1]-1)

def update_board():
    global board  # must explain what global means

    temp = np.zeros(dim)
    for x in x_range:
        for y in y_range:
            cell = board[x, y]
            neighbors = count_neighbors(x, y)
            if neighbors in B and cell == 0:
                cell = 1
            elif neighbors in S and cell == 1:
                cell = 1
            elif cell ==1:
                cell = 0

            temp[x, y] = cell

    board[:] = temp  # Update the board with the new values

"""END LESSON PART"""

def fill_board_random(board):
    board[:, :] = np.random.choice([0, 1], size=board.shape)

def clear_board(board):
    board[:, :] = 0

def save_board():
    """Save the board to a user-specified file."""
    filename = 'bugs/' + input("Enter filename to save (e.g., board): ") + '.npy'
    np.save(filename, board)
    print(f"Board saved to {filename}")

def load_board():
    global board
    """Load the board from a user-specified file."""
    filename = 'bugs/' + input("Enter filename to load (e.g., board): ") + '.npy'
    if os.path.exists(filename):
        board = np.load(filename)
        print(f"Board loaded from {filename}")
    else:
        print(f"{filename} not found!")
        board = np.zeros(dim, dtype=int)

