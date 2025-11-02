"""
Tombstone System
Handles tombstones that drop when worms die, containing lootable resources
"""

import pygame
import math
from src.config import *

class Tombstone:
    def __init__(self, x, y, gas_amount, dynamite_amount, deceased_worm_name="Unknown"):
        self.x = float(x)
        self.y = float(y)
        self.gas_amount = gas_amount
        self.dynamite_amount = dynamite_amount
        self.deceased_worm_name = deceased_worm_name
        
        # Visual properties
        self.creation_time = pygame.time.get_ticks()
        self.bob_offset = 0  # For floating animation
        self.glow_intensity = 0  # For glowing effect
        self.is_looted = False
        
        # Interaction radius
        self.interaction_radius = WORM_RADIUS + 10
        
    def update(self, dt):
        """Update tombstone animations"""
        if self.is_looted:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.creation_time) / 1000.0
        
        # Floating animation (slow bob up and down)
        self.bob_offset = math.sin(elapsed * 2.0) * 3
        
        # Glowing animation (pulsing effect)
        self.glow_intensity = (math.sin(elapsed * 3.0) + 1.0) * 0.3  # 0.0 to 0.6
        
    def can_be_looted_by(self, worm):
        """Check if a worm can loot this tombstone"""
        if self.is_looted:
            return False
            
        # Calculate distance to worm
        worm_x, worm_y = worm.body_segments[0]
        distance = math.sqrt((worm_x - self.x)**2 + (worm_y - self.y)**2)
        
        return distance <= self.interaction_radius
        
    def loot(self, worm):
        """Give resources to worm and mark tombstone as looted"""
        if self.is_looted:
            return False
            
        # Transfer resources to worm
        worm.gas = min(MAX_GAS, worm.gas + self.gas_amount)
        worm.dynamite_count += self.dynamite_amount
        
        # Mark as looted
        self.is_looted = True
        return True
        
    def render(self, screen, camera_x=0, camera_y=0):
        """Render the tombstone"""
        if self.is_looted:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.bob_offset
        
        # Only render if visible on screen
        if (-50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50):
            
            # Draw glow effect
            if self.glow_intensity > 0:
                glow_radius = 25 + int(self.glow_intensity * 10)
                glow_alpha = int(self.glow_intensity * 100)
                glow_color = (255, 215, 0, glow_alpha)  # Golden glow
                
                try:
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surf, (int(screen_x - glow_radius), int(screen_y - glow_radius)))
                except:
                    pass  # Skip glow if alpha blending fails
            
            # Draw tombstone base (dark gray rectangle)
            tombstone_width = 16
            tombstone_height = 20
            base_rect = pygame.Rect(
                int(screen_x - tombstone_width // 2),
                int(screen_y - tombstone_height // 2),
                tombstone_width,
                tombstone_height
            )
            pygame.draw.rect(screen, (64, 64, 64), base_rect)  # Dark gray
            pygame.draw.rect(screen, (32, 32, 32), base_rect, 2)  # Black border
            
            # Draw tombstone top (curved)
            top_center_x = int(screen_x)
            top_center_y = int(screen_y - tombstone_height // 2)
            pygame.draw.circle(screen, (64, 64, 64), (top_center_x, top_center_y), tombstone_width // 2)
            pygame.draw.circle(screen, (32, 32, 32), (top_center_x, top_center_y), tombstone_width // 2, 2)
            
            # Draw cross on tombstone
            cross_size = 6
            cross_color = (200, 200, 200)  # Light gray
            # Vertical line
            pygame.draw.line(screen, cross_color,
                           (top_center_x, top_center_y - cross_size // 2),
                           (top_center_x, top_center_y + cross_size // 2), 2)
            # Horizontal line
            pygame.draw.line(screen, cross_color,
                           (top_center_x - cross_size // 2, top_center_y),
                           (top_center_x + cross_size // 2, top_center_y), 2)
            
            # Draw resource indicators if tombstone has resources
            if self.gas_amount > 0 or self.dynamite_amount > 0:
                # Small resource icons above tombstone
                icon_y = int(screen_y - tombstone_height - 15)
                icon_x = int(screen_x)
                
                if self.gas_amount > 0:
                    # Gas bottle icon (small green circle)
                    pygame.draw.circle(screen, (0, 255, 0), (icon_x - 8, icon_y), 4)
                    pygame.draw.circle(screen, (0, 150, 0), (icon_x - 8, icon_y), 4, 1)
                    
                if self.dynamite_amount > 0:
                    # Dynamite icon (small red rectangle)
                    dynamite_rect = pygame.Rect(icon_x + 2, icon_y - 3, 6, 6)
                    pygame.draw.rect(screen, (255, 0, 0), dynamite_rect)
                    pygame.draw.rect(screen, (150, 0, 0), dynamite_rect, 1)
                    
            # Draw interaction hint when worm is nearby (this will be handled by the game)
            # The game can call this method to show interaction prompts
            
    def render_interaction_hint(self, screen, camera_x=0, camera_y=0):
        """Render interaction hint text"""
        if self.is_looted:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.bob_offset
        
        # Only render if visible on screen
        if (-100 <= screen_x <= SCREEN_WIDTH + 100 and -100 <= screen_y <= SCREEN_HEIGHT + 100):
            # Create font for hint text
            try:
                font = pygame.font.Font(None, 24)
                hint_text = "Press E to loot"
                text_surface = font.render(hint_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y - 40)))
                
                # Draw background for text
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
                
                screen.blit(text_surface, text_rect)
            except:
                pass  # Skip text if font loading fails
                
    def get_loot_info(self):
        """Get information about what this tombstone contains"""
        return {
            'gas': self.gas_amount,
            'dynamite': self.dynamite_amount,
            'deceased': self.deceased_worm_name
        }