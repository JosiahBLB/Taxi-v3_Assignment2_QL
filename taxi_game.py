import copy
import pygame
import random
import numpy as np


# Game constants
WIN_COLS = 10
WIN_ROWS = 7
CELL_SIZE = 80
WINDOW_SIZE = (WIN_COLS * CELL_SIZE, WIN_ROWS * CELL_SIZE)
EMPTY = "-"
TAXI = "T"
PASSENGER = "P"
DROPOFF = "D"

# Q-learning constants
NUM_ACTIONS = 6
NUM_EPISODES = 1000
MAX_STEPS = 100
ALPHA = 0.5
GAMMA = 0.99
EPSILON = 0.01

Q = np.zeros((WIN_ROWS, WIN_COLS, NUM_ACTIONS))

# Obstacles
OB__T = "XT"  # Top
OB__B = "XB"  # Bottom
OB__L = "XL"  # Left
OB__R = "XR"  # Right
OB__H = "XH"  # Horizontal
OB__V = "XV"  # Vertical
OBSTACLES = [OB__T, OB__B, OB__L, OB__R, OB__H, OB__V]

# Pickup and dropoff locations
LOC_A = (1, 1)
LOC_B = (1, 8)
LOC_C = (5, 1)
LOC_D = (5, 8)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Game variables
board: list[list]
taxi_x: int
taxi_y: int
passenger_x: int
passenger_y: int
dropoff_x: int
dropoff_y: int
has_passenger: bool


def new_game():
    global board, taxi_x, taxi_y, passenger_x, passenger_y, dropoff_x, dropoff_y, has_passenger

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
    while board[taxi_x][taxi_y] in OBSTACLES:
        taxi_x, taxi_y = random.randint(1, WIN_ROWS - 2), random.randint(
            1, WIN_COLS - 2
        )
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

    has_passenger = False


# Initialize Pygame
pygame.init()
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Taxi Game")

# Define font properties
font_size = 40
font = pygame.font.Font(None, font_size)

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


# Game loop
clock = pygame.time.Clock()
score = 0
running = True
reset = True
while running:
    # Resets the board to a randomized layout
    if reset:
        new_game()
        reset = False

    # A way for the user to exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Updating the Q-table
    for episode in range(NUM_EPISODES):
        has_passenger_q = False
        state = (copy.copy(taxi_x), copy.copy(taxi_y))
        total_reward = 0
        for step in range(MAX_STEPS):
            # Updates current status of passenger
            if has_passenger:
                has_passenger_q = True

            # Choose an optimised choice or random choice based on ϵ
            if random.uniform(0, 1) < EPSILON:
                action = random.choice(range(4))
            else:
                action = np.argmax(Q[state])

            # Taxi movement
            if action == 0 and board[state[0] - 1][state[1]] not in OBSTACLES:
                new_state = (state[0] - 1, state[1])
            elif action == 1 and board[state[0] + 1][state[1]] not in OBSTACLES:
                new_state = (state[0] + 1, state[1])
            elif action == 2 and board[state[0]][state[1] - 1] not in OBSTACLES:
                new_state = (state[0], state[1] - 1)
            elif action == 3 and board[state[0]][state[1] + 1] not in OBSTACLES:
                new_state = (state[0], state[1] + 1)
            else:
                new_state = state

            reward = 0

            # Check if passenger has been dropped off
            if new_state == (dropoff_x, dropoff_y) and has_passenger_q:
                reward += 100

            # Check if taxi picked up the passenger
            elif new_state == (passenger_x, passenger_y) and not has_passenger_q:
                has_passenger_q = True
                reward += 10

            # Minus one for playing a move
            else:
                reward -= 1

            max_future_reward = max(Q[new_state])

            # Update Q-learning table
            Q[state][action] = Q[state][action] + ALPHA * (
                reward + GAMMA * max_future_reward - Q[state][action]
            )

            total_reward += reward
            state = new_state

            # Break at found solution
            if state == (dropoff_x, dropoff_y) and has_passenger_q:
                break

    # Pick the best action from current state
    action = np.argmax(Q[taxi_x][taxi_y])

    # Taxi movement
    if action == 0 and board[taxi_x - 1][taxi_y] not in OBSTACLES:
        board[taxi_x][taxi_y] = EMPTY
        taxi_x -= 1
        direction = "up"
    elif action == 1 and board[taxi_x + 1][taxi_y] not in OBSTACLES:
        board[taxi_x][taxi_y] = EMPTY
        taxi_x += 1
        direction = "down"
    elif action == 2 and board[taxi_x][taxi_y - 1] not in OBSTACLES:
        board[taxi_x][taxi_y] = EMPTY
        taxi_y -= 1
        direction = "left"
    elif action == 3 and board[taxi_x][taxi_y + 1] not in OBSTACLES:
        board[taxi_x][taxi_y] = EMPTY
        taxi_y += 1
        direction = "right"

    # Check Objectives
    if (taxi_x, taxi_y) == (dropoff_x, dropoff_y) and has_passenger:
        reset = True
        score += 1
    elif (taxi_x, taxi_y) == (passenger_x, passenger_y) and not has_passenger:
        board[passenger_x][passenger_y] = EMPTY
        has_passenger = True

    # Update taxi and dropoff location on the board
    board[dropoff_x][dropoff_y] = DROPOFF
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
            if board[row][col] == DROPOFF:
                window.blit(dropoff_image, cell_rect)
            if board[row][col] == PASSENGER:
                window.blit(passenger_image, cell_rect)
            if board[row][col] == TAXI:
                window.blit(taxi_images[direction], cell_rect)

    # Render the score text
    score_text = font.render("Score: " + str(score), True, WHITE, BLACK)
    reward_text = font.render("Reward: " + str(total_reward), True, RED, BLACK)
    window.blit(reward_text, (WIN_COLS * CELL_SIZE - 200, 10))

    # Blit the score text onto the window surface
    window.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Game over!")
