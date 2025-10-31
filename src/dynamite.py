"""
Dynamite class for thrown explosives with timers
"""

import pygame
import math
import time
import random
from src.config import *

class ThrownDynamite:
    # Class variable for explosion sound (shared by all instances)
    explosion_sound = None
    
    @classmethod
    def _create_explosion_sound(cls):
        """Create a deep explosion sound effect"""
        if cls.explosion_sound is None:
            try:
                # Create a deep explosion sound using random noise and low frequencies
                sample_rate = 22050
                duration = 0.8  # Longer duration for more impact
                samples = int(sample_rate * duration)
                
                # Generate explosion sound data with deeper frequencies
                sound_data = []
                for i in range(samples):
                    t = i / sample_rate
                    
                    # Create noise with decreasing amplitude (exponential decay)
                    amplitude = max(0, 1.0 - (i / samples)) ** 1.5  # Less steep decay for longer rumble
                    
                    # Add low-frequency rumble component
                    rumble_freq = 40 + (1.0 - t/duration) * 60  # 40-100 Hz decreasing
                    rumble = math.sin(2 * math.pi * rumble_freq * t) * 0.4 * amplitude
                    
                    # Add mid-frequency boom
                    boom_freq = 80 + (1.0 - t/duration) * 120  # 80-200 Hz decreasing
                    boom = math.sin(2 * math.pi * boom_freq * t) * 0.3 * amplitude
                    
                    # High-frequency noise for impact
                    noise = random.uniform(-1, 1) * amplitude * 0.2
                    
                    # Combine all components
                    combined = (rumble + boom + noise) * 0.4  # Lower overall volume
                    
                    # Convert to 16-bit integer
                    sample = int(combined * 32767)
                    sample = max(-32768, min(32767, sample))  # Clamp
                    sound_data.extend([sample, sample])  # Stereo
                
                # Convert to bytes
                sound_bytes = b''.join(sample.to_bytes(2, 'little', signed=True) for sample in sound_data)
                
                # Create pygame sound object
                cls.explosion_sound = pygame.mixer.Sound(buffer=sound_bytes)
            except Exception as e:
                print(f"Could not create explosion sound: {e}")
                # Create a silent sound as fallback
                cls.explosion_sound = None
    
    def __init__(self, x, y, target_x, target_y, power):
        self.start_x = float(x)
        self.start_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.start_time = time.time()
        
        # Calculate direction and velocity based on target and power
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 1
            direction_y = 0
        
        # Calculate velocity based on power (0-100)
        base_speed = 200  # Base throw speed
        speed_multiplier = 0.5 + (power / 100) * 1.5  # 0.5x to 2x speed
        velocity = base_speed * speed_multiplier
        
        # Set velocity components
        self.vel_x = direction_x * velocity
        self.vel_y = direction_y * velocity - 50  # Slight upward bias for arc
        
        # Physics properties
        self.gravity = GRAVITY  # Use game gravity
        self.has_exploded = False
        
    def update(self, dt, terrain=None):
        """Update dynamite position and check for explosion"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Physics-based movement
        if not self.has_exploded and elapsed < DYNAMITE_FUSE_TIME:
            # Store old position for collision detection
            old_x = self.x
            old_y = self.y
            
            # Update position with velocity
            new_x = self.x + self.vel_x * dt
            new_y = self.y + self.vel_y * dt
            
            # Check for terrain collision if terrain is provided
            if terrain and terrain.is_solid(new_x, new_y):
                # Hit the ground - stop movement
                self.vel_x = 0
                self.vel_y = 0
                # Don't update position, keep it at the last valid position
            else:
                # No collision, update position normally
                self.x = new_x
                self.y = new_y
                
                # Apply gravity to Y velocity
                self.vel_y += self.gravity * dt
            
        # Check for explosion (timer-based)
        if elapsed >= DYNAMITE_FUSE_TIME and not self.has_exploded:
            self.has_exploded = True
            # Create and play explosion sound
            self._create_explosion_sound()
            if self.explosion_sound:
                self.explosion_sound.play()
            return True  # Signal explosion
            
        return False
        
    def get_position(self):
        """Get current position"""
        return (self.x, self.y)
        
    def render(self, screen, camera_x=0, camera_y=0):
        """Render the dynamite"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Convert to screen coordinates
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only render if visible on screen
        if -20 <= screen_x <= SCREEN_WIDTH + 20 and -20 <= screen_y <= SCREEN_HEIGHT + 20:
            # Blink faster as explosion approaches
            blink_rate = 2 + (elapsed / DYNAMITE_FUSE_TIME) * 8
            blink_phase = math.sin(elapsed * blink_rate * math.pi) > 0
            
            # Draw dynamite stick
            dynamite_color = RED if blink_phase else (150, 0, 0)
            fuse_color = YELLOW if blink_phase else (200, 200, 0)
            
            # Dynamite body
            pygame.draw.rect(screen, dynamite_color, 
                            (int(screen_x - 4), int(screen_y - 2), 8, 4))
            
            # Fuse
            pygame.draw.circle(screen, fuse_color, (int(screen_x + 4), int(screen_y - 3)), 2)
            
            # Sparks on fuse
            if blink_phase:
                for i in range(3):
                    spark_x = int(screen_x + 4 + i * 2)
                    spark_y = int(screen_y - 3)
                    pygame.draw.circle(screen, WHITE, (spark_x, spark_y), 1)