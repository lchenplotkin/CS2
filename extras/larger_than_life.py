import pygame
import numpy as np
import os


# The part that we will write in class. WRITE HERE
kernel = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # EASY METHOD

def transform_kernel(kernel_array):
    # Get the center position of the kernel (in this case, the center is at (1, 1))
    center_x, center_y = kernel_array.shape[0] // 2, kernel_array.shape[1] // 2

    # Generate the relative offset tuples for the "1" values in the kernel
    kernel = [(i - center_x, j - center_y) 
                      for i in range(kernel_array.shape[0]) 
                      for j in range(kernel_array.shape[1]) 
                      if kernel_array[i, j] == 1]
    return kernel

# NICE METHOD
# Define the 2D array (kernel)
kernel_array = np.array([[1, 1, 1],
                         [1, 0, 1],
                         [1, 1, 1]])

kernel = transform_kernel(kernel_array)
fps = 10
dim = (100, 100)
board = np.zeros(dim, dtype=int)
S = [2, 3]
B = [3]
wrapping = False

#BOSCOS RULE:
kernel_array = np.ones((11,11), dtype = int)
kernel_array[5,5] = 0
kernel = transform_kernel(kernel_array)
S = range(34,59)
B = range(34,46)


def count_neighbors(x, y):
    neighbors = 0
    
    for delta_x, delta_y in kernel:
        # Edge wrapping: wrap around the board edges
        wrapped_x = (x + delta_x) % dim[0]
        wrapped_y = (y + delta_y) % dim[1]
        neighbors += board[wrapped_x, wrapped_y]

    return neighbors

if wrapping == False:
    x_range = range(1, dim[0]-1)
    y_range = range(1, dim[1]-1)
else:
    x_range = range(dim[0])
    y_range = range(dim[1])

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
            elif cell == 1:
                cell = 0

            temp[x, y] = cell

    board[:] = temp  # Update the board with the new values

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

# Fixed window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

# Derived cell size
CELL_WIDTH = WINDOW_WIDTH // dim[1]
CELL_HEIGHT = WINDOW_HEIGHT // dim[0]

# Colors
COLOR_BG = (30, 30, 30)
COLOR_ON = (200, 200, 200)
COLOR_OFF = (50, 50, 50)
COLOR_GRID = (40, 40, 40)

if 'fps' not in locals() and 'fps' not in globals():
    fps = 10

def draw_board(screen, board, show_gridlines):
    screen.fill(COLOR_BG)
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * CELL_WIDTH, y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
            color = COLOR_ON if board[y, x] else COLOR_OFF
            pygame.draw.rect(screen, color, rect)

    if show_gridlines:
        for x in range(0, WINDOW_WIDTH, CELL_WIDTH):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_HEIGHT):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Adaptive Board Viewer")
    clock = pygame.time.Clock()

    paused = True
    show_gridlines = True
    running = True

    while running:
        clock.tick(fps)  # Limit to 30 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_g:
                    show_gridlines = not show_gridlines
                elif event.key == pygame.K_c:
                    clear_board(board)
                elif event.key == pygame.K_r:
                    fill_board_random(board)
                elif event.key == pygame.K_s:
                    prompt_text = "enter filename to save (eg. mybug)"
                    save_board()  # Save board to user-specified filename
                elif event.key == pygame.K_l:
                    prompt_text = "enter filename to load (eg. mybug)"
                    load_board()  # Load board to user-specified filename

            elif paused and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                board_x = x // CELL_WIDTH
                board_y = y // CELL_HEIGHT
                if 0 <= board_x < dim[0] and 0 <= board_y < dim[1]:
                    board[board_y, board_x] = 1 - board[board_y, board_x]  # Toggle

        draw_board(screen, board, show_gridlines)

        if not paused:
            update_board()

    pygame.quit()

main()
