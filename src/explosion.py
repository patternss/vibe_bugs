"""
General Explosion System
Handles explosion animations and damage logic for all explosive tools
"""

import pygame
import math
import random
from src.config import *

class Explosion:
    def __init__(self, x, y, radius, damage, source_worm=None):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.base_damage = damage
        self.source_worm = source_worm
        
        # Animation properties
        self.start_time = pygame.time.get_ticks()
        self.duration = EXPLOSION_DURATION  # milliseconds
        self.current_radius = 0
        self.is_active = True
        
        # Particle system for explosion effect
        self.particles = []
        self._create_particles()
        
    def _create_particles(self):
        """Create particles for explosion animation"""
        particle_count = int(self.radius * EXPLOSION_PARTICLE_DENSITY)  # More particles for bigger explosions
        
        for _ in range(particle_count):
            # Random angle and distance
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius)
            
            # Calculate particle position
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Random velocity (particles fly outward)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Create particle
            particle = {
                'x': px,
                'y': py,
                'vx': vx,
                'vy': vy,
                'life': 1.0,  # Full life at start
                'decay_rate': random.uniform(1.5, 3.0),  # How fast it fades
                'size': random.randint(2, 6),
                'color_type': random.choice(['fire', 'smoke', 'debris'])
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Update explosion animation"""
        if not self.is_active:
            return False
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        # Check if explosion is finished
        if elapsed >= self.duration:
            self.is_active = False
            return False
            
        # Update explosion radius (grows quickly then shrinks)
        progress = elapsed / self.duration
        if progress < 0.3:
            # Rapid expansion phase
            self.current_radius = (progress / 0.3) * self.radius
        elif progress < 0.7:
            # Full size phase
            self.current_radius = self.radius
        else:
            # Shrinking phase
            shrink_progress = (progress - 0.7) / 0.3
            self.current_radius = self.radius * (1.0 - shrink_progress)
        
        # Update particles
        for particle in self.particles[:]:  # Copy list to safely modify
            # Update position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Apply gravity to particles
            particle['vy'] += 200 * dt  # Gravity effect
            
            # Apply air resistance
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
            
            # Decay life
            particle['life'] -= particle['decay_rate'] * dt
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        return True
    
    def render(self, screen, camera_x=0, camera_y=0):
        """Render explosion effect"""
        if not self.is_active:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only render if visible on screen
        if (-self.radius <= screen_x <= SCREEN_WIDTH + self.radius and 
            -self.radius <= screen_y <= SCREEN_HEIGHT + self.radius):
            
            # Render main explosion circle (shockwave effect)
            if self.current_radius > 0:
                # Create pulsing shockwave effect
                alpha = int(255 * (self.current_radius / self.radius) * 0.3)
                shockwave_color = (255, 200, 100, alpha)  # Orange with transparency
                
                try:
                    # Create surface for alpha blending
                    explosion_surf = pygame.Surface((self.current_radius * 2, self.current_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(explosion_surf, shockwave_color, 
                                     (int(self.current_radius), int(self.current_radius)), 
                                     int(self.current_radius), 3)
                    screen.blit(explosion_surf, (int(screen_x - self.current_radius), 
                                               int(screen_y - self.current_radius)))
                except:
                    # Fallback to regular circle if alpha blending fails
                    pygame.draw.circle(screen, (255, 200, 100), 
                                     (int(screen_x), int(screen_y)), 
                                     int(self.current_radius), 3)
            
            # Render particles
            for particle in self.particles:
                if particle['life'] <= 0:
                    continue
                    
                particle_screen_x = particle['x'] - camera_x
                particle_screen_y = particle['y'] - camera_y
                
                # Skip particles outside screen
                if (particle_screen_x < -10 or particle_screen_x > SCREEN_WIDTH + 10 or
                    particle_screen_y < -10 or particle_screen_y > SCREEN_HEIGHT + 10):
                    continue
                
                # Calculate particle color based on type and life
                life = max(0, min(1, particle['life']))
                alpha = int(255 * life)
                
                if particle['color_type'] == 'fire':
                    # Fire particles: yellow to red to black
                    if life > 0.7:
                        color = (255, 255, int(255 * life))  # Bright yellow
                    elif life > 0.3:
                        color = (255, int(255 * life), 0)  # Orange to red
                    else:
                        color = (int(255 * life), 0, 0)  # Dark red to black
                elif particle['color_type'] == 'smoke':
                    # Smoke particles: white to gray to black
                    gray = int(128 * life)
                    color = (gray, gray, gray)
                else:  # debris
                    # Debris particles: brown/gray chunks
                    brown = int(139 * life)
                    color = (brown, int(69 * life), int(19 * life))
                
                # Draw particle
                try:
                    particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                    particle_surf.fill((*color, alpha))
                    screen.blit(particle_surf, (int(particle_screen_x - particle['size']), 
                                              int(particle_screen_y - particle['size'])))
                except:
                    # Fallback to regular circle
                    pygame.draw.circle(screen, color, 
                                     (int(particle_screen_x), int(particle_screen_y)), 
                                     particle['size'])
    
    def apply_damage(self, worms):
        """Apply explosion damage to all worms in range"""
        damaged_worms = []
        
        for worm in worms:
            if worm.is_dead:
                continue
                
            # Get worm position
            worm_x, worm_y = worm.body_segments[0]
            
            # Calculate distance from explosion center
            distance = math.sqrt((worm_x - self.x)**2 + (worm_y - self.y)**2)
            
            if distance <= self.radius:
                # Calculate damage based on distance (closer = more damage)
                damage = max(EXPLOSION_MIN_DAMAGE, self.base_damage - int(distance))
                
                # Apply damage
                damage_result = worm.take_damage(damage, self.source_worm)
                needs_death_handling = (damage_result and isinstance(damage_result, dict) 
                                      and damage_result.get('needs_death_handling'))
                damaged_worms.append((worm, damage, distance, needs_death_handling, damage_result))
        
        return damaged_worms
    
    def is_finished(self):
        """Check if explosion animation is complete"""
        return not self.is_active and len(self.particles) == 0

# Preset explosion types for easy use
class ExplosionPresets:
    @staticmethod
    def dynamite_explosion(x, y, source_worm=None):
        """Create a standard dynamite explosion"""
        return Explosion(x, y, DYNAMITE_RADIUS, DYNAMITE_BASE_DAMAGE, source_worm)
    
    @staticmethod
    def small_explosion(x, y, source_worm=None):
        """Create a small explosion (e.g., for grenades)"""
        return Explosion(x, y, DYNAMITE_RADIUS // 2, DYNAMITE_BASE_DAMAGE // 2, source_worm)
    
    @staticmethod
    def large_explosion(x, y, source_worm=None):
        """Create a large explosion (e.g., for rockets)"""
        return Explosion(x, y, DYNAMITE_RADIUS * 1.5, DYNAMITE_BASE_DAMAGE * 1.2, source_worm)
    
    @staticmethod
    def custom_explosion(x, y, radius, damage, source_worm=None):
        """Create a custom explosion with specified parameters"""
        return Explosion(x, y, radius, damage, source_worm)