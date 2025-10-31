"""
Worm Player Class
Handles worm movement, tool usage, and interaction with terrain
"""

import pygame
import math
import random
import time
from src.config import *
from src.dynamite import ThrownDynamite

class Worm:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0
        self.vel_y = 0
        
        # Health system
        self.max_hp = 100
        self.hp = self.max_hp
        
        # Physics state
        self.on_ground = False
        self.can_jump = True
        
        # Tools
        self.tools = ["drill", "dynamite", "torch", "laser"]
        self.current_tool_index = 0
        self.current_tool = self.tools[self.current_tool_index]
        
        # Gas system
        self.gas = STARTING_GAS
        
        # Dynamite system
        self.dynamite_count = DYNAMITE_COUNT_START
        self.thrown_dynamites = []  # List of active thrown dynamites
        

        # Power charging system
        self.charging_power = False
        self.power_level = 0
        self.charge_start_time = 0
        
        # Fire effects
        self.fire_particles = []  # For torch effect
        self.torch_fire_timer = 0
        
        # Laser effects
        self.laser_firing = False
        self.laser_fire_timer = 0
        self.laser_start_pos = None
        self.laser_end_pos = None
        
        # Laser battery system
        self.laser_battery = 100.0  # Full battery (0-100%)
        self.laser_use_count = 0    # Track rapid usage
        self.laser_cooldown_timer = 0.0  # Cooldown before recharging
        self.laser_last_use_time = 0.0   # Track time between uses
        
        # Torch direction state (1 for right, -1 for left)
        self.torch_direction = 1
        
        # Worm facing direction (1 for right, -1 for left)
        self.facing_direction = 1
        
        # Tool direction state for smooth interpolation
        self.tool_target_angle = 0  # Target angle for tool direction
        self.tool_current_angle = 0  # Current smoothed angle
        self.angle_interpolation_speed = 3.0  # Reduced speed for smoother control
        
        # Key press tracking for gradual direction change
        self.direction_key_timers = {
            pygame.K_UP: 0.0,
            pygame.K_DOWN: 0.0,
            pygame.K_LEFT: 0.0,
            pygame.K_RIGHT: 0.0
        }
        self.max_direction_time = 1.0  # Time to reach full deflection
        self.angle_locked = False  # Track if angle should stay locked
        
        # Worm properties
        self.name = "Player"
        self.color = WORM_COLOR
        self.is_human = True
        self.player_id = 1
        
        # Input state
        self.keys_pressed = set()
        
        # Worm body segments for trail effect
        self.body_segments = [(x, y) for _ in range(6)]  # 6 segments
        self.segment_update_timer = 0
        
        # Tool range limits
        self.max_reach_distance = WORM_RADIUS * 2  # How far worm can reach to dig
        
        # Virtual cursor position
        self.cursor_x = x + 50  # Start cursor near worm
        self.cursor_y = y
        self.cursor_speed = 300  # Pixels per second (increased for faster dynamite movement)
        
        # Initialize sound effects
        self._create_tool_sounds()
        
    def _create_tool_sounds(self):
        """Create sound effects for tools"""
        try:
            # Create drill sound - repetitive mechanical noise
            self.drill_sound = self._create_drill_sound()
            
            # Create laser sound - electronic beam
            self.laser_sound = self._create_laser_sound()
            
            # Create torch sound - crackling fire
            self.torch_sound = self._create_torch_sound()
            
        except Exception as e:
            print(f"Could not create tool sounds: {e}")
            self.drill_sound = None
            self.laser_sound = None
            self.torch_sound = None
    
    def _create_drill_sound(self):
        """Create drilling sound effect"""
        try:
            sample_rate = 22050
            duration = 0.3  # Short loop
            samples = int(sample_rate * duration)
            
            sound_data = []
            for i in range(samples):
                t = i / sample_rate
                
                # Create mechanical drilling sound with multiple frequencies
                drill_freq1 = 120 + math.sin(t * 30) * 20  # Base drill frequency with variation
                drill_freq2 = 240 + math.sin(t * 45) * 15  # Higher harmonic
                
                # Add mechanical noise and vibration
                vibration = math.sin(2 * math.pi * drill_freq1 * t) * 0.3
                harmonic = math.sin(2 * math.pi * drill_freq2 * t) * 0.2
                noise = random.uniform(-0.1, 0.1)  # Mechanical noise
                
                # Combine components
                combined = (vibration + harmonic + noise) * 0.25
                
                # Convert to 16-bit
                sample = int(combined * 32767)
                sample = max(-32768, min(32767, sample))
                sound_data.extend([sample, sample])
            
            sound_bytes = b''.join(sample.to_bytes(2, 'little', signed=True) for sample in sound_data)
            return pygame.mixer.Sound(buffer=sound_bytes)
        except:
            return None
    
    def _create_laser_sound(self):
        """Create laser beam sound effect"""
        try:
            sample_rate = 22050
            duration = 0.4  # Laser firing duration
            samples = int(sample_rate * duration)
            
            sound_data = []
            for i in range(samples):
                t = i / sample_rate
                
                # Create sci-fi laser sound with frequency sweep
                base_freq = 800 - (t / duration) * 400  # Sweep from 800Hz to 400Hz
                modulation_freq = 50  # Fast modulation for laser effect
                
                # Main laser tone with modulation
                laser_tone = math.sin(2 * math.pi * base_freq * t) * 0.4
                modulation = 1 + 0.3 * math.sin(2 * math.pi * modulation_freq * t)
                
                # Add high-frequency sizzle
                sizzle_freq = 2000 + random.uniform(-200, 200)
                sizzle = math.sin(2 * math.pi * sizzle_freq * t) * 0.1 * random.uniform(0.5, 1.0)
                
                # Fade out over time
                amplitude = 1.0 - (t / duration) * 0.7
                
                combined = (laser_tone * modulation + sizzle) * amplitude * 0.3
                
                # Convert to 16-bit
                sample = int(combined * 32767)
                sample = max(-32768, min(32767, sample))
                sound_data.extend([sample, sample])
            
            sound_bytes = b''.join(sample.to_bytes(2, 'little', signed=True) for sample in sound_data)
            return pygame.mixer.Sound(buffer=sound_bytes)
        except:
            return None
    
    def _create_torch_sound(self):
        """Create torch/fire crackling sound effect"""
        try:
            sample_rate = 22050
            duration = 0.5  # Fire crackling duration
            samples = int(sample_rate * duration)
            
            sound_data = []
            for i in range(samples):
                t = i / sample_rate
                
                # Create fire crackling with random pops and hiss
                # Low-frequency base fire sound
                fire_base = math.sin(2 * math.pi * 80 * t) * 0.2
                
                # Random crackling pops
                if random.random() < 0.02:  # 2% chance per sample for pop
                    pop_intensity = random.uniform(0.3, 0.8)
                    pop_freq = random.uniform(200, 800)
                    pop = math.sin(2 * math.pi * pop_freq * t) * pop_intensity
                else:
                    pop = 0
                
                # High-frequency hiss
                hiss = random.uniform(-0.15, 0.15)
                
                # Combine components
                combined = fire_base + pop + hiss
                
                # Add slight amplitude variation for natural fire sound
                amplitude_variation = 0.8 + 0.2 * math.sin(2 * math.pi * 5 * t)
                combined *= amplitude_variation * 0.25
                
                # Convert to 16-bit
                sample = int(combined * 32767)
                sample = max(-32768, min(32767, sample))
                sound_data.extend([sample, sample])
            
            sound_bytes = b''.join(sample.to_bytes(2, 'little', signed=True) for sample in sound_data)
            return pygame.mixer.Sound(buffer=sound_bytes)
        except:
            return None
        
    def handle_event(self, event, player_id=None):
        """Handle input events with new control scheme"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)

            # Tool cycling and player-specific keys
            if player_id == 1:
                # Q/E cycle tools backward/forward
                if event.key == pygame.K_q:
                    self.current_tool_index = (self.current_tool_index - 1) % len(self.tools)
                    self.current_tool = self.tools[self.current_tool_index]
                elif event.key == pygame.K_e:
                    self.current_tool_index = (self.current_tool_index + 1) % len(self.tools)
                    self.current_tool = self.tools[self.current_tool_index]

                # Jump
                if event.key == pygame.K_SPACE:
                    if self.on_ground and self.can_jump:
                        self.vel_y = JUMP_VELOCITY
                        self.on_ground = False
                        self.can_jump = False

                # Use tool (F)
                if event.key == pygame.K_f:
                    if self.current_tool == "dynamite":
                        if self.dynamite_count > 0:
                            self.charging_power = True
                            self.charge_start_time = time.time()
                            self.power_level = 0
                        else:
                            pass  # No dynamite
                    else:
                        self._use_tool(self.cursor_x, self.cursor_y)

            elif player_id == 2:
                # , and - cycle tools for player 2
                if event.key == pygame.K_COMMA:
                    self.current_tool_index = (self.current_tool_index - 1) % len(self.tools)
                    self.current_tool = self.tools[self.current_tool_index]
                elif event.key == pygame.K_MINUS:
                    self.current_tool_index = (self.current_tool_index + 1) % len(self.tools)
                    self.current_tool = self.tools[self.current_tool_index]

                # Jump (Right Ctrl)
                if event.key == pygame.K_RCTRL:
                    if self.on_ground and self.can_jump:
                        self.vel_y = JUMP_VELOCITY
                        self.on_ground = False
                        self.can_jump = False

                # Use tool (.)
                if event.key == pygame.K_PERIOD:
                    if self.current_tool == "dynamite":
                        if self.dynamite_count > 0:
                            self.charging_power = True
                            self.charge_start_time = time.time()
                            self.power_level = 0
                        else:
                            pass  # No dynamite
                    else:
                        self._use_tool(self.cursor_x, self.cursor_y)

        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)

            # Dynamite release handling
            if player_id == 1 and event.key == pygame.K_f and self.charging_power:
                self.charging_power = False
                if self.current_tool == "dynamite" and self.dynamite_count > 0:
                    target_x, target_y = self._calculate_tool_target_position()
                    self._throw_dynamite(target_x, target_y, self.power_level)
                self.power_level = 0
            elif player_id == 2 and event.key == pygame.K_PERIOD and self.charging_power:
                self.charging_power = False
                if self.current_tool == "dynamite" and self.dynamite_count > 0:
                    target_x, target_y = self._calculate_tool_target_position()
                    self._throw_dynamite(target_x, target_y, self.power_level)
                self.power_level = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._use_tool(self.cursor_x, self.cursor_y)

        elif event.type == pygame.MOUSEMOTION:
            self.cursor_x, self.cursor_y = pygame.mouse.get_pos()
                
    def _use_tool(self, target_x, target_y):
        """Use the current tool at the target position"""
        # Calculate distance from worm to target
        distance = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
        
        # Check gas requirement for torch
        if self.current_tool == "torch":
            if self.gas < TORCH_GAS_COST:
                print("Not enough gas for torch! Find gas bottles.")
                return
        
        # Different tools have different behaviors
        if self.current_tool == "drill":
            # Drill always works directly below the worm, no range or target restrictions
            self.dig_request = (self.x, self.y + WORM_RADIUS, self.current_tool)
            # Play drill sound
            if hasattr(self, 'drill_sound') and self.drill_sound:
                self.drill_sound.play()
                
        elif self.current_tool == "torch":
            # Torch creates a cone using the smooth interpolated direction
            if self.gas >= TORCH_GAS_COST:
                direction_angle = self.tool_current_angle
                
                # Dig starts from worm position, not target position
                self.dig_request = (self.x, self.y, self.current_tool, direction_angle)
                self.gas -= TORCH_GAS_COST  # Consume gas
                
                # Create fire effects
                self._create_fire_particles(self.x, self.y, TORCH_CONE_ANGLE, direction_angle)
                self.torch_fire_timer = 1.0  # Fire effect duration
                
                # Play torch sound
                if hasattr(self, 'torch_sound') and self.torch_sound:
                    self.torch_sound.play()
                
            else:
                pass  # Not enough gas for torch
                
        elif self.current_tool == "laser":
            # Check laser battery before firing
            if self.laser_battery >= 10.0:  # Need at least 10% battery to fire
                target_x, target_y = self._calculate_tool_target_position()
                self.dig_request = (target_x, target_y, self.current_tool, "line_from_worm")
                
                # Consume battery and track usage
                current_time = time.time()
                self.laser_battery -= 10.0  # Each shot costs 10% battery
                
                # Track rapid usage for cooldown system
                if current_time - self.laser_last_use_time < 2.0:  # If used within 2 seconds
                    self.laser_use_count += 1
                else:
                    self.laser_use_count = 1  # Reset if enough time passed
                
                self.laser_last_use_time = current_time
                
                # Start cooldown if used too rapidly
                if self.laser_use_count >= 10:
                    self.laser_cooldown_timer = 5.0  # 5 second cooldown
                    self.laser_use_count = 0
                
                # Play laser sound
                if hasattr(self, 'laser_sound') and self.laser_sound:
                    self.laser_sound.play()
            else:
                pass  # Not enough battery
            
        elif self.current_tool == "dynamite":
            # Dynamite can be thrown anywhere (within reasonable range)
            max_throw_distance = 200  # Pixels
            if distance <= max_throw_distance:
                self.dig_request = (target_x, target_y, self.current_tool)
            else:
                pass  # Too far to throw dynamite
                
    def _calculate_tool_target_position(self):
        """Calculate target position for directional tools based on current smoothed angle"""
        # Use different distances for different tools
        if self.current_tool == "laser":
            distance = 400  # Four times longer for laser
        else:
            distance = 100  # Default distance for other tools
            
        target_x = self.x + math.cos(self.tool_current_angle) * distance
        target_y = self.y + math.sin(self.tool_current_angle) * distance
        
        return target_x, target_y
    
    def _update_tool_direction(self, dt):
        """Update tool direction with smooth interpolation based on key hold duration"""
        # Determine which keys to check based on player
        if hasattr(self, 'player_id') and self.player_id == 1:
            # Player 1 uses W/S for aiming
            up_key = pygame.K_w
            down_key = pygame.K_s
            # Player 1 doesn't have left/right aiming keys in the new scheme
            left_key = None
            right_key = None
        elif hasattr(self, 'player_id') and self.player_id == 2:
            # Player 2 uses Up/Down for aiming
            up_key = pygame.K_UP
            down_key = pygame.K_DOWN
            # Player 2 doesn't have left/right aiming keys in the new scheme
            left_key = None
            right_key = None
        else:
            # Fallback for worms without player_id
            up_key = pygame.K_UP
            down_key = pygame.K_DOWN
            left_key = pygame.K_LEFT
            right_key = pygame.K_RIGHT
        
        # Update key timers for available keys
        any_direction_key_pressed = False
        
        # Check up/down keys
        up_strength = 0.0
        down_strength = 0.0
        left_strength = 0.0
        right_strength = 0.0
        
        if up_key and up_key in self.keys_pressed:
            self.direction_key_timers[up_key] = min(self.max_direction_time, 
                                               self.direction_key_timers.get(up_key, 0.0) + dt)
            up_strength = self.direction_key_timers[up_key] / self.max_direction_time
            any_direction_key_pressed = True
        elif up_key:
            self.direction_key_timers[up_key] = 0.0
            
        if down_key and down_key in self.keys_pressed:
            self.direction_key_timers[down_key] = min(self.max_direction_time, 
                                                 self.direction_key_timers.get(down_key, 0.0) + dt)
            down_strength = self.direction_key_timers[down_key] / self.max_direction_time
            any_direction_key_pressed = True
        elif down_key:
            self.direction_key_timers[down_key] = 0.0
            
        # Check left/right keys if available (fallback mode)
        if left_key and left_key in self.keys_pressed:
            self.direction_key_timers[left_key] = min(self.max_direction_time, 
                                                 self.direction_key_timers.get(left_key, 0.0) + dt)
            left_strength = self.direction_key_timers[left_key] / self.max_direction_time
            any_direction_key_pressed = True
        elif left_key:
            self.direction_key_timers[left_key] = 0.0
            
        if right_key and right_key in self.keys_pressed:
            self.direction_key_timers[right_key] = min(self.max_direction_time, 
                                                  self.direction_key_timers.get(right_key, 0.0) + dt)
            right_strength = self.direction_key_timers[right_key] / self.max_direction_time
            any_direction_key_pressed = True
        elif right_key:
            self.direction_key_timers[right_key] = 0.0
        
        # Only update target angle if keys are being pressed
        if any_direction_key_pressed:
            # Calculate direction vector based on key strengths
            total_input = up_strength + down_strength + left_strength + right_strength
            
            if total_input > 0.05:  # If there's any significant input
                # Use direct angle modification for smoother control at all angles
                angle_speed = 3.0 * dt  # Base rotation speed (radians per second)
                
                # Calculate rotation direction based on input
                horizontal_input = right_strength - left_strength
                vertical_input = down_strength - up_strength
                
                # Adjust vertical input based on facing direction
                # When facing left, invert vertical input to maintain intuitive controls
                if self.facing_direction < 0:  # Facing left
                    vertical_input = -vertical_input
                
                # Apply rotation based on input
                if abs(horizontal_input) > 0.01:
                    self.tool_target_angle += horizontal_input * angle_speed
                
                if abs(vertical_input) > 0.01:
                    self.tool_target_angle += vertical_input * angle_speed
                
                # Normalize angle to stay within -π to π range
                while self.tool_target_angle > math.pi:
                    self.tool_target_angle -= 2 * math.pi
                while self.tool_target_angle < -math.pi:
                    self.tool_target_angle += 2 * math.pi
                
                # Constrain angle based on facing direction
                self.tool_target_angle = self._constrain_angle_to_facing_direction(self.tool_target_angle)
                
                self.angle_locked = True  # Lock the angle once set by user input
        else:
            # No keys pressed - keep current target angle (don't change it)
            # This ensures the indicator stays exactly where it was when keys were released
            pass
        
        # Update facing direction flip logic
        if not any_direction_key_pressed:
            if not self.angle_locked:
                # Set default facing direction if never manually controlled
                # Right = 0°, Left = 180° (π radians)
                self.tool_target_angle = 0 if self.facing_direction > 0 else math.pi
            else:
                # Always flip the indicator to match worm facing direction when not actively aiming
                current_angle_magnitude = math.sqrt(
                    math.sin(self.tool_current_angle)**2 + math.cos(self.tool_current_angle)**2
                )
                current_vertical_component = math.sin(self.tool_current_angle)
                
                # Flip horizontal component to match facing direction
                if self.facing_direction > 0:  # Worm facing right
                    new_horizontal = abs(math.cos(self.tool_current_angle))
                else:  # Worm facing left  
                    new_horizontal = -abs(math.cos(self.tool_current_angle))
                
                # Update target angle to maintain vertical component but flip horizontal
                self.tool_target_angle = math.atan2(current_vertical_component, new_horizontal)
        
        # Smooth interpolation toward target angle (only if target differs from current)
        angle_diff = self.tool_target_angle - self.tool_current_angle
        
        # Handle angle wrapping (shortest path)
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Smooth interpolation
        max_change = self.angle_interpolation_speed * dt
        if abs(angle_diff) <= max_change:
            self.tool_current_angle = self.tool_target_angle
        else:
            self.tool_current_angle += max_change * (1 if angle_diff > 0 else -1)
        
        # Normalize angle
        while self.tool_current_angle > math.pi:
            self.tool_current_angle -= 2 * math.pi
        while self.tool_current_angle < -math.pi:
            self.tool_current_angle += 2 * math.pi
    
    def _constrain_angle_to_facing_direction(self, angle):
        """Constrain angle based on worm's facing direction"""
        if self.facing_direction > 0:  # Facing right
            # Allow angles from -90° to +90° (270° to 90° in 0-360° system)
            # In radians: -π/2 to π/2
            if angle > math.pi / 2:
                angle = math.pi / 2
            elif angle < -math.pi / 2:
                angle = -math.pi / 2
        else:  # Facing left
            # Allow angles from 90° to 270° (π/2 to π and -π to -π/2)
            # In radians: π/2 to π and -π to -π/2
            if angle > -math.pi / 2 and angle < math.pi / 2:
                # If angle is in right-facing zone, clamp to nearest boundary
                if angle >= 0:
                    angle = math.pi / 2
                else:
                    angle = -math.pi / 2
        
        return angle
    
    def _mirror_angle_for_direction_change(self):
        """Mirror the angle's X component when facing direction changes, keeping Y the same"""
        if self.angle_locked:
            # Get current angle components
            current_x = math.cos(self.tool_current_angle)
            current_y = math.sin(self.tool_current_angle)
            
            # Mirror the X component
            mirrored_x = -current_x
            
            # Calculate new angle with mirrored X but same Y
            new_angle = math.atan2(current_y, mirrored_x)
            
            # Apply directional constraints
            new_angle = self._constrain_angle_to_facing_direction(new_angle)
            
            # Set both target and current angle immediately for instant mirroring
            self.tool_target_angle = new_angle
            self.tool_current_angle = new_angle
    
    def _throw_dynamite(self, target_x, target_y, power):
        """Throw dynamite towards target with given power"""
        if self.dynamite_count <= 0:
            return
            
        # Create thrown dynamite
        dynamite = ThrownDynamite(self.x, self.y, target_x, target_y, power)
        self.thrown_dynamites.append(dynamite)
        self.dynamite_count -= 1
        
        power_percent = (power / MAX_POWER) * 100
        
    def _calculate_trajectory_points(self, start_x, start_y, angle, power):
        """Calculate trajectory points for dynamite throw preview"""
        points = []
        
        # Calculate velocity to match ThrownDynamite physics
        base_speed = 200  # Base throw speed
        speed_multiplier = 0.5 + (power / 100) * 1.5  # 0.5x to 2x speed
        velocity = base_speed * speed_multiplier
        
        # Set velocity components with same logic as ThrownDynamite
        vel_x = math.cos(angle) * velocity
        vel_y = math.sin(angle) * velocity - 50  # Slight upward bias for arc
        
        # Simulate trajectory with gravity
        x, y = start_x, start_y
        dt = 0.05  # Smaller time step for smoother preview
        
        for _ in range(100):  # Calculate up to 100 points
            points.append((x, y))
            
            # Update position
            x += vel_x * dt
            y += vel_y * dt
            
            # Apply gravity
            vel_y += GRAVITY * dt
            
            # Stop if we hit the ground (rough check)
            if y > MAP_HEIGHT * TILE_SIZE - 50:
                break
                
        return points
        
    def _create_fire_particles(self, center_x, center_y, cone_angle, direction_angle):
        """Create fire particles for torch effect - simplified for stability"""
        try:
            num_particles = 15  # Back to original safe amount
            for i in range(num_particles):
                # Random position within cone
                angle_offset = (random.random() - 0.5) * math.radians(cone_angle)
                particle_angle = direction_angle + angle_offset
                distance = random.random() * TORCH_RADIUS  # Back to original TORCH_RADIUS
                
                particle_x = center_x + math.cos(particle_angle) * distance
                particle_y = center_y + math.sin(particle_angle) * distance
                
                # Simple, safe particle properties
                particle = {
                    'x': float(particle_x),
                    'y': float(particle_y),
                    'life': 0.5 + random.random() * 0.5,  # 0.5-1.0 seconds
                    'max_life': 1.0,
                    'vel_x': (random.random() - 0.5) * 20,
                    'vel_y': (random.random() - 0.5) * 20 - 10,
                    'size': 2 + random.random() * 3
                }
                self.fire_particles.append(particle)
        except Exception as e:
            # If anything goes wrong, just skip particle creation
            pass
            
    def _update_fire_particles(self, dt):
        """Update fire particle positions and lifetimes - simplified for stability"""
        if not self.fire_particles:
            return
            
        try:
            # Process particles safely
            active_particles = []
            for particle in self.fire_particles:
                if particle.get('life', 0) > 0:
                    # Simple updates
                    particle['x'] += particle['vel_x'] * dt
                    particle['y'] += particle['vel_y'] * dt
                    particle['life'] -= dt
                    particle['vel_y'] += 100 * dt  # Simple gravity
                    active_particles.append(particle)
            
            self.fire_particles = active_particles
        except Exception as e:
            # If there's any error, clear particles safely
            self.fire_particles = []
                
    def _dig_laser_line(self, target_x, target_y, terrain):
        """Dig a line from worm position to target for laser"""
        start_x, start_y = int(self.x), int(self.y)
        end_x, end_y = int(target_x), int(target_y)
        
        # Start laser firing effect
        self.laser_firing = True
        self.laser_fire_timer = 0.3  # Laser beam visible for 0.3 seconds
        self.laser_start_pos = (start_x, start_y)
        self.laser_end_pos = (end_x, end_y)
        
        # Calculate points along the line using Bresenham's line algorithm (simplified)
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        steps = max(dx, dy)
        
        if steps == 0:
            return
            
        x_step = (end_x - start_x) / steps
        y_step = (end_y - start_y) / steps
        
        # Dig along the line with laser width
        laser_radius = LASER_WIDTH // 2
        for i in range(steps + 1):
            x = start_x + int(i * x_step)
            y = start_y + int(i * y_step)
            # Dig a wider area around each point for more laser effect
            terrain.dig(x, y, laser_radius, "laser")
        
    def update(self, dt, terrain):
        """Update worm position and handle interactions"""
        # Update laser battery system
        if self.laser_cooldown_timer > 0:
            self.laser_cooldown_timer -= dt
        else:
            # Recharge battery at 10% per second when not in cooldown
            if self.laser_battery < 100.0:
                self.laser_battery = min(100.0, self.laser_battery + 10.0 * dt)
        
        # Handle horizontal movement input based on player
        horizontal_input = 0
        
        # Player 1 uses A/D
        if pygame.K_a in self.keys_pressed:
            horizontal_input -= 1
        if pygame.K_d in self.keys_pressed:
            horizontal_input += 1
            
        # Player 2 uses Left/Right arrows
        if pygame.K_LEFT in self.keys_pressed:
            horizontal_input -= 1
        if pygame.K_RIGHT in self.keys_pressed:
            horizontal_input += 1
            
        # Apply horizontal movement
        if horizontal_input != 0:
            self.vel_x = horizontal_input * WORM_SPEED
            # Update facing direction based on movement and handle angle mirroring
            old_facing_direction = self.facing_direction
            self.facing_direction = horizontal_input
            
            # If facing direction changed, mirror the targeting angle
            if old_facing_direction != self.facing_direction:
                self._mirror_angle_for_direction_change()
        else:
            # Apply friction when no input
            if self.on_ground:
                self.vel_x *= GROUND_FRICTION
            else:
                self.vel_x *= 0.95  # Air resistance
                
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY * dt
            # Limit falling speed
            if self.vel_y > TERMINAL_VELOCITY:
                self.vel_y = TERMINAL_VELOCITY
        
        # Handle cursor movement - Player-specific aiming
        # Player 1 uses W/S, Player 2 uses Up/Down
        cursor_vel_x = 0
        cursor_vel_y = 0
        
        # Player-specific cursor movement
        if hasattr(self, 'player_id'):
            if self.player_id == 1:
                # Player 1: W/S for aiming
                if pygame.K_w in self.keys_pressed:
                    cursor_vel_y -= self.cursor_speed
                if pygame.K_s in self.keys_pressed:
                    cursor_vel_y += self.cursor_speed
            elif self.player_id == 2:
                # Player 2: Up/Down for aiming
                if pygame.K_UP in self.keys_pressed:
                    cursor_vel_y -= self.cursor_speed
                if pygame.K_DOWN in self.keys_pressed:
                    cursor_vel_y += self.cursor_speed
        else:
            # Fallback: if no player_id, allow both control schemes
            if pygame.K_w in self.keys_pressed:
                cursor_vel_y -= self.cursor_speed
            if pygame.K_s in self.keys_pressed:
                cursor_vel_y += self.cursor_speed
            if pygame.K_UP in self.keys_pressed:
                cursor_vel_y -= self.cursor_speed
            if pygame.K_DOWN in self.keys_pressed:
                cursor_vel_y += self.cursor_speed
            
        # Update cursor position
        self.cursor_x += cursor_vel_x * dt
        self.cursor_y += cursor_vel_y * dt
        
        # Keep cursor within screen bounds
        self.cursor_x = max(0, min(SCREEN_WIDTH, self.cursor_x))
        self.cursor_y = max(0, min(SCREEN_HEIGHT, self.cursor_y))
            
        # Update power charging
        if self.charging_power:
            elapsed = time.time() - self.charge_start_time
            self.power_level = min(elapsed * POWER_CHARGE_RATE, MAX_POWER)
            
        # Update tool direction smoothly
        self._update_tool_direction(dt)
        
        # Update thrown dynamites
        for dynamite in self.thrown_dynamites[:]:  # Copy list to avoid modification issues
            if dynamite.update(dt, terrain):
                # Dynamite exploded
                dyn_x, dyn_y = dynamite.get_position()
                terrain.dig(dyn_x, dyn_y, DYNAMITE_RADIUS, "dynamite")
                self.thrown_dynamites.remove(dynamite)
                
        # Update torch fire effects
        if self.torch_fire_timer > 0:
            self.torch_fire_timer -= dt
            self._update_fire_particles(dt)
            
        # Update laser firing effects
        if self.laser_fire_timer > 0:
            self.laser_fire_timer -= dt
            if self.laser_fire_timer <= 0:
                self.laser_firing = False
        
        # Apply physics-based movement with collision detection
        self._apply_physics_movement(dt, terrain)
        
        # Check for item collection
        self._check_item_collection(terrain)
        
        # Keep worm within horizontal screen bounds
        self.x = max(WORM_RADIUS, min(SCREEN_WIDTH - WORM_RADIUS, self.x))
        
        # Handle vertical screen wrapping - if worm goes below bottom, wrap to top
        if self.y > SCREEN_HEIGHT + WORM_RADIUS:
            # Wrap to a safe position in the sky area, below the UI but above terrain
            wrap_y_position = UI_HEIGHT + 50  # Just below the UI area with some margin
            self.x = max(WORM_RADIUS, min(SCREEN_WIDTH - WORM_RADIUS, self.x))  # Keep within horizontal bounds
            self.y = wrap_y_position
            
            # Completely reset physics state when wrapping
            self.vel_y = 50  # Gentle downward velocity
            self.vel_x = 0
            self.on_ground = False
            self.can_jump = False
            
            player_id = getattr(self, 'player_id', 'Unknown')
        
        # Very minimal top boundary check - only prevent going completely off screen
        if self.y < -50:  # Allow some margin above screen
            self.y = -50
            self.vel_y = max(0, self.vel_y)
        
        # Update body segments for worm-like movement
        self.segment_update_timer += dt
        if self.segment_update_timer > 0.1:  # Update segments every 0.1 seconds
            self._update_body_segments()
            self.segment_update_timer = 0
        
        # Handle tool usage
        if hasattr(self, 'dig_request'):
            if len(self.dig_request) == 4:
                if self.dig_request[3] == "line_from_worm":
                    # Special handling for laser
                    target_x, target_y, tool, _ = self.dig_request
                    self._dig_laser_line(target_x, target_y, terrain)
                else:
                    # Torch with direction angle
                    target_x, target_y, tool, direction_angle = self.dig_request
                    terrain.dig(target_x, target_y, TORCH_RANGE, tool, direction_angle)
            else:
                # Regular digging for other tools
                target_x, target_y, tool = self.dig_request
                radius = self._get_tool_radius(tool)
                terrain.dig(target_x, target_y, radius, tool)
            del self.dig_request
            
        # Check for items (gas bottles) near the worm
        found_items = terrain.check_for_items(self.x, self.y, WORM_RADIUS + 5)
        for item_pos, item_type in found_items:
            if item_type == 1:  # ItemType.GAS_BOTTLE
                self.gas = min(self.gas + GAS_BOTTLE_AMOUNT, MAX_GAS)
                print(f"Found gas bottle! Gas: {self.gas}/{MAX_GAS}")
            
    def _apply_physics_movement(self, dt, terrain):
        """Apply physics-based movement with proper collision detection and slope climbing"""
        # Store old position
        old_x, old_y = self.x, self.y
        
        # Calculate new position
        new_x = self.x + self.vel_x * dt
        new_y = self.y + self.vel_y * dt
        
        # Check horizontal movement with slope climbing
        horizontal_blocked = False
        if not self._check_collision(new_x, self.y, terrain):
            # Normal horizontal movement - no obstacle
            self.x = new_x
        else:
            # Try slope climbing - check if we can move up a bit to climb over
            slope_climb_attempted = False
            if abs(self.vel_x) > 0:  # Only try if moving horizontally
                # Try climbing up to climb a slope
                max_climb_height = WORM_RADIUS  # Maximum height to try climbing
                climb_step = 4  # Check in 4-pixel increments
                
                for climb_height in range(climb_step, int(max_climb_height) + climb_step, climb_step):
                    test_y = self.y - climb_height
                    # Check if we can move horizontally at this higher position
                    if not self._check_collision(new_x, test_y, terrain):
                        # Check if this slope isn't too steep
                        slope_angle = math.degrees(math.atan2(climb_height, abs(self.vel_x * dt)))
                        if slope_angle <= MAX_SLOPE_ANGLE:
                            # We can climb this slope!
                            self.x = new_x
                            self.y = test_y
                            slope_climb_attempted = True
                            break
                            
            if not slope_climb_attempted:
                # Hit a wall horizontally that we can't climb, stop horizontal movement
                horizontal_blocked = True
                self.vel_x = 0
            
        # Check vertical movement
        if not self._check_collision(self.x, new_y, terrain):
            self.y = new_y
            # Check if we were on ground and are now falling
            if self.on_ground and self.vel_y > 0:
                self.on_ground = False
        else:
            # Hit something vertically
            if self.vel_y > 0:
                # Hit ground while falling
                self.on_ground = True
                self.can_jump = True
                self.vel_y = 0
                
                # Snap to ground level to prevent sinking
                # But don't do this correction if we're near the top of the screen (wrapped worms)
                if self.y > UI_HEIGHT:  # Only apply ground snapping if we're well below the top
                    while self._check_collision(self.x, self.y, terrain) and self.y > WORM_RADIUS:
                        self.y -= 1
                    
            elif self.vel_y < 0:
                # Hit ceiling while jumping
                self.vel_y = 0
                
        # Additional ground check - if worm is not colliding below, they're not on ground
        # But also check if we're on a slope
        if self.on_ground and not self._check_ground_below(terrain):
            # Check if we're on a slope that we can still stand on
            if not self._is_on_climbable_slope(terrain):
                self.on_ground = False
            
    def _check_ground_below(self, terrain):
        """Check if there's solid ground directly below the worm"""
        # Check a few pixels below the worm's bottom
        ground_check_distance = 3  # Reduced distance for more reliable detection
        check_y = self.y + WORM_RADIUS + ground_check_distance
        
        # Check multiple points across the worm's width
        ground_found = False
        for offset in [-WORM_RADIUS//2, -WORM_RADIUS//4, 0, WORM_RADIUS//4, WORM_RADIUS//2]:
            check_x = self.x + offset
            if terrain.is_solid(check_x, check_y):
                ground_found = True
                break
                
        # Also check if we're directly touching ground
        touching_ground = False
        for offset in [-WORM_RADIUS//2, 0, WORM_RADIUS//2]:
            check_x = self.x + offset
            check_y = self.y + WORM_RADIUS + 1  # Just one pixel below
            if terrain.is_solid(check_x, check_y):
                touching_ground = True
                break
                
        return ground_found or touching_ground
        
    def _is_on_climbable_slope(self, terrain):
        """Check if worm is standing on a slope it can stay on"""
        # Check ground contact points around the worm
        ground_contacts = []
        check_distance = WORM_RADIUS + 3
        
        # Check several points around the bottom of the worm
        for angle in range(45, 136, 15):  # Check angles from 45 to 135 degrees (bottom arc)
            rad = math.radians(angle)
            check_x = self.x + math.cos(rad) * check_distance
            check_y = self.y + math.sin(rad) * check_distance
            
            if terrain.is_solid(check_x, check_y):
                ground_contacts.append((check_x, check_y))
        
        # If we have at least 2 ground contact points, calculate slope
        if len(ground_contacts) >= 2:
            # Use the leftmost and rightmost contact points
            left_contact = min(ground_contacts, key=lambda p: p[0])
            right_contact = max(ground_contacts, key=lambda p: p[0])
            
            # Calculate slope angle
            dx = right_contact[0] - left_contact[0]
            dy = right_contact[1] - left_contact[1]
            
            if dx != 0:
                slope_angle = abs(math.degrees(math.atan2(dy, dx)))
                return slope_angle <= MAX_SLOPE_ANGLE
                
        return len(ground_contacts) > 0  # If we have any ground contact, assume we can stay
            
    def _check_collision(self, x, y, terrain):
        """Check if the worm would collide with terrain at the given position"""
        # Check multiple points around the worm's circumference
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            check_x = x + math.cos(rad) * WORM_RADIUS
            check_y = y + math.sin(rad) * WORM_RADIUS
            
            if terrain.is_solid(check_x, check_y):
                return True
        return False
        
    def _update_body_segments(self):
        """Update the body segments to follow the head"""
        # Move each segment to the position of the previous one
        for i in range(len(self.body_segments) - 1, 0, -1):
            self.body_segments[i] = self.body_segments[i - 1]
        # Head segment follows the actual worm position
        self.body_segments[0] = (self.x, self.y)
        
    def _get_tool_radius(self, tool):
        """Get the digging radius for a tool"""
        if tool == "drill":
            return DRILL_WIDTH // 2  # Return half-width as radius
        elif tool == "dynamite":
            return DYNAMITE_RADIUS
        elif tool == "torch":
            return TORCH_RADIUS
        elif tool == "laser":
            return LASER_WIDTH // 2  # Laser uses width/2 as radius
        return DRILL_WIDTH // 2  # Default
        
    def get_position(self):
        """Get current position as tuple"""
        return (self.x, self.y)
        
    def render(self, screen, camera_x, camera_y):
        """Render the worm and its indicators"""
        # Use the worm's individual color, or default if not set
        worm_color = getattr(self, 'color', WORM_COLOR)
        # Make body color slightly darker than head color
        body_color = tuple(max(0, c - 40) for c in worm_color)
        
        # Render worm segments
        for i, (x, y) in enumerate(self.body_segments):
            screen_x = x - camera_x
            screen_y = y - camera_y
            
            # Check if segment is visible on screen
            if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
                if i == 0:  # Head
                    pygame.draw.circle(screen, worm_color, (int(screen_x), int(screen_y)), WORM_RADIUS)
                    # Draw eyes
                    eye_offset = WORM_RADIUS // 3
                    pygame.draw.circle(screen, BLACK, (int(screen_x - eye_offset), int(screen_y - eye_offset)), 3)
                    pygame.draw.circle(screen, BLACK, (int(screen_x + eye_offset), int(screen_y - eye_offset)), 3)
                else:  # Body segments
                    segment_radius = WORM_RADIUS - (i * 2)
                    if segment_radius > 2:
                        pygame.draw.circle(screen, body_color, (int(screen_x), int(screen_y)), segment_radius)
        
        # Render fire particles for torch
        if self.current_tool == "torch" and self.fire_particles:
            for particle in self.fire_particles:
                screen_x = particle['x'] - camera_x
                screen_y = particle['y'] - camera_y
                if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                    alpha = int(255 * particle['life'])
                    color = (255, max(0, 255 - int(100 * (1 - particle['life']))), 0)
                    try:
                        # Create a surface for the particle with alpha
                        particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                        particle_surf.fill((*color, alpha))
                        screen.blit(particle_surf, (int(screen_x - 3), int(screen_y - 3)))
                    except:
                        # Fallback to regular circle if alpha blending fails
                        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 2)
        
        # Render laser beam when firing
        if self.laser_firing and self.laser_start_pos and self.laser_end_pos:
            start_screen_x = self.laser_start_pos[0] - camera_x
            start_screen_y = self.laser_start_pos[1] - camera_y
            end_screen_x = self.laser_end_pos[0] - camera_x
            end_screen_y = self.laser_end_pos[1] - camera_y
            
            # Draw multiple laser beam layers for effect
            laser_color = LASER_INDICATOR_COLOR
            laser_glow = (100, 100, 255)  # Light blue glow
            
            # Draw glow effect (thicker, lighter line)
            pygame.draw.line(screen, laser_glow, (int(start_screen_x), int(start_screen_y)), 
                           (int(end_screen_x), int(end_screen_y)), 8)
            # Draw main laser beam (thinner, brighter line)
            pygame.draw.line(screen, laser_color, (int(start_screen_x), int(start_screen_y)), 
                           (int(end_screen_x), int(end_screen_y)), 4)
            # Draw core beam (very thin, white line)
            pygame.draw.line(screen, WHITE, (int(start_screen_x), int(start_screen_y)), 
                           (int(end_screen_x), int(end_screen_y)), 2)
        
        # Render tool indicators
        if self.current_tool == "drill":
            # Drill indicator: vertical rectangle completely below worm
            head_x, head_y = self.body_segments[0]
            indicator_x = head_x - camera_x
            indicator_y = head_y - camera_y
            
            drill_rect = pygame.Rect(
                indicator_x - DRILL_WIDTH // 2,
                indicator_y + WORM_RADIUS,  # Start below the worm
                DRILL_WIDTH,
                DRILL_DEPTH
            )
            pygame.draw.rect(screen, DRILL_INDICATOR_COLOR, drill_rect, 2)
            
        elif self.current_tool == "torch":
            # Torch indicator: cone shape using smooth interpolated angle
            head_x, head_y = self.body_segments[0]
            indicator_x = head_x - camera_x
            indicator_y = head_y - camera_y
            
            # Use smoothed angle
            target_angle = self.tool_current_angle
            
            # Calculate cone points
            cone_length = TORCH_RANGE
            cone_angle = math.radians(TORCH_CONE_ANGLE)
            
            # Base angles for the cone
            left_angle = target_angle - cone_angle / 2
            right_angle = target_angle + cone_angle / 2
            
            # Calculate cone points
            cone_tip_x = indicator_x + cone_length * math.cos(target_angle)
            cone_tip_y = indicator_y + cone_length * math.sin(target_angle)
            
            left_edge_x = indicator_x + cone_length * math.cos(left_angle)
            left_edge_y = indicator_y + cone_length * math.sin(left_angle)
            
            right_edge_x = indicator_x + cone_length * math.cos(right_angle)
            right_edge_y = indicator_y + cone_length * math.sin(right_angle)
            
            # Draw cone outline
            cone_points = [
                (indicator_x, indicator_y),
                (left_edge_x, left_edge_y),
                (cone_tip_x, cone_tip_y),
                (right_edge_x, right_edge_y)
            ]
            
            # Draw filled cone with transparency
            try:
                cone_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(cone_surf, (*TORCH_INDICATOR_COLOR, 50), cone_points)
                screen.blit(cone_surf, (0, 0))
            except:
                pygame.draw.polygon(screen, TORCH_INDICATOR_COLOR, cone_points)
            
            # Draw cone outline
            pygame.draw.polygon(screen, TORCH_INDICATOR_COLOR, cone_points, 2)
            
        elif self.current_tool == "dynamite":
            # Dynamite indicator: power charging bar and trajectory
            head_x, head_y = self.body_segments[0]
            indicator_x = head_x - camera_x
            indicator_y = head_y - camera_y
            
            # Use smoothed angle
            target_angle = self.tool_current_angle
            
            # Power charging bar
            if self.charging_power:
                bar_width = 60
                bar_height = 8
                bar_x = indicator_x - bar_width // 2
                bar_y = indicator_y - 30
                
                # Background bar
                pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
                
                # Power level bar
                power_width = int((self.power_level / 100) * (bar_width - 2))
                power_color = (255, int(255 * (1 - self.power_level / 100)), 0)  # Red to yellow
                pygame.draw.rect(screen, power_color, (bar_x + 1, bar_y + 1, power_width, bar_height - 2))
                
                # Bar outline
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Trajectory line if power > 0
            if self.power_level > 0:
                trajectory_points = self._calculate_trajectory_points(head_x, head_y, target_angle, self.power_level)
                if len(trajectory_points) > 1:
                    screen_points = [(x - camera_x, y - camera_y) for x, y in trajectory_points]
                    # Filter points that are on screen
                    visible_points = [(x, y) for x, y in screen_points if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT]
                    if len(visible_points) > 1:
                        pygame.draw.lines(screen, DYNAMITE_INDICATOR_COLOR, False, visible_points, 2)
            
            # Direction indicator arrow (always visible)
            arrow_length = 40
            arrow_end_x = indicator_x + math.cos(target_angle) * arrow_length
            arrow_end_y = indicator_y + math.sin(target_angle) * arrow_length
            
            # Draw direction line
            pygame.draw.line(screen, DYNAMITE_INDICATOR_COLOR, 
                           (int(indicator_x), int(indicator_y)), 
                           (int(arrow_end_x), int(arrow_end_y)), 3)
            
            # Draw arrowhead
            arrowhead_size = 8
            arrowhead_angle = 0.5  # radians for arrowhead spread
            
            # Calculate arrowhead points
            left_angle = target_angle + math.pi - arrowhead_angle
            right_angle = target_angle + math.pi + arrowhead_angle
            
            left_x = arrow_end_x + math.cos(left_angle) * arrowhead_size
            left_y = arrow_end_y + math.sin(left_angle) * arrowhead_size
            right_x = arrow_end_x + math.cos(right_angle) * arrowhead_size
            right_y = arrow_end_y + math.sin(right_angle) * arrowhead_size
            
            # Draw arrowhead triangle
            arrowhead_points = [
                (int(arrow_end_x), int(arrow_end_y)),
                (int(left_x), int(left_y)),
                (int(right_x), int(right_y))
            ]
            pygame.draw.polygon(screen, DYNAMITE_INDICATOR_COLOR, arrowhead_points)
                        
        elif self.current_tool == "laser":
            # Laser indicator: small red targeting line showing where laser will hit
            head_x, head_y = self.body_segments[0]
            indicator_x = head_x - camera_x
            indicator_y = head_y - camera_y
            
            # Calculate target position using tool targeting system (like dynamite)
            target_x, target_y = self._calculate_tool_target_position()
            target_screen_x = target_x - camera_x
            target_screen_y = target_y - camera_y
            
            # Draw small red targeting laser (preview)
            targeting_color = (255, 100, 100)  # Light red
            pygame.draw.line(screen, targeting_color, (int(indicator_x), int(indicator_y)), 
                           (int(target_screen_x), int(target_screen_y)), 2)
            
            # Small target circle at end point
            pygame.draw.circle(screen, targeting_color, (int(target_screen_x), int(target_screen_y)), 6, 2)
            pygame.draw.circle(screen, WHITE, (int(target_screen_x), int(target_screen_y)), 3, 1)
    
    def _check_item_collection(self, terrain):
        """Check if worm is touching any collectible items and collect them"""
        # Convert worm position to tile coordinates, accounting for terrain offset
        terrain_y_offset = UI_HEIGHT  # Top space offset
        adjusted_y = self.y - terrain_y_offset  # Subtract offset to get terrain-relative coordinates
        
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(adjusted_y // TILE_SIZE)
        
        # Check surrounding tiles for items
        collection_radius = 1  # Check tiles around the worm
        for dy in range(-collection_radius, collection_radius + 1):
            for dx in range(-collection_radius, collection_radius + 1):
                check_x = tile_x + dx
                check_y = tile_y + dy
                
                # Make sure coordinates are valid
                if (0 <= check_x < terrain.width and 0 <= check_y < terrain.height):
                    # Check if there's an item at this position
                    item_key = (check_x, check_y)
                    if item_key in terrain.items:
                        item_type = terrain.items[item_key]
                        
                        # Calculate distance between worm center and item center
                        item_world_x = check_x * TILE_SIZE + TILE_SIZE // 2
                        item_world_y = check_y * TILE_SIZE + TILE_SIZE // 2 + terrain_y_offset  # Add offset back for world coordinates
                        distance = math.sqrt((self.x - item_world_x) ** 2 + (self.y - item_world_y) ** 2)
                        
                        # If close enough, collect the item
                        if distance < WORM_RADIUS + TILE_SIZE // 2:
                            if item_type == 1:  # ItemType.GAS_BOTTLE
                                # Refill gas
                                self.gas = min(MAX_GAS, self.gas + GAS_REFILL_AMOUNT)
                            elif item_type == 2:  # ItemType.DYNAMITE
                                # Add dynamite
                                self.dynamite_count += 1
                            
                            # Remove item from terrain
                            del terrain.items[item_key]
        
    def _get_tool_color(self):
        """Get the color for the current tool"""
        colors = {
            "drill": GRAY,
            "dynamite": RED,
            "torch": (255, 165, 0),  # Orange
            "laser": BLUE
        }
        return colors.get(self.current_tool, WHITE)