# Dino Game with Day/Night Cycle & Obstacle Variations

This repository contains an implementation of the Google Dino Game using Pygame and the Gymnasium (formerly Gym) environment. The game simulates the classic Dino game where the player must jump over obstacles, but with enhanced features such as a dynamic day/night cycle, obstacle color variations, and high score tracking.

The environment is structured for use in reinforcement learning (RL) setups, making it easy to integrate RL algorithms.

Key Features
1. Day/Night Cycle
The game has a dynamic day/night cycle that switches every 10 seconds.
During the day, the background is a light blue sky.
During the night, the background is dark blue, and stars are displayed.
2. Obstacle Variations
Obstacles come in different colors (Red, Green, Blue).
Each obstacle has a random color assigned when it spawns, adding visual variety.
3. Jumping Mechanics
The Dino can jump by pressing the spacebar.
A simple gravity system is implemented, where the Dino jumps upward and is pulled back down to the ground.
4. Reward System
+1 reward for avoiding obstacles and for each new obstacle that passes.
-100 penalty for collisions, which ends the game.
The score increases as the Dino survives longer and avoids more obstacles.
5. High Score Tracking
The high score is tracked and saved to a file (high_score.txt) between game sessions.
The high score is displayed during gameplay.
6. Gymnasium Environment
The game is wrapped into a custom Gymnasium environment for use in reinforcement learning experiments.
The state includes:
Dino’s Y position and velocity.
Obstacle's X position, type, and speed.
The action space is discrete, with two actions: Do Nothing (0) and Jump (1).
Requirements

To run this game, you'll need the following Python packages:

gymnasium
pygame
numpy

Modifications & Improvements
Day/Night Cycle
Introduced a dynamic day/night cycle with smooth transitions every 10 seconds.
The background color changes between light blue for the day and dark blue for the night.
Stars are drawn during the night for an added visual effect.
Obstacle Variations
Obstacles now have different colors (Red, Green, Blue) that are randomly assigned when they spawn.
This variation adds more visual interest to the game.
Reward System
Added a custom reward structure where:
The player earns a reward for avoiding obstacles (+1).
The player gets penalized for collisions (-100).
High Score
The high score is saved to a file (high_score.txt) and is displayed on the screen during gameplay.
If a new high score is achieved, it gets saved to the file.
![ScreenRecording2025-01-17at9 00 23PM-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/0a7fe458-afc1-4091-8d05-62541ff8f58b)
