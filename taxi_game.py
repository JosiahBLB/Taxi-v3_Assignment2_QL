import pygame
import random

# Game constants
WIN_COLS = 10
WIN_ROWS = 7
CELL_SIZE = 80
WINDOW_SIZE = (WIN_COLS * CELL_SIZE, WIN_ROWS * CELL_SIZE)
EMPTY = "-"
TAXI = "T"
PASSENGER = "P"
DROPOFF = "D"

# Obstacles
OB__T = "XT"  # Top
OB__B = "XB"  # Bottom
OB__L = "XL"  # Left
OB__R = "XR"  # Right
OB__H = "XH"  # Horizontal
OB__V = "XV"  # Vertical
OBSTACLES = [OB__T, OB__B, OB__L, OB__R, OB__H, OB__V]

# PICKUP & DROPOFF LOCATIONS
LOC_A = (1, 1)
LOC_B = (1, 8)
LOC_C = (5, 1)
LOC_D = (5, 8)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game variables
board: list[list]
taxi_x: int
taxi_y: int
passenger_x: int
passenger_y: int
dropoff_x: int
dropoff_y: int

def new_game():
    global board, taxi_x, taxi_y, passenger_x, passenger_y, dropoff_x, dropoff_y

    # Initialize game board
    board = [
        [EMPTY, OB__L, OB__H, OB__H, OB__H, OB__H, OB__H, OB__H, OB__R, EMPTY],
        [OB__T, EMPTY, EMPTY, OB__T, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OB__T],
        [OB__V, EMPTY, EMPTY, OB__B, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OB__V],
        [OB__V, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, OB__V],
        [OB__V, EMPTY, OB__T, EMPTY, EMPTY, EMPTY, EMPTY, OB__T, EMPTY, OB__V],
        [OB__B, EMPTY, OB__B, EMPTY, EMPTY, EMPTY, EMPTY, OB__B, EMPTY, OB__B],
        [EMPTY, OB__L, OB__H, OB__H, OB__H, OB__H, OB__H, OB__H, OB__R, EMPTY],
    ]

    # Set taxi to random position
    taxi_x, taxi_y = random.randint(1, WIN_ROWS - 2), random.randint(1, WIN_COLS - 2)
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

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Taxi Game")

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
obstacle_image_hoz = pygame.image.load("img/gridworld_median_horiz.png")
obstacle_image_left = pygame.image.load("img/gridworld_median_left.png")
obstacle_image_right = pygame.image.load("img/gridworld_median_right.png")

# Resize sprites to fit cell size
for direction in taxi_images:
    taxi_images[direction] = pygame.transform.scale(
        taxi_images[direction], (CELL_SIZE, CELL_SIZE)
    )
passenger_image = pygame.transform.scale(passenger_image, (CELL_SIZE, CELL_SIZE))
dropoff_image = pygame.transform.scale(dropoff_image, (CELL_SIZE, CELL_SIZE))
obstacle_image_vert = pygame.transform.scale(
    obstacle_image_vert, (CELL_SIZE, CELL_SIZE)
)
obstacle_image_top = pygame.transform.scale(obstacle_image_top, (CELL_SIZE, CELL_SIZE))
obstacle_image_bot = pygame.transform.scale(obstacle_image_bot, (CELL_SIZE, CELL_SIZE))
obstacle_image_hoz = pygame.transform.scale(obstacle_image_hoz, (CELL_SIZE, CELL_SIZE))
obstacle_image_left = pygame.transform.scale(
    obstacle_image_left, (CELL_SIZE, CELL_SIZE)
)
obstacle_image_right = pygame.transform.scale(
    obstacle_image_right, (CELL_SIZE, CELL_SIZE)
)
background_tile = pygame.transform.scale(background_tile, (CELL_SIZE, CELL_SIZE))

clock = pygame.time.Clock()
score = 0
has_passenger = False

# Game loop
running = True
reset = True
while running:
    if reset:
        new_game()
        reset = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Get user input for taxi movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and taxi_x > 0:
                if board[taxi_x - 1][taxi_y] not in OBSTACLES:
                    board[taxi_x][taxi_y] = EMPTY
                    taxi_x -= 1
                    direction = "up"
            elif event.key == pygame.K_DOWN and taxi_x < WIN_ROWS - 1:
                if board[taxi_x + 1][taxi_y] not in OBSTACLES:
                    board[taxi_x][taxi_y] = EMPTY
                    taxi_x += 1
                    direction = "down"
            elif event.key == pygame.K_LEFT and taxi_y > 0:
                if board[taxi_x][taxi_y - 1] not in OBSTACLES:
                    board[taxi_x][taxi_y] = EMPTY
                    taxi_y -= 1
                    direction = "left"
            elif event.key == pygame.K_RIGHT and taxi_y < WIN_COLS - 1:
                if board[taxi_x][taxi_y + 1] not in OBSTACLES:
                    board[taxi_x][taxi_y] = EMPTY
                    taxi_y += 1
                    direction = "right"
            board[dropoff_x][dropoff_y] = DROPOFF

    # Check if passenger has been dropped off
    if (taxi_x, taxi_y) == (dropoff_x, dropoff_y) and has_passenger:
        print("Passenger dropped off! You win!")
        reset = True
        score += 1

    # Check if taxi picked up the passenger
    if (taxi_x, taxi_y) == (passenger_x, passenger_y):
        board[passenger_x][passenger_y] = EMPTY
        has_passenger = True
        print("Passenger picked up! Head to the drop-off location.")

    # Update taxi location on the board
    board[taxi_x][taxi_y] = TAXI

    # Clear the window
    window.fill(WHITE)

    # Draw the background tiles
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            cell_rect = pygame.Rect(
                col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            window.blit(background_tile, cell_rect)

    # Draw the obstacles
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            if board[row][col] in OBSTACLES:
                cell_rect = pygame.Rect(
                    col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                if board[row][col] == OB__B:
                    window.blit(obstacle_image_bot, cell_rect)
                if board[row][col] == OB__T:
                    window.blit(obstacle_image_top, cell_rect)
                if board[row][col] == OB__L:
                    window.blit(obstacle_image_left, cell_rect)
                if board[row][col] == OB__R:
                    window.blit(obstacle_image_right, cell_rect)
                if board[row][col] == OB__H:
                    window.blit(obstacle_image_hoz, cell_rect)
                if board[row][col] == OB__V:
                    window.blit(obstacle_image_vert, cell_rect)

    # Draw the game board
    for row in range(WIN_ROWS):
        for col in range(WIN_COLS):
            cell_rect = pygame.Rect(
                col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
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
