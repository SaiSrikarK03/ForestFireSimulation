import pygame
import random

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 10
EMPTY = 0
GRASS = 1
TREE = 2
BURNING = 3
BURNT = 4

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
BUTTON_COLOR = (0, 100, 0)
BUTTON_HOVER_COLOR = (0, 150, 0)
BUTTON_BORDER_COLOR = (0, 50, 0)
PAUSE_RESUME_COLOR = BLACK
PAUSE_RESUME_TEXT_COLOR = WHITE

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Forest Fire Simulation")

# Grid dimensions
rows = HEIGHT // CELL_SIZE
cols = WIDTH // CELL_SIZE

font = pygame.font.Font(None, 36)

# Burning time constants
BURNING_DURATION = 5  # Number of frames a tree burns before turning to empty

# Initialize burning times dictionary
burning_times = {}

# Function to create the initial grid
def create_grid():
    return [[GRASS for _ in range(cols)] for _ in range(rows)]

# Function to draw the grid
def draw_grid(grid):
    for y in range(rows):
        for x in range(cols):
            color = LIGHT_GREEN
            if grid[y][x] == TREE:
                color = DARK_GREEN
            elif grid[y][x] == BURNING:
                color = RED
            elif grid[y][x] == BURNT:
                color = BLACK
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw grid lines
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y))

# Function to update the grid
def update_grid(grid):
    global burning_times
    new_grid = [row[:] for row in grid]
    
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == BURNING:
                # Track burning time
                if (x, y) not in burning_times:
                    burning_times[(x, y)] = BURNING_DURATION
                else:
                    burning_times[(x, y)] -= 1
                    if burning_times[(x, y)] <= 0:
                        new_grid[y][x] = BURNT
                        del burning_times[(x, y)]
            elif grid[y][x] == TREE:
                if any(grid[ny][nx] == BURNING for nx, ny in get_neighbors(x, y)):
                    new_grid[y][x] = BURNING
            elif grid[y][x] == GRASS:
                if any(grid[ny][nx] == BURNING for nx, ny in get_neighbors(x, y)):
                    if random.random() < 0.1:  # Decrease probability of grass burning
                        new_grid[y][x] = BURNING

    return new_grid


# Function to get neighboring cells
def get_neighbors(x, y):
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            neighbors.append((nx, ny))
    return neighbors

# Function to draw the UI
def draw_ui(paused, random_button_rect, make_it_rain_button_rect, mouse_pos):
    if not ui_visible:  # Check if UI should be visible
        return
    
    # Draw pause/resume button
    pause_resume_rect = pygame.Rect(10, 10, 120, 50)
    pygame.draw.rect(screen, PAUSE_RESUME_COLOR, pause_resume_rect)
    pause_resume_surface = font.render("Pause" if not paused else "Resume", True, PAUSE_RESUME_TEXT_COLOR)
    text_rect = pause_resume_surface.get_rect(center=pause_resume_rect.center)
    screen.blit(pause_resume_surface, text_rect)

    # Draw random trees button
    button_color = BUTTON_HOVER_COLOR if random_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, random_button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, random_button_rect, 2)  # Border
    random_button_surface = font.render("Random Trees", True, WHITE)
    text_rect = random_button_surface.get_rect(center=random_button_rect.center)
    screen.blit(random_button_surface, text_rect)

    # Draw make it rain button
    button_color = BUTTON_HOVER_COLOR if make_it_rain_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, make_it_rain_button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, make_it_rain_button_rect, 2)  # Border
    make_it_rain_surface = font.render("Make It Rain", True, WHITE)
    text_rect = make_it_rain_surface.get_rect(center=make_it_rain_button_rect.center)
    screen.blit(make_it_rain_surface, text_rect)

# Function to place random trees
def place_random_trees(grid, density=0.1):
    for y in range(rows):
        for x in range(cols):
            if random.random() < density:
                grid[y][x] = TREE

# Function to make it rain
def make_it_rain(grid):
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == BURNT:
                grid[y][x] = GRASS

# Main function
def main():
    global ui_visible  # Declare as global to modify
    clock = pygame.time.Clock()
    grid = create_grid()
    running = True
    paused = False
    ui_visible = True  # UI starts as visible

    # Define the buttons
    random_button_rect = pygame.Rect(WIDTH - 200, 10, 180, 50)
    make_it_rain_button_rect = pygame.Rect(WIDTH - 200, 70, 180, 50)

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    grid = create_grid()
                    burning_times.clear()
                elif event.key == pygame.K_h:  # Toggle UI visibility
                    ui_visible = not ui_visible
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                if event.button == 1:  # Left click to plant a tree
                    if random_button_rect.collidepoint(event.pos):
                        place_random_trees(grid)
                    elif make_it_rain_button_rect.collidepoint(event.pos):
                        make_it_rain(grid)
                    else:
                        grid[grid_y][grid_x] = TREE
                elif event.button == 3:  # Right click to set fire
                    grid[grid_y][grid_x] = BURNING
                    burning_times[(grid_x, grid_y)] = BURNING_DURATION  # Start burning time

        if not paused:
            grid = update_grid(grid)

        screen.fill(LIGHT_GREEN)
        draw_grid(grid)
        draw_ui(paused, random_button_rect, make_it_rain_button_rect, mouse_pos)  # Draw UI based on visibility
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
