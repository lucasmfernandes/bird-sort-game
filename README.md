# Bird Sort Game

A puzzle game where you sort birds of the same color onto branches.

## Description

Bird Sort is a puzzle game where you have a number of branches, each containing birds of different colors. The goal is to sort the birds so that all birds of the same color are on the same branch. Each branch can hold up to 4 birds, and each color has exactly 4 birds.

## Features

- Random game generation with configurable number of branches and colors
- Drag-and-drop bird movement
- Undo functionality
- Auto-solver using A* search algorithm
- Hint system

## Installation

1. Clone the repository:
git clone [https://github.com/yourusername/bird-sort.git](https://github.com/yourusername/bird-sort.git)
cd bird-sort

2. Install the required dependencies:
pip install -r requirements.txt

3. Run the game:
python main.py

## Command Line Options

- `--branches N`: Set the number of branches (4-10, default: 7)
- `--colors N`: Set the number of colors (3-8, default: 5)
- `--solver`: Enable the auto-solver
- `--ui [pygame|tkinter|pyqt]`: Select the UI framework (default: pygame)

## How to Play

1. Click on a bird to select it.
2. Click on another branch to move the bird.
3. Birds can only be placed on empty branches or on top of birds of the same color.
4. The goal is to sort all birds so that each branch contains 4 birds of the same color.

## Project Structure

- `main.py`: Entry point for the application
- `models/`: Core game logic and data structures
- `search/`: Search algorithms for the auto-solver
- `ui/`: User interface implementations
- `utils/`: Utility functions
