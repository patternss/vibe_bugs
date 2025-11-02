"""
Game Menu System
Handles main menu, player configuration, and game setup
"""

import pygame
import time
from src.config import *
from src.game_info_manager import game_info

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
        
        # Try to load cooler fonts, fallback to default if not available
        try:
            # Try some common cool fonts
            self.font_title = pygame.font.SysFont("impact", 64)  # Bold, impactful
            if self.font_title.get_ascent() < 50:  # If Impact not available
                self.font_title = pygame.font.SysFont("arial black", 56)
            if self.font_title.get_ascent() < 40:  # If Arial Black not available
                self.font_title = pygame.font.Font(None, 64)
        except:
            self.font_title = pygame.font.Font(None, 64)
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Menu state
        self.game_mode = "battle"  # "battle" or "coop"
        self.mode_display_names = {"battle": "Battle", "coop": "Co-op"}
        
        # Battle-specific settings
        self.battle_length_minutes = 5  # Default battle length in minutes
        self.battle_length_options = [1, 3, 5, 10, 15]  # Available battle lengths in minutes
        
        # Tools & Weapons settings
        self.tools_mode = "standard"  # "standard" or "unlimited"
        self.tools_mode_options = ["standard", "unlimited"]
        self.tools_display_names = {"standard": "Standard", "unlimited": "Unlimited"}
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
        self.menu_options = self._get_menu_options()
        
        # Initialize game info system
        game_info.set_game_mode(self.game_mode)
        self.info_content = self._get_formatted_info()
    
    def _get_menu_options(self):
        """Get the current menu options based on game mode"""
        options = ["active_players", "tools_weapons", "game_mode"]
        
        # Add mode-specific options
        if self.game_mode == "battle":
            options.append("battle_length")
            
        options.append("start_game")
        return options
        
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
            modes = ["battle", "coop"]
            current_index = modes.index(self.game_mode)
            new_index = (current_index + direction) % len(modes)
            old_mode = self.game_mode
            self.game_mode = modes[new_index]
            
            # Update menu options if mode changed
            if old_mode != self.game_mode:
                self.menu_options = self._get_menu_options()
                # Adjust selected option if needed
                if self.selected_option >= len(self.menu_options):
                    self.selected_option = len(self.menu_options) - 1
            
            # Update game info when mode changes
            game_info.set_game_mode(self.game_mode)
            self.info_content = self._get_formatted_info()
            
        elif option == "battle_length":
            current_index = self.battle_length_options.index(self.battle_length_minutes)
            new_index = (current_index + direction) % len(self.battle_length_options)
            self.battle_length_minutes = self.battle_length_options[new_index]
            
        elif option == "tools_weapons":
            current_index = self.tools_mode_options.index(self.tools_mode)
            new_index = (current_index + direction) % len(self.tools_mode_options)
            self.tools_mode = self.tools_mode_options[new_index]
            
        elif option == "active_players":
            # Cycle through different player count setups
            if direction > 0:
                self._activate_next_player_setup()
            else:
                self._activate_prev_player_setup()
    
    def _activate_next_player_setup(self):
        """Activate the next player configuration"""
        active_count = sum(1 for w in self.worms if w.is_active)
        
        if active_count == 0:
            # Activate first player
            self.worms[0].is_active = True
        elif active_count < 4:
            # Find next inactive player and activate
            for i in range(4):
                if not self.worms[i].is_active:
                    self.worms[i].is_active = True
                    break
        else:
            # All 4 active, go back to 1 player
            for w in self.worms:
                w.is_active = False
            self.worms[0].is_active = True
    
    def _activate_prev_player_setup(self):
        """Activate the previous player configuration"""
        active_count = sum(1 for w in self.worms if w.is_active)
        
        if active_count <= 1:
            # Go to all 4 players
            for w in self.worms:
                w.is_active = True
        else:
            # Find last active player and deactivate
            for i in range(3, -1, -1):
                if self.worms[i].is_active:
                    self.worms[i].is_active = False
                    break
            
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks on menu elements"""
        # Calculate dynamic START GAME button position
        y_start = 140  # Base y position
        y_spacing = 80
        
        # Calculate the position of START GAME button based on number of menu options
        start_game_index = self.menu_options.index("start_game")
        # +2 for Active Players and Tools & Weapons static items
        start_game_y = y_start + y_spacing * (start_game_index + 2)
        
        # Check if clicking on START GAME button
        start_game_rect = pygame.Rect(50, start_game_y, 250, 40)  # Larger click area for START GAME
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
        
    def _get_formatted_info(self):
        """Get formatted game info for current mode - organized for three-column display"""
        mode_info = game_info.get_mode_info()
        controls = game_info.get_controls_info()
        mechanics = game_info.get_mechanics_info()
        
        # Left column - Game Mode Info
        left_column = []
        left_column.append(f"=== {mode_info.get('title', 'Game Mode')} ===")
        left_column.append(mode_info.get('description', ''))
        left_column.append(f"Goal: {mode_info.get('objective', 'N/A')}")
        left_column.append("")
        
        # Timer info
        timer_info = mode_info.get('timer', {})
        left_column.append(f"Duration: {timer_info.get('duration', 'N/A')}")
        if timer_info.get('warning'):
            left_column.append(f"Warning: {timer_info.get('warning', '')}")
        left_column.append("")
        
        # Respawn system
        left_column.append("=== Respawn System ===")
        respawn = mode_info.get('respawn_system', {})
        if respawn.get('enabled'):
            left_column.append(f"Respawn: {respawn.get('respawn_time', '2s')}")
            left_column.append(f"Protection: {respawn.get('protection_time', '2s')}")
            left_column.append("• No attacks during protection")
            left_column.append("• All resources restored")
            left_column.append("• Body flickers to show status")
        
        # Middle column - Combat Tools
        middle_column = []
        middle_column.append("=== Combat Tools ===")
        tools = controls.get('tools', {})
        for tool_name, tool_info in tools.items():
            key = tool_info.get('key', 'Unknown')
            damage = tool_info.get('damage', 'N/A')
            middle_column.append(f"{tool_name.title()}: {key}")
            middle_column.append(f"  {damage}")
        middle_column.append("")
        
        # Basic controls
        middle_column.append("=== Basic Controls ===")
        movement = controls.get('movement', {})
        middle_column.append(f"Move Left: {movement.get('left', 'A')}")
        middle_column.append(f"Move Right: {movement.get('right', 'D')}")
        middle_column.append(f"Jump: {movement.get('jump', 'W')}")
        middle_column.append("")
        middle_column.append("Loot Tombstone: E key")
        
        # Right column - Game Mechanics
        right_column = []
        right_column.append("=== Health System ===")
        health = mechanics.get('health_system', {})
        right_column.append("Body changes with damage:")
        right_column.append("• Full health: Complete worm")
        right_column.append("• Damaged: Shorter body")
        right_column.append("• Critical: Head only")
        right_column.append("• Zero health: Tombstone")
        right_column.append("")
        
        # Environmental hazards
        fall_dmg = mechanics.get('fall_damage', {})
        right_column.append("=== Fall Damage ===")
        right_column.append("• Small drops: Safe")
        right_column.append("• Medium drops: Some damage")
        right_column.append("• High drops: Major damage")
        right_column.append("• Extreme drops: Can be fatal")
        right_column.append("")
        right_column.append("=== Tips ===")
        right_column.append("• Dig safe paths down")
        right_column.append("• Use protection time wisely")
        right_column.append("• Collect tombstone resources")
        
        return {"left": left_column, "middle": middle_column, "right": right_column}
        
    def update(self, dt):
        """Update menu state"""
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""
                
    def render(self):
        """Render the menu"""
        self.screen.fill(BLACK)
        
        # Title with cool green color and better font
        title_color = (0, 255, 100)  # Bright green
        title = self.font_title.render("VIBE BUGS", True, title_color)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=30)
        
        # Add a subtle shadow effect
        shadow_color = (0, 150, 60)  # Darker green for shadow
        title_shadow = self.font_title.render("VIBE BUGS", True, shadow_color)
        shadow_rect = title_shadow.get_rect(centerx=SCREEN_WIDTH//2 + 3, y=33)
        
        # Render shadow first, then main title
        self.screen.blit(title_shadow, shadow_rect)
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
        y_start = 140  # Increased from 120 to add more space after title
        y_spacing = 80
        current_y = y_start
        
        # Render dynamic menu options
        for i, option in enumerate(self.menu_options):
            color = YELLOW if self.selected_option == i else WHITE
            x_pos = 50  # Default position
            
            if option == "active_players":
                active_count = sum(1 for w in self.worms if w.is_active)
                text = self.font_medium.render(f"Active Players: {active_count}", True, color)
                
            elif option == "tools_weapons":
                tools_display = self.tools_display_names.get(self.tools_mode, self.tools_mode.title())
                text = self.font_medium.render(f"Tools & Weapons: {tools_display}", True, color)
                
            elif option == "game_mode":
                mode_display = self.mode_display_names.get(self.game_mode, self.game_mode.title())
                text = self.font_medium.render(f"Game Mode: {mode_display}", True, color)
                
            elif option == "battle_length":
                # Indent battle-specific options to show they're sub-options
                x_pos = 70  # Indent by 20 pixels
                text = self.font_medium.render(f"  Battle Length: {self.battle_length_minutes} min", True, color)
                
            elif option == "start_game":
                text = self.font_medium.render("START GAME", True, color)
                
            self.screen.blit(text, (x_pos, current_y))
            current_y += y_spacing
        
        # Instructions
        instructions_y = current_y + 20
        self.screen.blit(self.font_small.render("Click color indicators to activate/deactivate players", True, GRAY), (50, instructions_y))
        self.screen.blit(self.font_small.render("Click names to edit, click Human/AI to toggle", True, GRAY), (50, instructions_y + 25))
        
        # Show dynamic game info
        self._render_game_info(50, instructions_y + 70)
        
    def _render_game_info(self, x, y):
        """Render dynamic game information in three columns spanning full width"""
        left_column = self.info_content["left"]
        middle_column = self.info_content["middle"]
        right_column = self.info_content["right"]
        
        # Calculate column positions for full window width
        window_width = self.screen.get_width()
        worm_section_width = 400  # Width reserved for worm list on the right
        available_width = window_width - worm_section_width - x - 20  # 20px margin
        column_width = available_width // 3
        
        left_x = x
        middle_x = x + column_width
        right_x = x + (column_width * 2)
        
        # Render all three columns
        self._render_column(left_column, left_x, y)
        self._render_column(middle_column, middle_x, y)
        self._render_column(right_column, right_x, y)
    
    def _render_column(self, column_content, x, y):
        """Render a single column of info content with word wrapping"""
        current_y = y
        
        # Calculate column width for wrapping
        window_width = self.screen.get_width()
        worm_section_width = 400
        available_width = window_width - worm_section_width - 50 - 20  # 50 = start x, 20 = margin
        column_width = available_width // 3 - 20  # 20px padding between columns
        
        for line in column_content:
            if line.startswith("===") and line.endswith("==="):
                # Section header
                wrapped_lines = self._wrap_text(line, column_width, self.font_small)
                for wrapped_line in wrapped_lines:
                    text = self.font_small.render(wrapped_line, True, YELLOW)
                    self.screen.blit(text, (x, current_y))
                    current_y += 28
            elif line.startswith("•"):
                # Bullet point
                wrapped_lines = self._wrap_text(line, column_width - 10, self.font_small)
                for i, wrapped_line in enumerate(wrapped_lines):
                    if i == 0:
                        # First line keeps the bullet
                        text = self.font_small.render(wrapped_line, True, GREEN)
                        self.screen.blit(text, (x + 10, current_y))
                    else:
                        # Continuation lines are indented more
                        text = self.font_small.render(wrapped_line.strip(), True, GREEN)
                        self.screen.blit(text, (x + 20, current_y))
                    current_y += 22
            elif line.startswith("  "):
                # Indented text (tool descriptions)
                wrapped_lines = self._wrap_text(line.strip(), column_width - 15, self.font_small)
                for wrapped_line in wrapped_lines:
                    text = self.font_small.render(wrapped_line, True, GRAY)
                    self.screen.blit(text, (x + 15, current_y))
                    current_y += 20
            elif line.strip():
                # Regular text
                if ":" in line and not line.startswith("==="):
                    # Key: value pairs or tool names
                    wrapped_lines = self._wrap_text(line, column_width, self.font_small)
                    for wrapped_line in wrapped_lines:
                        text = self.font_small.render(wrapped_line, True, WHITE)
                        self.screen.blit(text, (x, current_y))
                        current_y += 22
                else:
                    # Descriptions
                    wrapped_lines = self._wrap_text(line, column_width, self.font_small)
                    for wrapped_line in wrapped_lines:
                        text = self.font_small.render(wrapped_line, True, GRAY)
                        self.screen.blit(text, (x, current_y))
                        current_y += 22
            else:
                # Empty line spacing
                current_y += 12
    
    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within specified pixel width"""
        if not text.strip():
            return [""]
        
        # Check if the text fits on one line
        text_surface = font.render(text, True, (255, 255, 255))
        if text_surface.get_width() <= max_width:
            return [text]
        
        # Split text into words and wrap
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Test adding this word to current line
            test_line = current_line + (" " if current_line else "") + word
            test_surface = font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                # Word doesn't fit, start new line
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, break it
                    lines.append(word)
                    current_line = ""
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
        
    def _render_worm_list(self):
        """Render worm configuration on the right"""
        x_start = 550
        y_start = 140  # Increased to match main options
        
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
        
        config = {
            'num_worms': len(active_worms),
            'game_mode': self.game_mode,
            'tools_mode': self.tools_mode,
            'worms': active_worms
        }
        
        # Add battle-specific settings
        if self.game_mode == "battle":
            config['battle_length_minutes'] = self.battle_length_minutes
        
        return config