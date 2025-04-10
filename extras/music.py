import pygame
import numpy as np
import os
import math

# Initialize pygame mixer for sound
pygame.mixer.init(frequency=22050)  # Set frequency to a standard value

# EASY METHOD
kernel = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

dim = (50, 50)
board = np.zeros(dim, dtype=int)
S = [2, 3]
B = [3]

def count_neighbors(x, y):
    neighbors = 0
    for delta_x, delta_y in kernel:
        # Edge wrapping: wrap around the board edges
        wrapped_x = (x + delta_x) % dim[0]
        wrapped_y = (y + delta_y) % dim[1]
        neighbors += board[wrapped_x, wrapped_y]
    return neighbors

x_range = range(1, dim[0]-1)
y_range = range(1, dim[1]-1)

# Function to generate a tone based on the frequency
def generate_tone(frequency, duration=0.1, sample_rate=22050):
    """Generates a sine wave tone based on the given frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.sin(2 * np.pi * frequency * t) * 32767  # Generate sine wave
    waveform = waveform.astype(np.int16)  # Convert to 16-bit PCM format
    
    # Convert to stereo by duplicating the waveform for the second channel
    stereo_waveform = np.stack((waveform, waveform), axis=-1)  # Create a 2D array
    
    return pygame.sndarray.make_sound(stereo_waveform)

def update_board():
    global board  # must explain what global means

    temp = np.zeros(dim)
    births = 0
    deaths = 0

    for x in x_range:
        for y in y_range:
            cell = board[x, y]
            neighbors = count_neighbors(x, y)
            if neighbors in B and cell == 0:
                # Birth: cell becomes alive
                temp[x, y] = 1
                births += 1
            elif neighbors in S and cell == 1:
                # Survival: cell stays alive
                temp[x, y] = 1
            else:
                # Death: cell becomes dead
                if cell == 1:  # Only count death if the cell was alive
                    deaths += 1
                    temp[x, y] = 0

    board[:] = temp  # Update the board with the new values

    # If no changes (no births or deaths), don't play any tone
    if births == 0 and deaths == 0:
        return

    # Calculate the frequency for the tone based on the number of births and deaths
    if deaths !=0:
        delta = births/deaths
    else:
        delta = 0

    print(delta)
    base_frequency = 220# Frequency of A4 note (440 Hz) as the base
    frequency = base_frequency ** delta# Modify frequency based on the difference

    # Ensure the frequency stays within a comfortable range
    frequency = max(100, min(frequency, 800))  # Limit frequency to a range between 100Hz and 800Hz

    # Add smoothing to avoid abrupt changes in frequency
    if hasattr(update_board, 'last_frequency'):
        frequency = 0.8 * update_board.last_frequency + 0.2 * frequency  # Smooth the frequency transition
    update_board.last_frequency = frequency

    # Generate and play the tone continuously
    tone = generate_tone(frequency)
    tone.play(maxtime=0)  # Play the tone without stopping, maxtime=0 means it won't stop automatically

def fill_board_random(board):
    board[:, :] = np.random.choice([0, 1], size=board.shape)

def clear_board(board):
    board[:, :] = 0
def save_board():
    """Save the board to a user-specified file."""
    filename = input("Enter filename to save (e.g., board): ") + '.npy'
    np.save(filename, board)
    print(f"Board saved to {filename}")

def load_board():
    global board
    """Load the board from a user-specified file."""
    filename = input("Enter filename to load (e.g., board): ") + '.npy'
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
    fps = 5

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

