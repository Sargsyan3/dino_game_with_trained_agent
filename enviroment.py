import numpy as np
import gymnasium as gym
from gymnasium import spaces
import pygame
import random
import os



SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
DINO_WIDTH, DINO_HEIGHT = 40, 40
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40  # Default obstacle size
GROUND_HEIGHT = 300
FONT_SIZE = 24
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60
HIGH_SCORE_FILE = "high_score.txt"

# Colors for obstacles
OBSTACLE_COLORS = [RED, (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue obstacles

# Day/Night Cycle Colors
DAY_SKY_COLOR = (135, 206, 235)  # Light Blue for Day
NIGHT_SKY_COLOR = (10, 10, 50)   # Dark Blue for Night
GROUND_COLOR = (150, 75, 0)  # Ground color (brown)
STAR_COLOR = (255, 255, 255)  # White stars

class DinoGame(gym.Env):
    def __init__(self):
        super(DinoGame, self).__init__()

        # Action space (0: Do nothing, 1: Jump)
        self.action_space = spaces.Discrete(2)

        # Observation space: (dino_y, dino_velocity, obstacle_x, obstacle_type, obstacle_speed)
        # Added obstacle_speed in the state
        self.observation_space = spaces.Box(low=np.array([-1, -1, 0, 0, 0]),
                                            high=np.array([1, 1, 1, len(OBSTACLE_COLORS)-1, 1]),
                                            shape=(5,),  # Updated shape to include the speed
                                            dtype=np.float32)

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Google Dino Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)

        # Load images
        self.dino_image = pygame.Surface((DINO_WIDTH, DINO_HEIGHT))
        self.dino_image.fill(BLACK)

        self.obstacle_images = []
        for color in OBSTACLE_COLORS:
            surface = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
            surface.fill(color)
            self.obstacle_images.append(surface)

        # Initialize game state variables
        self.dino_y = GROUND_HEIGHT - DINO_HEIGHT
        self.dino_velocity = 0
        self.is_jumping = False
        self.obstacle_x = SCREEN_WIDTH
        self.obstacle_y = GROUND_HEIGHT - OBSTACLE_HEIGHT
        self.obstacle_speed = random.randint(5, 10)  # Random speed for obstacles
        self.obstacle_type = random.randint(0, len(OBSTACLE_COLORS)-1)  # Random obstacle type
        self.reward = 0
        self.score = 0
        self.time_of_day = 0  # Time of day (0 = day, 1 = night)
        self.star_positions = []  # List to store positions of stars during the night
        self.last_transition_time = pygame.time.get_ticks()  # Track time of last day/night transition

        # Load high score from file (if exists)
        self.high_score = self.load_high_score()

    def load_high_score(self):
        """ Loads the high score from a file """
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as file:
                return int(file.read().strip())
        return 0

    def save_high_score(self):
        """ Saves the high score to a file """
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(self.high_score))

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset game state
        self.dino_y = GROUND_HEIGHT - DINO_HEIGHT
        self.dino_velocity = 0
        self.is_jumping = False
        self.obstacle_x = SCREEN_WIDTH
        self.obstacle_y = GROUND_HEIGHT - OBSTACLE_HEIGHT
        self.obstacle_speed = random.randint(5, 10)
        self.obstacle_type = random.randint(0, len(OBSTACLE_COLORS)-1)
        self.reward = 0
        self.score = 0
        self.time_of_day = 0
        self.star_positions = []  # Clear star positions
        self.last_transition_time = pygame.time.get_ticks()  # Reset time for transition

        # Initial state: [normalized dino_y, normalized dino_velocity, normalized obstacle_x, obstacle_type, normalized obstacle_speed]
        # Added normalized obstacle_speed (scaled to max 1, since obstacle speed can vary between 5 and 10)
        self.state = np.array([self.dino_y / SCREEN_HEIGHT,
                               self.dino_velocity / 20,
                               self.obstacle_x / SCREEN_WIDTH,
                               self.obstacle_type,
                               self.obstacle_speed / 10], dtype=np.float32)

        return self.state, {}

    def step(self, action):
        """ Takes in the self (DinoGame environment) and an action (int) to take a step in the environment. """
        # Action handling: Jumping
        if action == 1 and not self.is_jumping:
            self.is_jumping = True
            self.dino_velocity = -15  # Negative velocity to move up

        # Handle jumping physics
        if self.is_jumping:
            self.dino_y += self.dino_velocity
            self.dino_velocity += 1  # Gravity effect

            if self.dino_y >= GROUND_HEIGHT - DINO_HEIGHT:
                self.dino_y = GROUND_HEIGHT - DINO_HEIGHT
                self.is_jumping = False

        # Update obstacle
        self.obstacle_x -= self.obstacle_speed
        if self.obstacle_x < 0:
            self.obstacle_x = SCREEN_WIDTH
            self.reward += 1  # Reward for avoiding the obstacle
            self.score += 1  # Increment score over time, simulating distance
            self.obstacle_speed = random.randint(5, 10)  # New random speed for next obstacle
            self.obstacle_type = random.randint(0, len(OBSTACLE_COLORS)-1)  # New random obstacle type

        # Check for collisions
        done = False
        # Check if the Dino and obstacle collide
        if (50 + DINO_WIDTH > self.obstacle_x and  # Dino's right side is beyond obstacle's left side
            50 < self.obstacle_x + OBSTACLE_WIDTH and  # Dino's left side is beyond obstacle's right side
            self.dino_y + DINO_HEIGHT > GROUND_HEIGHT - OBSTACLE_HEIGHT):  # Dino is below the obstacle
            done = True  # Collision occurs

        # Update high score if necessary
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

        # Update state and reward
        # Now include obstacle_speed in the state
        self.state = np.array([self.dino_y / SCREEN_HEIGHT,
                               self.dino_velocity / 20,
                               self.obstacle_x / SCREEN_WIDTH,
                               self.obstacle_type,
                               self.obstacle_speed / 10], dtype=np.float32)
        reward = 1 if not done else -100  # Negative reward for collision

        return self.state, reward, done, False, {}

    def render(self, mode="human"):
        # Get the current time and check if the day/night cycle should switch
        current_time = pygame.time.get_ticks()
        if current_time - self.last_transition_time > 10000:  # Every 10 seconds
            self.time_of_day = 1 - self.time_of_day  # Switch between day (0) and night (1)
            self.last_transition_time = current_time  # Update the last transition time

        # Switch between day and night
        if self.time_of_day == 0:  # Day
            self.screen.fill(DAY_SKY_COLOR)
        else:  # Night
            self.screen.fill(NIGHT_SKY_COLOR)

        # Draw stars at night
        if self.time_of_day == 1:
            self.draw_stars()

        # Draw ground line
        pygame.draw.line(self.screen, GROUND_COLOR, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)

        # Draw Dino (represented as a rectangle)
        self.screen.blit(self.dino_image, (50, self.dino_y))

        # Draw obstacle (use different types)
        self.screen.blit(self.obstacle_images[self.obstacle_type], (self.obstacle_x, self.obstacle_y))

        # Render score and high score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))

        # Update screen
        pygame.display.flip()
        self.clock.tick(FPS)

        return self.screen

    def draw_stars(self):
        """ Draw random stars in the night sky """
        if not self.star_positions:
            self.star_positions = [(random.randint(0, SCREEN_WIDTH), random.randint(0, GROUND_HEIGHT)) for _ in range(100)]

        for star in self.star_positions:
            pygame.draw.circle(self.screen, STAR_COLOR, star, 2)

    def close(self):
        pygame.quit()


# Register the environment
gym.envs.registration.register(
    id='Game-v0',
    entry_point='__main__:DinoGame'
)

if __name__ == "__main__":
    env = DinoGame()
    done = False
    obs, _ = env.reset()

    # Instructions
    print("Press SPACE to jump. Close the game window to exit.")

    while not done:
        env.render()
        action = 0  # Default action is doing nothing

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                action = 1  # Jump action

        # Apply action to environment
        obs, reward, done, truncated, info = env.step(action)
        print(f"Action: {action}, Reward: {reward}, Done: {done}")

    env.close()