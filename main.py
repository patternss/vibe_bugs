"""
Worm Digging Game - Main Entry Point
A 2D game where worms dig through terrain using various tools
"""

import pygame
import sys
from src.game import Game
from src.menu import GameMenu
from src.music import MusicSystem
from src.endgame_stats import show_endgame_stats
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    """Main game loop"""
    pygame.init()
    pygame.mixer.init()  # Initialize audio mixer
    
    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vibe Bugs")
    
    # Initialize music system
    music_system = MusicSystem()
    music_system.play_background_music()
    
    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Game state
    game_state = "menu"  # "menu" or "playing"
    menu = GameMenu(screen)
    game = None
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_state == "menu":
                result = menu.handle_event(event)
                if result == "start_game":
                    # Start the game with menu configuration
                    config = menu.get_game_config()
                    game = Game(screen, config)
                    game_state = "playing"
            elif game_state == "playing":
                result = game.handle_event(event)
                if result == "quit_to_menu":
                    # Return to menu
                    game_state = "menu"
                    game = None
        
        # Update game state
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Update music system
        music_system.update(dt)
        
        if game_state == "menu":
            menu.update(dt)
        elif game_state == "playing":
            result = game.update(dt)
            if result == "show_endgame_stats":
                # Show end game statistics screen
                game_stats = game.get_game_stats()
                continue_to_menu = show_endgame_stats(screen, game_stats)
                if continue_to_menu:
                    game_state = "menu"
                    game = None
                else:
                    running = False
        
        # Render everything
        if game_state == "menu":
            menu.render()
        elif game_state == "playing":
            game.render()
            
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()