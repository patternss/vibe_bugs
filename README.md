# Worm Digging Game

A 2D game built with Pygame where worms dig through terrain using various tools to reach their destination.

## Features

- **Destructible Terrain**: Dig through different types of terrain (dirt, rock, metal)
- **Multiple Tools**: 
  - Drill: Good for dirt and rock
  - Dynamite: Can destroy any terrain type with large radius
  - Torch: Burns through dirt quickly
  - Laser: Precise cutting through rock and metal
- **Procedural Generation**: Each level has randomly generated terrain
- **Goal-Based Gameplay**: Navigate from start to finish

## Controls

- **WASD** or **Arrow Keys**: Move the worm
- **Mouse Click**: Use current tool at cursor position
- **Tab**: Switch between tools

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required dependencies:
   ```
   pip install pygame noise
   ```
3. Run the game:
   ```
   python main.py
   ```

## Game Mechanics

### Terrain Types
- **Empty**: Can move through freely
- **Dirt** (Brown): Soft terrain, easy to dig
- **Rock** (Gray): Harder terrain, requires drill or stronger tools
- **Metal** (Dark Gray): Strongest terrain, requires dynamite or laser

### Tools
- **Drill**: Medium radius, works on dirt and rock
- **Dynamite**: Large radius, works on all terrain types
- **Torch**: Small radius, only works on dirt but very fast
- **Laser**: Thin line, works on rock and metal with precision

## Project Structure

```
matopeli_pygame/
├── main.py           # Game entry point
├── src/
│   ├── __init__.py   # Package marker
│   ├── config.py     # Game configuration and constants
│   ├── game.py       # Main game logic and coordination
│   ├── terrain.py    # Terrain generation and management
│   └── worm.py       # Player character logic
└── README.md         # This file
```

## Future Enhancements

- Multiple worm characters
- Power-ups and tool upgrades
- Level progression system
- Multiplayer support
- Sound effects and music
- Better graphics and animations
- Enemy creatures in the tunnels