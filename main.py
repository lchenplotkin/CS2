from lesson import *
import pygame
import numpy as np
import os
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
    global board
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
                    board = load_board()  # Load board to user-specified filename

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

if __name__ == "__main__":
    main()
