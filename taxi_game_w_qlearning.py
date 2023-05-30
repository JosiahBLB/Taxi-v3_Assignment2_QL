"""
Taxi game solved with Q-Learning.

Authors: Josiah, Luke and Kisoon
"""

import copy
import time
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
NUM_EPISODES = 300
MAX_STEPS = 140
ALPHA = 0.3  # Learning rate
GAMMA = 0.99  # Discount factor
EPSILON_INITIAL = 0.05  # Exploration rate
EPSILON_FINAL = 0.01

# Initialze Q-table
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
pickup: bool
dropoff: bool
taxi_x, taxi_y = (3, 4)


# A function that re-initializes the game into a random starting state
def new_game():
    global board, passenger_x, passenger_y, dropoff_x, dropoff_y, has_passenger, pickup, dropoff

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

    # initalize without passenger
    has_passenger = False
    pickup = False
    dropoff = False


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
display_reward = 0

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
        q_has_passenger = False
        q_pickup = False
        q_dropoff = False
        q_passenger_pos = (copy.copy(passenger_x), copy.copy(passenger_y))
        state = (copy.copy(taxi_x), copy.copy(taxi_y))
        new_state = state

        # Calculate epsilon for the current episode
        epsilon = max(
            EPSILON_FINAL,
            EPSILON_INITIAL
            - (episode / NUM_EPISODES) * (EPSILON_INITIAL - EPSILON_FINAL),
        )

        for step in range(MAX_STEPS):
            # Updates current status of passenger
            if has_passenger:
                q_has_passenger = True

            # Choose an optimised choice or random choice based on ϵ
            if random.uniform(0, 1) < epsilon:
                action = random.choice(range(NUM_ACTIONS))
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
            elif action == 4:
                q_pickup = True
            elif action == 5:
                q_dropoff = True

            reward = 0

            # Check if passenger has been dropped off at the correct location
            if new_state == (dropoff_x, dropoff_y) and q_has_passenger and q_dropoff:
                q_dropoff = False
                reward += 20

            # Check if the taxi has picked up the passenger
            elif q_pickup and not q_has_passenger and new_state == q_passenger_pos:
                q_pickup = False
                q_has_passenger = True
                reward += 2

            # Check if passenger has been dropped off at the wrong location
            elif q_dropoff and q_has_passenger and new_state != (dropoff_x, dropoff_y):
                q_passenger_pos = new_state
                q_has_passenger = False
                q_dropoff = False
                reward -= 10

            # Check if the pickup or dropoff chosen with no passenger
            elif (
                q_dropoff
                and not q_has_passenger
                or q_pickup
                and new_state != q_passenger_pos
            ):
                q_pickup = False
                q_dropoff = False
                reward -= 10

            # Minus one for playing a move
            else:
                reward -= 1

            # Update Q-learning table
            max_future_reward = max(Q[new_state])
            Q[state][action] = Q[state][action] + ALPHA * (
                reward + GAMMA * max_future_reward - Q[state][action]
            )

            state = new_state

            # Break at found solution
            if state == (dropoff_x, dropoff_y) and q_has_passenger:
                break

    # Pick the best action from current state
    action = np.argmax(Q[taxi_x][taxi_y])

    print(action)

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
    elif action == 4:
        pickup = True
    elif action == 5:
        dropoff = True

    # Check if passenger has been dropped off at the correct location
    if (taxi_x, taxi_y) == (dropoff_x, dropoff_y) and has_passenger and dropoff:
        dropoff = False
        reset = True
        score += 1
        display_reward += 20

    # Check if the taxi has picked up the passenger
    elif (
        pickup and not has_passenger and (taxi_x, taxi_y) == (passenger_x, passenger_y)
    ):
        board[passenger_x][passenger_y] = EMPTY
        pickup = False
        has_passenger = True
        display_reward += 5

    # Check if passenger has been dropped off at the wrong location
    elif dropoff and has_passenger and (taxi_x, taxi_y) != (dropoff_x, dropoff_y):
        (passenger_x, passenger_y) = (taxi_x, taxi_y)
        has_passenger = False
        dropoff = False
        display_reward -= 10

    # Check if the pickup or dropoff chosen with no passenger
    elif (
        dropoff
        and not has_passenger
        or pickup
        and (taxi_x, taxi_y) != (passenger_x, passenger_y)
    ):
        pickup = False
        dropoff = False
        display_reward -= 10

    else:
        display_reward -= 1

    # Update sprites on the board
    board[dropoff_x][dropoff_y] = DROPOFF
    board[taxi_x][taxi_y] = TAXI
    if not has_passenger and (passenger_x, passenger_y) != (taxi_x, taxi_y):
        board[passenger_x][passenger_y] = PASSENGER

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
    reward_text = font.render("Reward: " + str(display_reward), True, RED, BLACK)
    window.blit(reward_text, (WIN_COLS * CELL_SIZE - 200, 10))

    # Render the score text onto the window surface
    window.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()
    clock.tick(60)

    # Allows user to see each taxi movement
    time.sleep(0.01)

pygame.quit()
