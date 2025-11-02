# Worm Digging Game

A 2D game built with Pygame where worms dig through terrain using various tools to reach their destination.
This project is purely vibe coded
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

- re-write the hitbox system  matching the current animation style, with multiple body parts. Update the animation system also to match the following changes 
    - Worms have a multi-segment hit-boxes 
        - 4 body segments with decreasing radii
        - Segments follow each other in a trail
        - Each segment has a specific position and radius
    - when a worm loses enough hp it loses these body parts
        - 20% drop means a loss of one body part. 
        - The last 20% is just the head
        - when the hp drops to 0, the worm (the remaining head part) is removed and a tomb-tome is erected to the place where the worm died
    - with hp boost - the worm grows more circles again



- Create separation between battle mode and co-op mode (leave also room for future battle team mode develplment):
    - Battle mode features:
        - worms are able to harm each other
        - worms get killed and respawn to a random location after 5 seconds 
        - tomb-stones can be collected and they carry 20% of the ammo, fuel, etc. that the worm had when it died
        - add "kills" and "deaths" counters to the upper stat bar for every worm
        - timer how long the map lasts 
            - timer is set in the game menu
            - default time 5 minutes
            - is shown at the top right corner of the upper stats bar in the game
        - after the game ends - stats will be shown in a table where columns are as follows: worm, kills, deaths (ordered by most kills)
        - add item drops from the sky (dynamites, healt-boost, fuel for torch, speed boost )
        - no stargates and no switching between maps or levels
    
    - Co-op mode: 
        - no friendly fire
        - keep wormhole system and multiple levels (implementing level system later)
        - no looting other player's tombstones - instead ressurect another worm by going to it's tombstone and standing there for 3 seconds
        - Level number added to the upper stats box
        - no item drops - but collactables are found inside the map. 
        - when the level changes worms get boost to hp (like 20 hp) maybe other boosts also like dynamite so leave room to add those later, but let's start with the hp for now
        - add ai creeps to the game
            - they try to harm the worms
            - creep kill counters for players in upper stats box
            - more bug-like appearence (different colors)
            - create now only one type of bug/creep (we'll add these later)
            - movement
                - back and forth movement atm. they cover small areas and attack the worms only when they are in close vincinity (create a variabale for this)
                - return to their posts if the distance to a worm is above some value (this value is greater than the close vincinity variable,  but still not too long)
            - battle
                - meelee and ranged creeps 
                    - meelee creeps expload when hitting a worm (20 hp per explotion)
                    - ranged creeps have unlimited ammo (damage 5 hp per hit)

- map editor tool
- a tool for creating and editing levels
    - add and remove terrain, creeps, weapons 
    - toolbar for creating these changes
    - map-file type that can be used in conjunction with the current rendering system
    
- AI worms
- AI for battle mode
    - tries to get as many kills as possible
    - few different profiles (agressive, medium, camper etc.)
- AI for co-op mode
    - a friednly worm to help a human player in co-op mode


- other changes 
    - the direction of the drill can be changed (keep the shape and size of the current indicator box )
        - use the same direction change system as with laser for example
    - add speed boost - 200% speed (create a graphical effect around the worm - maybe a blueish glow)
    - add damage from dropping (increasing damage for drops that are over 50px (variable for this so it can be tested and changed))



## ideas for future
- boss levels
- co-op battle mode
- textures for the tool/weapon in use atm. 
- items and weapons
    - parachute
    - rope gun 
    