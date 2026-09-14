# Flappy Bird

A small Flappy Bird-style game written in Python with Pygame.

## Requirements

- Python 3
- Pygame

## Installation

Install Pygame with pip:

```bash
python -m pip install pygame
```

## Running the game

From the project directory, run:

```bash
python main_game.py
```

The game loads its window size from `assets/background-day.png`. Keep the `assets` directory next to `flappy_bird.py` so the game can find the images it needs.

## Controls

| Action | Keyboard or mouse |
| --- | --- |
| Start the game | Space, Up Arrow, or left mouse button |
| Flap | Space, Up Arrow, or left mouse button |
| Restart after a crash | Space, Up Arrow, left mouse button, or `R` |
| Quit | Escape or close the game window |

## How to play

Guide the bird through the gaps between the pipes. The score increases each time the bird passes a pipe. The game ends when the bird touches a pipe, the ground, or the top of the screen.

## Project structure

```text
Flappy Bird/
├── main_game.py
├── assets/
│   ├── background-day.png
│   ├── base.png
│   ├── pipe-green.png
│   ├── redbird-downflap.png
│   ├── redbird-midflap.png
│   ├── redbird-upflap.png
│   ├── message.png
│   ├── gameover.png
│   └── 0.png to 9.png
└── README.md
```

## Notes

The game checks for all required assets when it starts. If an image is missing, it prints the missing filename and the expected asset directory before exiting.
