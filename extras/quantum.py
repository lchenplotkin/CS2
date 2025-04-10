import pygame
import numpy as np
import os
import random
from scipy.stats import norm

# Precompute normal distribution probabilities for 0-8 neighbors
def precompute_probabilities(sigma_birth, sigma_survival_2, sigma_survival_3, threshold_birth=3, threshold_survival_2=2, threshold_survival_3=3):
    prob_table = {}
    # Birth probability distribution centered at threshold_birth
    for neighbors in range(9):  # 0 to 8 neighbors
        prob_table[neighbors] = {
            'birth': norm.pdf(neighbors, threshold_birth, sigma_birth),
            'survival_2': norm.pdf(neighbors, threshold_survival_2, sigma_survival_2),
            'survival_3': norm.pdf(neighbors, threshold_survival_3, sigma_survival_3)
        }
    return prob_table

# Kernel for counting neighbors
kernel = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def transform_kernel(kernel_array):
    center_x, center_y = kernel_array.shape[0] // 2, kernel_array.shape[1] // 2
    return [(i - center_x, j - center_y) 
            for i in range(kernel_array.shape[0]) 
            for j in range(kernel_array.shape[1]) 
            if kernel_array[i, j] == 1]

# Traditional Game of Life rules
S = [2, 3]  # Survival: cells with 2 or 3 neighbors stay alive
B = [3]      # Birth: cells with exactly 3 neighbors become alive

# Quantum probability function with bimodal survival
def quantum_probability(cell_value, neighbors, is_birth, prob_table):
    """ Use precomputed probabilities for faster performance. """
    if is_birth:  # For dead cells trying to become alive (exactly 3 neighbors)
        prob = prob_table.get(neighbors, {}).get('birth', 0)
    else:  # For live cells trying to survive (bimodal for 2 or 3 neighbors)
        if neighbors == 2:
            prob = prob_table.get(neighbors, {}).get('survival_2', 0)
        elif neighbors == 3:
            prob = prob_table.get(neighbors, {}).get('survival_3', 0)
        else:
            prob = 0  # If neighbors are neither 2 nor 3, survival is impossible
    
    # Normalize to make sure the probability is between 0 and 1
    prob = max(0, min(prob, 1))
    return prob

# Count the neighbors of a cell at (x, y)
def count_neighbors(x, y):
    neighbors = 0
    for dx, dy in kernel:
        nx = (x + dx) % dim[0]
        ny = (y + dy) % dim[1]
        if board[nx, ny] == 1:
            neighbors += 1
    return neighbors

# Parameters
fps = 10
dim = (100, 100)
board = np.zeros(dim, dtype=int)
wrapping = False
sigma_birth = 0.34  # Spread for birth probability (centered at 3)
sigma_survival_2 = 0.34  # Spread for survival with 2 neighbors
sigma_survival_3 = 0.34  # Spread for survival with 3 neighbors

# Precompute probability tables once
prob_table = precompute_probabilities(sigma_birth, sigma_survival_2, sigma_survival_3)

def update_board():
    global board
    temp = np.zeros(dim, dtype=int)
    
    for x in range(1, dim[0]-1):
        for y in range(1, dim[1]-1):
            cell = board[x, y]
            neighbors = count_neighbors(x, y)

            if cell == 0:  # Dead cell
                # Birth condition with quantum probability
                prob = quantum_probability(cell, neighbors, is_birth=True, prob_table=prob_table)
                if random.random() < prob:
                    temp[x, y] = 1
            elif cell == 1:  # Alive cell
                # Survival condition with quantum probability
                prob = quantum_probability(cell, neighbors, is_birth=False, prob_table=prob_table)
                if random.random() < prob:
                    temp[x, y] = 1
                else:
                    temp[x, y] = 0

    board[:] = temp

def fill_board_random(board):
    board[:, :] = np.random.choice([0, 1], size=board.shape)

def clear_board(board):
    board[:, :] = 0

def save_board():
    filename = 'bugs/' + input("Enter filename to save (e.g., board): ") + '.npy'
    np.save(filename, board)
    print(f"Board saved to {filename}")

def load_board():
    global board
    filename = 'bugs/' + input("Enter filename to load (e.g., board): ") + '.npy'
    if os.path.exists(filename):
        board = np.load(filename)
        print(f"Board loaded from {filename}")
    else:
        print(f"{filename} not found!")
        board = np.zeros(dim, dtype=int)

# Fixed window size for visualization
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
CELL_WIDTH = WINDOW_WIDTH // dim[1]
CELL_HEIGHT = WINDOW_HEIGHT // dim[0]
COLOR_BG = (30, 30, 30)
COLOR_ON = (200, 200, 200)
COLOR_OFF = (50, 50, 50)
COLOR_GRID = (40, 40, 40)

def draw_board(screen, board, show_gridlines):
    screen.fill(COLOR_BG)
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * CELL_WIDTH, y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
            if board[y, x] == 1:
                color = COLOR_ON
            else:
                color = COLOR_OFF
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
    pygame.display.set_caption("Quantum Game of Life")
    clock = pygame.time.Clock()

    paused = True
    show_gridlines = True
    running = True

    while running:
        clock.tick(fps)
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
                    save_board()
                elif event.key == pygame.K_l:
                    load_board()

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

