"""
Game Menu System
Handles main menu, player configuration, and game setup
"""

import pygame
import time
from src.config import *

class WormConfig:
    def __init__(self, player_id):
        self.player_id = player_id
        self.name = f"Player {player_id}"
        self.color = self._get_default_color(player_id)
        self.is_human = True if player_id <= 2 else False  # First 2 are human by default
        self.is_active = False  # Will be set by menu
        
    def _get_default_color(self, player_id):
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green  
            (0, 0, 255),    # Blue
            (255, 255, 0)   # Yellow
        ]
        return colors[(player_id - 1) % 4]

class GameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Menu state
        self.game_mode = "battle"  # "battle" or "co-op"
        self.worms = [WormConfig(i+1) for i in range(4)]
        
        # Set first 2 worms as active by default
        for i, worm in enumerate(self.worms):
            worm.is_active = (i < 2)
        
        # UI state
        self.editing_name = None  # Which worm name is being edited
        self.name_input = ""
        self.error_message = ""
        self.error_timer = 0
        
        # Menu options
        self.selected_option = 0
        self.menu_options = ["game_mode", "start_game"]
        
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if self.editing_name is not None:
                self._handle_name_edit(event)
            else:
                return self._handle_menu_navigation(event)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_mouse_click(event.pos)
        
        return None
                
    def _handle_name_edit(self, event):
        """Handle name editing input"""
        if event.key == pygame.K_RETURN:
            # Finish editing
            if self.name_input.strip():
                self.worms[self.editing_name].name = self.name_input.strip()
            self.editing_name = None
            self.name_input = ""
        elif event.key == pygame.K_ESCAPE:
            # Cancel editing
            self.editing_name = None
            self.name_input = ""
        elif event.key == pygame.K_BACKSPACE:
            self.name_input = self.name_input[:-1]
        elif len(self.name_input) < 12 and event.unicode.isprintable():
            self.name_input += event.unicode
            
    def _handle_menu_navigation(self, event):
        """Handle menu navigation keys"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif event.key == pygame.K_LEFT:
            self._adjust_option(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_option(1)
        elif event.key == pygame.K_RETURN:
            if self.menu_options[self.selected_option] == "start_game":
                return "start_game"
        return None
        
    def _adjust_option(self, direction):
        """Adjust the currently selected option"""
        option = self.menu_options[self.selected_option]
        
        if option == "game_mode":
            modes = ["battle", "co-op"]
            current_index = modes.index(self.game_mode)
            new_index = (current_index + direction) % len(modes)
            self.game_mode = modes[new_index]
            
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks on menu elements"""
        # Check if clicking on START GAME button
        start_game_rect = pygame.Rect(50, 385, 250, 40)  # Larger click area for START GAME
        if start_game_rect.collidepoint(pos):
            # Check if we have at least one active player
            active_count = sum(1 for w in self.worms if w.is_active)
            if active_count > 0:
                return "start_game"
            else:
                self.error_message = "At least 1 player required!"
                self.error_timer = 2.0
                return None
        
        # Check if clicking on worm elements (right side)
        for i in range(4):
            # Color indicator (for activation/deactivation)
            color_rect = pygame.Rect(570, 200 + i * 60, 20, 20)
            # Name area
            name_rect = pygame.Rect(600, 200 + i * 60, 200, 30)
            # Human/AI toggle area
            human_rect = pygame.Rect(820, 200 + i * 60, 80, 30)
            
            if color_rect.collidepoint(pos):
                # Toggle active/inactive status
                self._toggle_worm_active(i)
            elif name_rect.collidepoint(pos) and self.worms[i].is_active:
                # Start editing name (only if worm is active)
                self.editing_name = i
                self.name_input = self.worms[i].name
            elif human_rect.collidepoint(pos) and self.worms[i].is_active:
                # Toggle human/AI (only if worm is active)
                self._toggle_human_ai(i)
        
        return None
                
    def _toggle_worm_active(self, worm_index):
        """Toggle active/inactive status for a worm"""
        if self.worms[worm_index].is_active:
            # Deactivating - check minimum requirement
            active_count = sum(1 for w in self.worms if w.is_active)
            if active_count <= 1:
                self.error_message = "At least 1 player required!"
                self.error_timer = 2.0
                return
        else:
            # Activating - check maximum
            active_count = sum(1 for w in self.worms if w.is_active)
            if active_count >= 4:
                self.error_message = "Maximum 4 players allowed!"
                self.error_timer = 2.0
                return
        
        # Toggle the status
        self.worms[worm_index].is_active = not self.worms[worm_index].is_active
        
        # If deactivating, set to AI
        if not self.worms[worm_index].is_active:
            self.worms[worm_index].is_human = False
                
    def _toggle_human_ai(self, worm_index):
        """Toggle human/AI status for a worm"""
        if not self.worms[worm_index].is_active:
            return  # Can't change inactive worms
            
        if not self.worms[worm_index].is_human:
            # Trying to set to human - check if we already have 2 humans
            active_human_count = sum(1 for w in self.worms if w.is_human and w.is_active)
            if active_human_count >= 2:
                self.error_message = "Maximum 2 human players allowed!"
                self.error_timer = 2.0  # Show for 2 seconds
                return
        
        self.worms[worm_index].is_human = not self.worms[worm_index].is_human
        
    def update(self, dt):
        """Update menu state"""
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""
                
    def render(self):
        """Render the menu"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("WORM GAME SETUP", True, WHITE)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=50)
        self.screen.blit(title, title_rect)
        
        # Left column - Main options
        self._render_main_options()
        
        # Right column - Worm list
        self._render_worm_list()
        
        # Error message
        if self.error_message:
            error_text = self.font_small.render(self.error_message, True, RED)
            error_rect = error_text.get_rect(centerx=SCREEN_WIDTH//2, y=SCREEN_HEIGHT-50)
            self.screen.blit(error_text, error_rect)
            
    def _render_main_options(self):
        """Render main menu options on the left"""
        y_start = 150
        y_spacing = 80
        
        # Active players count
        active_count = sum(1 for w in self.worms if w.is_active)
        text = self.font_medium.render(f"Active Players: {active_count}", True, WHITE)
        self.screen.blit(text, (50, y_start))
        
        # Tools & Weapons (placeholder)
        text = self.font_medium.render("Tools & Weapons: Default", True, WHITE)
        self.screen.blit(text, (50, y_start + y_spacing))
        
        # Game mode
        color = YELLOW if self.selected_option == 0 else WHITE
        text = self.font_medium.render(f"Game Mode: {self.game_mode.title()}", True, color)
        self.screen.blit(text, (50, y_start + y_spacing * 2))
        
        # Start game
        color = YELLOW if self.selected_option == 1 else WHITE
        text = self.font_medium.render("START GAME", True, color)
        self.screen.blit(text, (50, y_start + y_spacing * 3))
        
        # Instructions
        instructions_y = y_start + y_spacing * 4 + 20
        self.screen.blit(self.font_small.render("Click color indicators to activate/deactivate players", True, GRAY), (50, instructions_y))
        self.screen.blit(self.font_small.render("Click names to edit, click Human/AI to toggle", True, GRAY), (50, instructions_y + 25))
        
        # Show controls directly
        controls_y = instructions_y + 70
        self.screen.blit(self.font_small.render("GAME CONTROLS:", True, YELLOW), (50, controls_y))
        self.screen.blit(self.font_small.render("Player 1: A/D move, W/S aim, Q/E cycle tools, F use, SPACE jump", True, WHITE), (50, controls_y + 30))
        self.screen.blit(self.font_small.render("Player 2: ←/→ move, ↑/↓ aim, ,/. cycle tools, / use, Right Ctrl jump", True, WHITE), (50, controls_y + 55))
        self.screen.blit(self.font_small.render("ESC: Pause game", True, WHITE), (50, controls_y + 80))
        
    def _render_worm_list(self):
        """Render worm configuration on the right"""
        x_start = 550
        y_start = 150
        
        # Header
        text = self.font_medium.render("WORMS", True, WHITE)
        self.screen.blit(text, (x_start, y_start))
        
        # Worm list
        for i in range(4):
            y = y_start + 50 + i * 60
            worm = self.worms[i]
            
            # Determine colors based on active status
            if worm.is_active:
                # Bright colors for active worms
                display_color = worm.color
                name_color = YELLOW if self.editing_name == i else WHITE
                border_color = WHITE
            else:
                # Dim colors for inactive worms
                display_color = tuple(c // 3 for c in worm.color)  # Dim the color
                name_color = GRAY
                border_color = GRAY
            
            # Color indicator (clickable for activation)
            color_rect = pygame.Rect(x_start, y, 20, 20)
            pygame.draw.rect(self.screen, display_color, color_rect)
            pygame.draw.rect(self.screen, border_color, color_rect, 2)
            
            # Name (editable only if active)
            if self.editing_name == i and worm.is_active:
                display_name = self.name_input + "_"
            else:
                display_name = worm.name
                
            name_text = self.font_small.render(display_name, True, name_color)
            self.screen.blit(name_text, (x_start + 30, y))
            
            # Human/AI toggle (only for active worms)
            if worm.is_active:
                human_text = "HUMAN" if worm.is_human else "AI"
                human_color = GREEN if worm.is_human else GRAY
            else:
                human_text = "INACTIVE"
                human_color = GRAY
                
            toggle_text = self.font_small.render(human_text, True, human_color)
            self.screen.blit(toggle_text, (x_start + 200, y))
                
    def get_game_config(self):
        """Get the current game configuration"""
        active_worms = []
        player_id = 1
        for worm in self.worms:
            if worm.is_active:
                active_worms.append({
                    'name': worm.name,
                    'color': worm.color,
                    'is_human': worm.is_human,
                    'player_id': player_id
                })
                player_id += 1
        
        return {
            'num_worms': len(active_worms),
            'game_mode': self.game_mode,
            'worms': active_worms
        }