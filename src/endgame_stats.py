"""
End Game Statistics Screen
Displays match results, player rankings, and fun awards
"""

import pygame
import math
from src.config import *

class EndGameStats:
    """
    End game statistics screen showing match results and awards
    """
    
    def __init__(self, screen, game_stats):
        self.screen = screen
        self.game_stats = game_stats  # Dictionary with player stats
        
        # Fonts
        try:
            self.font_title = pygame.font.SysFont("impact", 48)
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 24)
        
        # Colors
        self.bg_color = (15, 15, 25)
        self.title_color = (0, 255, 100)  # Bright green like main menu
        self.winner_color = (255, 215, 0)  # Gold
        self.award_color = (255, 160, 50)  # Orange
        self.text_color = (255, 255, 255)
        self.secondary_color = (180, 180, 180)
        
        # Animation
        self.animation_time = 0
        
        # Buttons - moved higher up for better layout
        self.return_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 120, 200, 50)
        
        # Calculate stats and awards
        self.rankings = self._calculate_rankings()
        self.awards = self._calculate_awards()
    
    def _calculate_rankings(self):
        """Calculate player rankings sorted by kills"""
        players = []
        for worm_id, stats in self.game_stats.items():
            # Calculate K/D ratio with proper handling of division by zero
            if stats['deaths'] == 0:
                if stats['kills'] == 0:
                    kd_ratio = 0.0  # 0 kills and 0 deaths = 0.0 ratio
                else:
                    kd_ratio = float(stats['kills'])  # Kills with no deaths = kills as ratio
            else:
                kd_ratio = stats['kills'] / stats['deaths']  # Normal K/D calculation
                
            players.append({
                'name': stats['name'],
                'color': stats['color'],
                'kills': stats['kills'],
                'deaths': stats['deaths'],
                'kd_ratio': kd_ratio,
                'fall_deaths': stats.get('fall_deaths', 0),
                'self_deaths': stats.get('self_deaths', 0)
            })
        
        # Sort by kills (descending), then by fewest deaths as tiebreaker
        players.sort(key=lambda x: (x['kills'], -x['deaths']), reverse=True)
        return players
    
    def _calculate_awards(self):
        """Calculate fun awards for players"""
        if not self.rankings:
            return {}
        
        awards = {}
        
        # 🏆 Champion (most kills)
        champion = max(self.rankings, key=lambda x: x['kills'])
        if champion['kills'] > 0:
            awards['champion'] = champion
        
        # 💀 Eliminator (most aggressive - most total kills + deaths)
        eliminator = max(self.rankings, key=lambda x: x['kills'] + x['deaths'])
        if eliminator['kills'] + eliminator['deaths'] > 0:
            awards['eliminator'] = eliminator
        
        # 🛡️ Survivor (fewest deaths, but must have participated)
        survivors = [p for p in self.rankings if p['kills'] > 0 or p['deaths'] > 0]
        if survivors:
            survivor = min(survivors, key=lambda x: x['deaths'])
            awards['survivor'] = survivor
        
        # 🎯 Sharpshooter (best K/D ratio, minimum 2 kills)
        sharpshooters = [p for p in self.rankings if p['kills'] >= 2]
        if sharpshooters:
            sharpshooter = max(sharpshooters, key=lambda x: x['kd_ratio'])
            awards['sharpshooter'] = sharpshooter
        
        # 🤦 Fumbler (most fall/self deaths)
        fumbler_deaths = [(p, p['fall_deaths'] + p['self_deaths']) for p in self.rankings]
        fumbler_deaths.sort(key=lambda x: x[1], reverse=True)
        if fumbler_deaths and fumbler_deaths[0][1] > 0:
            awards['fumbler'] = fumbler_deaths[0][0]
        
        return awards
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.QUIT:
            return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.return_button.collidepoint(event.pos):
                return "menu"
        return None
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
    
    def render(self):
        """Render the stats screen"""
        self.screen.fill(self.bg_color)
        
        # Title with animation
        title_y = 40 + math.sin(self.animation_time * 2) * 3
        title = self.font_title.render("MATCH RESULTS", True, self.title_color)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH//2, y=title_y)
        self.screen.blit(title, title_rect)
        
        # Main content area - moved down to give more space
        content_y = 100
        
        # Left side - Rankings
        self._render_rankings(50, content_y)
        
        # Right side - Awards
        self._render_awards(SCREEN_WIDTH//2 + 50, content_y)
        
        # Return button
        self._render_return_button()
    
    def _render_rankings(self, x, y):
        """Render player rankings"""
        current_y = y
        
        # Header
        header = self.font_large.render("FINAL RANKINGS", True, self.winner_color)
        self.screen.blit(header, (x, current_y))
        current_y += 50
        
        # Column headers
        headers = ["RANK", "PLAYER", "KILLS", "DEATHS", "K/D"]
        header_x_positions = [x, x + 60, x + 200, x + 280, x + 360]
        
        for i, header_text in enumerate(headers):
            header_surface = self.font_small.render(header_text, True, self.secondary_color)
            self.screen.blit(header_surface, (header_x_positions[i], current_y))
        current_y += 30
        
        # Player rankings
        for i, player in enumerate(self.rankings[:4]):  # Show top 4
            rank_color = self.winner_color if i == 0 else self.text_color
            
            # Rank with special formatting for winner
            rank_text = f"{i + 1}."
            if i == 0:
                rank_text = "[#1]"  # Text symbol instead of emoji
            rank_surface = self.font_medium.render(rank_text, True, rank_color)
            self.screen.blit(rank_surface, (header_x_positions[0], current_y))
            
            # Player name with color indicator
            name_surface = self.font_medium.render(player['name'], True, rank_color)
            self.screen.blit(name_surface, (header_x_positions[1], current_y))
            
            # Color indicator
            color_rect = pygame.Rect(header_x_positions[1] - 20, current_y + 5, 12, 12)
            pygame.draw.rect(self.screen, player['color'], color_rect)
            pygame.draw.rect(self.screen, self.text_color, color_rect, 1)
            
            # Kills
            kills_surface = self.font_medium.render(str(player['kills']), True, rank_color)
            self.screen.blit(kills_surface, (header_x_positions[2], current_y))
            
            # Deaths
            deaths_surface = self.font_medium.render(str(player['deaths']), True, rank_color)
            self.screen.blit(deaths_surface, (header_x_positions[3], current_y))
            
            # K/D ratio with proper formatting
            if player['deaths'] == 0:
                if player['kills'] == 0:
                    kd_text = "0.00"  # 0 kills and 0 deaths
                else:
                    kd_text = "∞"  # Kills with no deaths
            else:
                kd_text = f"{player['kd_ratio']:.2f}"  # Normal ratio
            kd_surface = self.font_medium.render(kd_text, True, rank_color)
            self.screen.blit(kd_surface, (header_x_positions[4], current_y))
            
            current_y += 35
    
    def _render_awards(self, x, y):
        """Render awards section"""
        current_y = y
        
        # Header
        header = self.font_large.render("ACHIEVEMENTS", True, self.winner_color)
        self.screen.blit(header, (x, current_y))
        current_y += 50
        
        # Award definitions with text symbols instead of emojis
        award_info = {
            'champion': ('[CHAMPION]', 'Most eliminations'),
            'eliminator': ('[ELIMINATOR]', 'Most aggressive'),
            'survivor': ('[SURVIVOR]', 'Fewest deaths'),
            'sharpshooter': ('[SHARPSHOOTER]', 'Best K/D ratio'),
            'fumbler': ('[FUMBLER]', 'Most accidents')
        }
        
        # Render each award
        for award_key, (award_title, award_desc) in award_info.items():
            if award_key in self.awards:
                player = self.awards[award_key]
                
                # Award title
                title_surface = self.font_medium.render(award_title, True, self.award_color)
                self.screen.blit(title_surface, (x, current_y))
                current_y += 25
                
                # Player name and description
                player_text = f"{player['name']} - {award_desc}"
                player_surface = self.font_small.render(player_text, True, self.text_color)
                self.screen.blit(player_surface, (x + 20, current_y))
                
                # Color indicator
                color_rect = pygame.Rect(x, current_y + 3, 12, 12)
                pygame.draw.rect(self.screen, player['color'], color_rect)
                pygame.draw.rect(self.screen, self.text_color, color_rect, 1)
                
                current_y += 40
            else:
                # No award winner
                title_surface = self.font_medium.render(award_title, True, self.secondary_color)
                self.screen.blit(title_surface, (x, current_y))
                current_y += 25
                
                no_winner = self.font_small.render("No winner", True, self.secondary_color)
                self.screen.blit(no_winner, (x + 20, current_y))
                current_y += 40
    
    def _render_return_button(self):
        """Render the return to menu button"""
        # Button background
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.return_button.collidepoint(mouse_pos)
        button_color = (60, 60, 80) if not is_hovered else (80, 80, 100)
        
        pygame.draw.rect(self.screen, button_color, self.return_button)
        pygame.draw.rect(self.screen, self.text_color, self.return_button, 2)
        
        # Button text
        button_text = self.font_medium.render("RETURN TO MENU", True, self.text_color)
        button_rect = button_text.get_rect(center=self.return_button.center)
        self.screen.blit(button_text, button_rect)
        
        # Instructions - moved higher up
        instructions = "Press ESC or ENTER to return to menu"
        inst_surface = self.font_small.render(instructions, True, self.secondary_color)
        inst_rect = inst_surface.get_rect(centerx=SCREEN_WIDTH//2, y=SCREEN_HEIGHT - 65)
        self.screen.blit(inst_surface, inst_rect)

def show_endgame_stats(screen, game_stats):
    """
    Display the end game stats screen and handle events until closed.
    Returns True if should return to menu, False if should quit.
    """
    stats_screen = EndGameStats(screen, game_stats)
    clock = pygame.time.Clock()
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            result = stats_screen.handle_event(event)
            if result == "quit":
                return False
            elif result == "menu":
                return True
        
        stats_screen.update(dt)
        stats_screen.render()
        pygame.display.flip()
    
    return True