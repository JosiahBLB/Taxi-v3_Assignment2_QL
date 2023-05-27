import pygame
import random

# Game constants
WIN_COLS = 10
WIN_ROWS = 6
CELL_SIZE = 80
WINDOW_SIZE = (WIN_COLS * CELL_SIZE, WIN_ROWS * CELL_SIZE)
EMPTY = "-"
TAXI = "T"
PASSENGER = "P"
DROPOFF = "D"
OBSTACLE = "X"

# PICKUP & DROPOFF LOCATIONS
LOC_A = (1,1)
LOC_B = (1,8)
LOC_C = (5,1)
LOC_D = (5,8)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Taxi Game")

# Load custom sprites
# Load custom sprites
taxi_images = {
    "up": pygame.image.load("img/cab_rear.png"),
    "down": pygame.image.load("img/cab_front.png"),
    "left": pygame.image.load("img/cab_left.png"),
    "right": pygame.image.load("img/cab_right.png"),
}
passenger_image = pygame.image.load("img/passenger.png")
dropoff_image = pygame.image.load("img/hotel.png")
background_tile = pygame.image.load("img/taxi_background.png")
obstacle_image_vert = pygame.image.load("img/gridworld_median_vert.png")
obstacle_image_top = pygame.image.load("img/gridworld_median_top.png")
obstacle_image_bot = pygame.image.load("img/gridworld_median_bottom.png")

# Resize sprites to fit cell size
for direction in taxi_images:
    taxi_images[direction] = pygame.transform.scale(taxi_images[direction], (CELL_SIZE, CELL_SIZE))
passenger_image = pygame.transform.scale(passenger_image, (CELL_SIZE, CELL_SIZE))
dropoff_image = pygame.transform.scale(dropoff_image, (CELL_SIZE, CELL_SIZE))
obstacle_image_vert = pygame.transform.scale(obstacle_image_vert, (CELL_SIZE, CELL_SIZE))
obstacle_image_top = pygame.transform.scale(obstacle_image_top, (CELL_SIZE, CELL_SIZE))
obstacle_image_bot = pygame.transform.scale(obstacle_image_bot, (CELL_SIZE, CELL_SIZE))
background_tile = pygame.transform.scale(background_tile, (CELL_SIZE, CELL_SIZE))

# Initialize game board
board = [[EMPTY for _ in range(WIN_COLS)] for _ in range(WIN_ROWS)]

# Set taxi to random position
taxi_x, taxi_y = random.randint(0, WIN_ROWS-1), random.randint(0, WIN_COLS-1)
board[taxi_x][taxi_y] = TAXI

# Generate random passenger locations 
locations = [LOC_A, LOC_B, LOC_C, LOC_D]
passenger_x, passenger_y = locations[random.randint(0, 3)]

# Generate random drop-off locations
dropoff_x, dropoff_y = locations[random.randint(0, 3)]
while (passenger_x, passenger_y) == (dropoff_x, dropoff_y):
    dropoff_x, dropoff_y = locations[random.randint(0, 3)]

# Save Locations
board[passenger_x][passenger_y] = PASSENGER
board[dropoff_x][dropoff_y] = DROPOFF

# Generate obstacle positions
obstacle_locations = []
for row in range(WIN_ROWS):
    for col in range(WIN_COLS):
        # Top boundary
        if row == 0 and col in range(1,9):
            obstacle_locations.append((row, col))
        # Bottom boundary
        if row == 6 and col in range(1,9):
            obstacle_locations.append((row, col))
for location in obstacle_locations:
    obstacle_x, obstacle_y = location
    board[obstacle_x][obstacle_y] = OBSTACLE


clock = pygame.time.Clock()
score = 0
has_passenger = False

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Get user input for taxi movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and taxi_x > 0:
                board[taxi_x][taxi_y] = EMPTY
                taxi_x -= 1
                direction = "up"
            elif event.key == pygame.K_DOWN and taxi_x < WIN_ROWS - 1:
                board[taxi_x][taxi_y] = EMPTY
                taxi_x += 1
                direction = "down"
            elif event.key == pygame.K_LEFT and taxi_y > 0:
                board[taxi_x][taxi_y] = EMPTY
                taxi_y -= 1
                direction = "left"
            elif event.key == pygame.K_RIGHT and taxi_y < WIN_COLS - 1:
                board[taxi_x][taxi_y] = EMPTY
                taxi_y += 1
                direction = "right"
            board[dropoff_x][dropoff_y] = DROPOFF

    # Check if passenger has been dropped off
    if (taxi_x, taxi_y) == (dropoff_x, dropoff_y) and has_passenger:
        print("Passenger dropped off! You win!")
        running = False

    # Check if taxi picked up the passenger
    if (taxi_x, taxi_y) == (passenger_x, passenger_y):
        board[passenger_x][passenger_y] = EMPTY
        score += 1
        has_passenger = True
        print("Passenger picked up! Head to the drop-off location.")

    # Update taxi location on the board
    board[taxi_x][taxi_y] = TAXI

    # Clear the window
    window.fill(WHITE)

    # Draw the background tiles
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            cell_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            window.blit(background_tile, cell_rect)

    # Draw the obstacles
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            if board[row][col] == OBSTACLE:
                cell_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if(row, col) == locations[1] or (row, col) == locations[3]:
                    window.blit(obstacle_image_top, cell_rect)
                elif(row, col) == locations[0]:
                    window.blit(obstacle_image_bot, cell_rect)
                else:
                    window.blit(obstacle_image_vert, cell_rect)

    # Draw the game board
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            cell_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[row][col] == TAXI:
                window.blit(taxi_images[direction], cell_rect)
            elif board[row][col] == PASSENGER:
                window.blit(passenger_image, cell_rect)
            elif board[row][col] == DROPOFF:
                window.blit(dropoff_image, cell_rect)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Game over!")
