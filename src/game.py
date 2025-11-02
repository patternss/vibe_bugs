"""
Main Game Class
Handles overall game state, coordination between systems
"""

import pygame
import math
import time
import random
from src.terrain import Terrain
from src.worm import Worm
from src.explosion import Explosion, ExplosionPresets
from src.tombstone import Tombstone
from src.config import *

class Game:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.level = 1
        self.terrain = Terrain(MAP_WIDTH, MAP_HEIGHT)
        
        # Create worms based on configuration
        self.worms = []
        self.current_player = 0  # Index of currently active player
        
        # Pause menu state
        self.paused = False
        self.quit_menu_active = False
        self.quit_menu_selection = 0  # 0 for No, 1 for Yes
        
        # FPS tracking
        self.fps_values = []
        self.fps_update_timer = 0
        
        for i, worm_config in enumerate(config['worms']):
            # Start positions spread across the top with terrain offset
            terrain_y_offset = UI_HEIGHT
            start_x = 100 + i * 300  # Spread worms wider for bigger map
            start_y = int(MAP_HEIGHT * TILE_SIZE * 0.3) + terrain_y_offset  # Account for offset
            
            # Move up until we find empty space
            while start_y > terrain_y_offset + 50 and self.terrain.is_solid(start_x, start_y):
                start_y -= TILE_SIZE
                
            worm = Worm(start_x, start_y)
            worm.name = worm_config['name']
            worm.color = worm_config['color']
            worm.is_human = worm_config['is_human']
            worm.player_id = worm_config['player_id']
            worm.tools_mode = config.get('tools_mode', 'standard')
            self.worms.append(worm)
        
        self.goal_pos = (MAP_WIDTH * TILE_SIZE - 100, MAP_HEIGHT * TILE_SIZE + terrain_y_offset - 100)
        self.wormhole_animation_time = 0  # For animating the wormhole
        self.level_complete = False
        
        # Camera follows the current active worm
        self.camera_x = 0
        self.camera_y = 0
        
        # Explosion system
        self.active_explosions = []
        
        # Death and respawn system
        self.tombstones = []
        
        # Battle timer system
        self.battle_timer_enabled = config.get('game_mode') == 'battle'  # Enable for battle mode
        # Use configured battle length or default
        battle_minutes = config.get('battle_length_minutes', 5)  # Default to 5 minutes
        self.battle_timer_duration = battle_minutes * 60  # Convert to seconds
        self.battle_timer = self.battle_timer_duration  # Timer in seconds
        self.battle_timer_start_time = time.time()  # Track when game started
        self.timer_flash_state = False  # For flashing effect
        self.timer_flash_timer = 0.0  # Track flash timing
        
    def handle_event(self, event):
        """Handle input events"""
        # Handle pause menu events first
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.quit_menu_active:
                    self.quit_menu_active = False
                    self.paused = False
                elif self.paused:
                    self.paused = False
                else:
                    self.paused = True
                    self.quit_menu_active = True
                    self.quit_menu_selection = 0
                return
            
            # Handle quit menu navigation
            if self.quit_menu_active:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.quit_menu_selection = 1 - self.quit_menu_selection  # Toggle between 0 and 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.quit_menu_selection == 1:  # Yes selected
                        return "quit_to_menu"
                    else:  # No selected
                        self.quit_menu_active = False
                        self.paused = False
                return
        
        # Handle mouse events for quit menu
        if event.type == pygame.MOUSEBUTTONDOWN and self.quit_menu_active:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calculate button positions (same as in render method)
            box_width = 400
            box_height = 200
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            button_width = 120
            button_height = 50
            button_y = box_y + 120
            
            # No button bounds
            no_x = box_x + 70
            if no_x <= mouse_x <= no_x + button_width and button_y <= mouse_y <= button_y + button_height:
                self.quit_menu_active = False
                self.paused = False
                return
            
            # Yes button bounds  
            yes_x = box_x + 210
            if yes_x <= mouse_x <= yes_x + button_width and button_y <= mouse_y <= button_y + button_height:
                return "quit_to_menu"
        
        # Handle mouse hover for quit menu
        if event.type == pygame.MOUSEMOTION and self.quit_menu_active:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calculate button positions
            box_width = 400
            box_height = 200
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            button_width = 120
            button_height = 50
            button_y = box_y + 120
            
            # Check which button mouse is over
            no_x = box_x + 70
            yes_x = box_x + 210
            
            if no_x <= mouse_x <= no_x + button_width and button_y <= mouse_y <= button_y + button_height:
                self.quit_menu_selection = 0  # No button
            elif yes_x <= mouse_x <= yes_x + button_width and button_y <= mouse_y <= button_y + button_height:
                self.quit_menu_selection = 1  # Yes button
        
        # Don't process game events if paused
        if self.paused:
            return
        
        # Route events to the appropriate player based on key
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # Keys that belong to player 1
            p1_keys = [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_f, pygame.K_SPACE, pygame.K_q, pygame.K_e]
            # Keys that belong to player 2
            p2_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RCTRL, pygame.K_COMMA, pygame.K_MINUS, pygame.K_PERIOD]

            if event.key in p1_keys:
                player1_worms = [w for w in self.worms if w.is_human and w.player_id == 1]
                if player1_worms:
                    player1_worms[0].handle_event(event, player_id=1)
            elif event.key in p2_keys:
                player2_worms = [w for w in self.worms if w.is_human and w.player_id == 2]
                if player2_worms:
                    player2_worms[0].handle_event(event, player_id=2)
            else:
                # If key does not map to a specific player, send to current active human worm
                current_worm = self.worms[self.current_player]
                if current_worm.is_human:
                    current_worm.handle_event(event, player_id=current_worm.player_id)
        else:
            # Other events (mouse, etc.) go to current active player
            current_worm = self.worms[self.current_player]
            if current_worm.is_human:
                current_worm.handle_event(event)
        
    def update(self, dt):
        """Update game state"""
        # Update FPS tracking
        if dt > 0:
            current_fps = 1.0 / dt
            self.fps_values.append(current_fps)
            if len(self.fps_values) > 60:  # Keep last 60 frames
                self.fps_values.pop(0)
        
        self.fps_update_timer += dt
        
        # Don't update game state if paused
        if self.paused:
            return
            
        # Update battle timer if enabled
        if self.battle_timer_enabled:
            elapsed_time = time.time() - self.battle_timer_start_time
            self.battle_timer = max(0, self.battle_timer_duration - elapsed_time)
            
            # Update flash timer for warning effect
            if self.battle_timer <= BATTLE_TIMER_WARNING_TIME:
                self.timer_flash_timer += dt
                if self.timer_flash_timer >= BATTLE_TIMER_FLASH_RATE:
                    self.timer_flash_state = not self.timer_flash_state
                    self.timer_flash_timer = 0.0
            
            # Check if time is up
            if self.battle_timer <= 0:
                return "show_endgame_stats"  # Signal to show stats screen
            
            
        # Update wormhole animation
        self.wormhole_animation_time += dt
        
        # Update all worms
        for worm in self.worms:
            death_info = worm.update(dt, self.terrain)
            # Handle any death from fall damage
            if death_info and isinstance(death_info, dict) and death_info.get('needs_death_handling'):
                self._handle_worm_death(worm, death_info.get('damage', 0), death_info.get('killer'))
            
        # Check for tool damage between worms
        self._check_tool_damage()
        
        # Update explosions
        self._update_explosions(dt)
        
        # Handle death and respawn
        self._handle_death_and_respawn(dt)
        
        # Update tombstones
        self._update_tombstones(dt)
        
        # Check if any worm reached goal
        for worm in self.worms:
            worm_pos = worm.get_position()
            goal_distance = ((worm_pos[0] - self.goal_pos[0])**2 + (worm_pos[1] - self.goal_pos[1])**2)**0.5
            if goal_distance < 50 and not self.level_complete:
                self.level_complete = True
                self._next_level()
                break
            
    def _check_tool_damage(self):
        """Check if any worms are damaged by tools used by other worms"""
        for attacker in self.worms:
            if attacker.is_dead or not attacker.tool_used_this_frame:
                continue
                
            tool_info = attacker.tool_used_this_frame
            tool = tool_info['tool']
            target_x = tool_info['target_x']
            target_y = tool_info['target_y']
            head_x, head_y = tool_info['attacker_pos']
            
            # Check damage to other worms based on tool type
            for victim in self.worms:
                if victim == attacker or victim.is_dead:
                    continue
                    
                victim_x, victim_y = victim.body_segments[0]
                
                # Check if victim is in tool's damage area
                if tool == "drill":
                    # Drill: Check if victim is in drill rectangle below attacker
                    drill_left = head_x - DRILL_WIDTH // 2
                    drill_right = head_x + DRILL_WIDTH // 2
                    drill_top = head_y + WORM_RADIUS
                    drill_bottom = head_y + WORM_RADIUS + DRILL_DEPTH
                    
                    if (drill_left <= victim_x <= drill_right and 
                        drill_top <= victim_y <= drill_bottom):
                        damage_result = victim.take_damage(DRILL_DAMAGE, attacker)
                        if damage_result and isinstance(damage_result, dict) and damage_result.get('needs_death_handling'):
                            self._handle_worm_death(victim, DRILL_DAMAGE, attacker)
                        
                elif tool == "laser":
                    # Laser: Check if victim is on the laser line
                    # Calculate distance from victim to laser line
                    # Line from (head_x, head_y) to (target_x, target_y)
                    line_length = math.sqrt((target_x - head_x)**2 + (target_y - head_y)**2)
                    if line_length > 0:
                        # Distance from point to line formula
                        distance = abs((target_y - head_y) * victim_x - (target_x - head_x) * victim_y + 
                                     target_x * head_y - target_y * head_x) / line_length
                        
                        # Check if victim is close to laser line and within laser range
                        victim_distance_from_start = math.sqrt((victim_x - head_x)**2 + (victim_y - head_y)**2)
                        if distance <= LASER_WIDTH // 2 and victim_distance_from_start <= line_length:
                            damage_result = victim.take_damage(LASER_DAMAGE, attacker)
                            if damage_result and isinstance(damage_result, dict) and damage_result.get('needs_death_handling'):
                                self._handle_worm_death(victim, LASER_DAMAGE, attacker)
                            
                elif tool == "torch":
                    # Torch: Check if victim is in torch cone
                    if 'direction_angle' in tool_info:
                        direction_angle = tool_info['direction_angle']
                        
                        # Calculate angle from attacker to victim
                        victim_angle = math.atan2(victim_y - head_y, victim_x - head_x)
                        
                        # Check if victim is within torch cone
                        angle_diff = abs(victim_angle - direction_angle)
                        # Normalize angle difference to [-pi, pi]
                        while angle_diff > math.pi:
                            angle_diff -= 2 * math.pi
                        while angle_diff < -math.pi:
                            angle_diff += 2 * math.pi
                            
                        victim_distance = math.sqrt((victim_x - head_x)**2 + (victim_y - head_y)**2)
                        cone_half_angle = math.radians(TORCH_CONE_ANGLE / 2)
                        
                        if abs(angle_diff) <= cone_half_angle and victim_distance <= TORCH_RANGE:
                            damage_result = victim.take_damage(TORCH_DAMAGE, attacker)
                            if damage_result and isinstance(damage_result, dict) and damage_result.get('needs_death_handling'):
                                self._handle_worm_death(victim, TORCH_DAMAGE, attacker)
        
        # Check dynamite explosions
        for worm in self.worms:
            if worm.is_dead:
                continue
                
            # Check for exploded dynamites and create explosions
            for dynamite in worm.thrown_dynamites[:]:  # Copy list to safely modify
                if hasattr(dynamite, 'exploded_this_frame') and dynamite.exploded_this_frame:
                    explosion_x, explosion_y = dynamite.get_position()
                    
                    # Remove the exploded dynamite
                    worm.thrown_dynamites.remove(dynamite)
                    
                    # Create explosion animation and handle damage
                    explosion = ExplosionPresets.dynamite_explosion(explosion_x, explosion_y, worm)
                    damaged_worms = explosion.apply_damage(self.worms)
                    
                    # Handle any deaths from explosion
                    for damaged_worm, damage, distance, needs_death_handling, damage_result in damaged_worms:
                        if needs_death_handling:
                            self._handle_worm_death(damaged_worm, damage, worm)
                    
                    self.active_explosions.append(explosion)
    
    def _update_explosions(self, dt):
        """Update all active explosions"""
        for explosion in self.active_explosions[:]:  # Copy list to safely modify
            if not explosion.update(dt):
                # Explosion finished, remove it
                self.active_explosions.remove(explosion)
    
    def create_explosion(self, x, y, radius, damage, source_worm=None):
        """Create an explosion at the specified location"""
        explosion = Explosion(x, y, radius, damage, source_worm)
        explosion.apply_damage(self.worms)
        self.active_explosions.append(explosion)
        return explosion
    
    def _create_tombstone(self, tombstone_data):
        """Create a tombstone from death data"""
        tombstone = Tombstone(
            tombstone_data['x'],
            tombstone_data['y'],
            tombstone_data['gas'],
            tombstone_data['dynamite'],
            tombstone_data['deceased_name']
        )
        self.tombstones.append(tombstone)
        
    def _handle_death_and_respawn(self, dt):
        """Handle worm death and respawn logic"""
        for worm in self.worms:
            if worm.is_respawning:
                # Update respawn timer for respawning worms
                ready_to_complete_respawn = worm.update_respawn_timer(dt)
                
                if ready_to_complete_respawn:
                    # Complete the respawn process (transition to spawn protection)
                    worm.respawn()
            elif not worm.is_dead:
                # Update spawn protection for living worms
                if worm.spawn_protection > 0:
                    worm.spawn_protection -= dt
                    
    def _handle_worm_death(self, worm, damage, attacker):
        """Handle worm death with immediate relocation and tombstone creation"""
        # Find a safe spawn location for immediate relocation
        spawn_x, spawn_y = self._find_safe_spawn_location(worm)
        
        # Call die method with new location
        tombstone_data = worm.die(attacker, spawn_x, spawn_y)
        
        # Create tombstone if data was returned
        if tombstone_data:
            self._create_tombstone(tombstone_data)
        
        return tombstone_data
                    
    def _find_safe_spawn_location(self, respawning_worm):
        """Find a safe location to spawn away from other worms"""
        # Try to spawn near the top of the map, but not too close to other worms
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            # Random X position across the map
            spawn_x = random.uniform(WORM_RADIUS + 50, SCREEN_WIDTH - WORM_RADIUS - 50)
            # Spawn in upper portion of the map
            spawn_y = random.uniform(UI_HEIGHT + 100, UI_HEIGHT + 300)
            
            # Check distance from other living worms
            safe = True
            for other_worm in self.worms:
                if other_worm != respawning_worm and not other_worm.is_dead:
                    other_x, other_y = other_worm.body_segments[0]
                    distance = math.sqrt((spawn_x - other_x)**2 + (spawn_y - other_y)**2)
                    if distance < MIN_SPAWN_DISTANCE:
                        safe = False
                        break
                        
            # Check if spawn location is not inside terrain
            if safe and not self.terrain.is_solid(spawn_x, spawn_y):
                # Find ground level below spawn point
                ground_y = spawn_y
                while ground_y < SCREEN_HEIGHT - 50 and not self.terrain.is_solid(spawn_x, ground_y):
                    ground_y += 5
                    
                # Spawn a bit above ground
                return spawn_x, max(spawn_y, ground_y - WORM_RADIUS - 10)
                
            attempts += 1
            
        # Fallback: spawn at default location if no safe spot found
        return 200, UI_HEIGHT + 150
        
    def _update_tombstones(self, dt):
        """Update tombstone animations and handle looting"""
        for tombstone in self.tombstones[:]:  # Copy list to safely modify
            tombstone.update(dt)
            
            # Check if any living worm can loot this tombstone
            for worm in self.worms:
                if not worm.is_dead and tombstone.can_be_looted_by(worm):
                    # For now, auto-loot when near. Later we can add key press requirement
                    if tombstone.loot(worm):
                        # Tombstone was successfully looted, remove it
                        self.tombstones.remove(tombstone)
                        break
    
    def _next_level(self):
        """Transition to the next level"""
        self.level += 1
        
        # Generate new terrain
        self.terrain = Terrain(MAP_WIDTH, MAP_HEIGHT)
        
        # Reset all worms but keep their gas
        for i, worm in enumerate(self.worms):
            terrain_y_offset = UI_HEIGHT
            start_x = 100 + i * 300  # Spread worms wider for bigger map
            # Find a safe spot on the surface for new level
            start_y = int(MAP_HEIGHT * TILE_SIZE * 0.3) + terrain_y_offset
            while start_y > terrain_y_offset + 50 and self.terrain.is_solid(start_x, start_y):
                start_y -= TILE_SIZE
            
            # Preserve properties
            worm_gas = worm.gas
            worm_dynamites = worm.dynamite_count
            worm_hp = worm.hp
            worm_name = worm.name
            worm_color = worm.color
            worm_is_human = worm.is_human
            worm_player_id = worm.player_id
            
            # Create new worm with preserved properties
            new_worm = Worm(start_x, start_y)
            new_worm.gas = worm_gas
            new_worm.dynamite_count = worm_dynamites
            new_worm.hp = worm_hp
            new_worm.name = worm_name
            new_worm.color = worm_color
            new_worm.is_human = worm_is_human
            new_worm.player_id = worm_player_id
            
            self.worms[i] = new_worm
        
        # Reset level completion flag
        self.level_complete = False
            
    def render(self):
        """Render everything to screen"""
        self.screen.fill(BLACK)
        
        # Fixed camera system - no camera movement
        camera_x = 0
        camera_y = 0
        
        # Render terrain with camera offset
        self.terrain.render(self.screen, camera_x, camera_y)
        
        # Render wormhole (goal) with camera offset
        self._render_wormhole(camera_x, camera_y)
        
        # Render all worms
        for worm in self.worms:
            worm.render(self.screen, camera_x, camera_y)
            
        # Render explosions
        for explosion in self.active_explosions:
            explosion.render(self.screen, camera_x, camera_y)
            
        # Render thrown dynamites for each worm
        for worm in self.worms:
            for dynamite in worm.thrown_dynamites:
                dynamite.render(self.screen, camera_x, camera_y)
                
        # Render tombstones
        for tombstone in self.tombstones:
            tombstone.render(self.screen, camera_x, camera_y)
        
        # Render UI
        self._render_ui()
        
        # Render FPS counter
        self._render_fps()
        
        # Render pause menu if active
        if self.paused:
            self._render_pause_menu()
        
    def _render_wormhole(self, camera_x=0, camera_y=0):
        """Render an animated wormhole at the goal position"""
        center_x, center_y = self.goal_pos
        screen_x = center_x - camera_x
        screen_y = center_y - camera_y
        
        # Only render if visible on screen
        if -100 <= screen_x <= SCREEN_WIDTH + 100 and -100 <= screen_y <= SCREEN_HEIGHT + 100:
            # Wormhole consists of multiple rotating rings
            num_rings = 8
            max_radius = 60
            
            for ring in range(num_rings):
                # Calculate ring properties
                ring_radius = max_radius * (ring + 1) / num_rings
                ring_alpha = max(50, 255 - ring * 25)  # Fade out towards edges
                
                # Rotation speed varies for each ring (creates spiral effect)
                rotation_speed = 2.0 + ring * 0.3
                rotation_angle = self.wormhole_animation_time * rotation_speed
            
            # Create swirling colors (purple to blue to white)
            base_colors = [
                (75, 0, 130),    # Indigo
                (138, 43, 226),  # Blue Violet  
                (0, 191, 255),   # Deep Sky Blue
                (255, 255, 255)  # White (center)
            ]
            
            color_index = ring % len(base_colors)
            base_color = base_colors[color_index]
            
            # Draw ring segments for swirling effect
            segments = 12
            for segment in range(segments):
                segment_angle = (segment * 2 * math.pi / segments) + rotation_angle
                
                # Calculate segment positions
                inner_radius = ring_radius * 0.7
                outer_radius = ring_radius
                
                # Create segment points
                angle1 = segment_angle
                angle2 = segment_angle + (2 * math.pi / segments) * 0.8  # Small gap between segments
                
                # Only draw every other segment for spiral effect
                if segment % 2 == 0:
                    # Draw arc segments
                    start_angle = angle1
                    end_angle = angle2
                    
                    # Create a surface for the ring segment with alpha
                    ring_surface = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
                    
                    # Draw the ring segment
                    points = []
                    arc_segments = 8
                    for i in range(arc_segments + 1):
                        angle = start_angle + (end_angle - start_angle) * i / arc_segments
                        # Outer edge (use screen coordinates)
                        x = screen_x + math.cos(angle) * outer_radius
                        y = screen_y + math.sin(angle) * outer_radius
                        points.append((x, y))
                    
                    for i in range(arc_segments, -1, -1):
                        angle = start_angle + (end_angle - start_angle) * i / arc_segments
                        # Inner edge (use screen coordinates)
                        x = screen_x + math.cos(angle) * inner_radius
                        y = screen_y + math.sin(angle) * inner_radius
                        points.append((x, y))
                    
                    if len(points) > 2:
                        # Create color with alpha for transparency effect
                        color_with_alpha = (*base_color, ring_alpha)
                        
                        # Create a temporary surface to draw the polygon with alpha
                        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        pygame.draw.polygon(temp_surface, color_with_alpha, points)
                        self.screen.blit(temp_surface, (0, 0))
        
            # Draw center glow
            glow_radius = 15 + math.sin(self.wormhole_animation_time * 4) * 5
            glow_color = (255, 255, 255, 200)
            
            # Create glowing center
            glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, 100), (glow_radius * 2, glow_radius * 2), int(glow_radius * 2))
            pygame.draw.circle(glow_surface, (200, 200, 255, 150), (glow_radius * 2, glow_radius * 2), int(glow_radius * 1.5))
            pygame.draw.circle(glow_surface, (255, 255, 255, 255), (glow_radius * 2, glow_radius * 2), int(glow_radius))
            
            # Position the glow at the center (using screen coordinates)
            glow_rect = glow_surface.get_rect(center=(screen_x, screen_y))
            self.screen.blit(glow_surface, glow_rect)
            
            # Add sparkle effects around the wormhole
            self._render_wormhole_sparkles(camera_x, camera_y)
        
    def _render_wormhole_sparkles(self, camera_x=0, camera_y=0):
        """Add sparkle effects around the wormhole"""
        center_x, center_y = self.goal_pos
        sparkle_count = 12
        
        for i in range(sparkle_count):
            # Each sparkle has its own animation offset
            sparkle_time = self.wormhole_animation_time + i * 0.5
            
            # Position sparkles in a wider area around the wormhole
            angle = (i * 2 * math.pi / sparkle_count) + sparkle_time * 0.5
            distance = 70 + math.sin(sparkle_time * 2) * 20
            
            world_x = center_x + math.cos(angle) * distance
            world_y = center_y + math.sin(angle) * distance
            
            # Convert to screen coordinates
            sparkle_x = world_x - camera_x
            sparkle_y = world_y - camera_y
            
            # Only render if on screen
            if 0 <= sparkle_x <= SCREEN_WIDTH and 0 <= sparkle_y <= SCREEN_HEIGHT:
                # Sparkle size and brightness variation
                sparkle_size = 2 + math.sin(sparkle_time * 3) * 1
                brightness = int(150 + math.sin(sparkle_time * 4) * 105)
                
                # Draw sparkle
                sparkle_color = (brightness, brightness, 255)
                pygame.draw.circle(self.screen, sparkle_color, (int(sparkle_x), int(sparkle_y)), int(sparkle_size))
                
                # Add a smaller white center
                if sparkle_size > 1:
                    pygame.draw.circle(self.screen, WHITE, (int(sparkle_x), int(sparkle_y)), 1)
        
    def _render_ui(self):
        """Render user interface elements"""
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 24)
        tiny_font = pygame.font.Font(None, 20)
        
        # Draw light gray background for the top UI area
        ui_background_color = (180, 180, 180)  # Light gray
        pygame.draw.rect(self.screen, ui_background_color, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        
        # Player status bars at the top horizontally
        player_width = SCREEN_WIDTH // (len(self.worms) + 1)  # Make space tighter by adding 1
        for i, worm in enumerate(self.worms):
            x_start = i * player_width + 10
            y_start = 10
            
            # Player name with color indicator (fluctuates during respawn/protection)
            if worm.is_respawning or worm.spawn_protection > 0:
                # Use the same fluctuating colors as the worm body
                name_color = worm.get_render_color()
            else:
                name_color = worm.color if hasattr(worm, 'color') else BLACK
            name_text = font.render(worm.name, True, name_color)
            self.screen.blit(name_text, (x_start, y_start))
            
            # === HEALTH SECTION ===
            hp_y = y_start + 25
            bar_width = min(120, player_width - 20)
            bar_height = 8
            
            # HP text above bar
            hp_text = tiny_font.render(f"HP: {worm.hp}/{worm.max_hp}", True, BLACK)
            self.screen.blit(hp_text, (x_start, hp_y))
            
            # HP background bar
            pygame.draw.rect(self.screen, GRAY, (x_start, hp_y + 12, bar_width, bar_height))
            
            # HP level bar
            hp_ratio = worm.hp / worm.max_hp
            hp_bar_width = int(bar_width * hp_ratio)
            if hp_ratio > 0.6:
                hp_color = GREEN
            elif hp_ratio > 0.3:
                hp_color = YELLOW
            else:
                hp_color = RED
            pygame.draw.rect(self.screen, hp_color, (x_start, hp_y + 12, hp_bar_width, bar_height))
            
            # === GAS SECTION ===
            gas_y = hp_y + 30
            
            # Only show weapon stats in standard mode
            if getattr(worm, 'tools_mode', 'standard') == 'standard':
                # Gas text above bar
                gas_text = tiny_font.render(f"GAS: {worm.gas}/{MAX_GAS}", True, BLACK)
                self.screen.blit(gas_text, (x_start, gas_y))
                
                # Gas background bar
                pygame.draw.rect(self.screen, GRAY, (x_start, gas_y + 12, bar_width, bar_height))
                
                # Gas level bar
                gas_ratio = worm.gas / MAX_GAS
                gas_bar_width = int(bar_width * gas_ratio)
                gas_color = GREEN if gas_ratio > 0.3 else (YELLOW if gas_ratio > 0.1 else RED)
                pygame.draw.rect(self.screen, gas_color, (x_start, gas_y + 12, gas_bar_width, bar_height))
                
                # === LASER SECTION ===
                battery_y = gas_y + 30
                
                # Battery text above bar with cooldown indicator
                if worm.laser_cooldown_timer > 0:
                    battery_text = tiny_font.render(f"LASER: COOLDOWN {worm.laser_cooldown_timer:.1f}s", True, BLACK)
                else:
                    battery_text = tiny_font.render(f"LASER: {int(worm.laser_battery)}%", True, BLACK)
                self.screen.blit(battery_text, (x_start, battery_y))
                
                # Laser background bar
                pygame.draw.rect(self.screen, GRAY, (x_start, battery_y + 12, bar_width, bar_height))
                
                # Battery level bar
                battery_ratio = worm.laser_battery / 100.0
                battery_bar_width = int(bar_width * battery_ratio)
                
                # Color based on battery level and cooldown status
                if worm.laser_cooldown_timer > 0:
                    battery_color = RED  # Red when in cooldown
                elif battery_ratio > 0.6:
                    battery_color = CYAN  # Cyan for high battery (laser color)
                elif battery_ratio > 0.3:
                    battery_color = YELLOW
                else:
                    battery_color = RED
                
                pygame.draw.rect(self.screen, battery_color, (x_start, battery_y + 12, battery_bar_width, bar_height))
                
                # === EQUIPMENT SECTION ===
                # Dynamites count with icon color
                dynamite_text = tiny_font.render(f"Dynamites: {worm.dynamite_count}", True, DYNAMITE_INDICATOR_COLOR)
                self.screen.blit(dynamite_text, (x_start, battery_y + 30))
                
                # === COMBAT STATS SECTION ===
                # Kill/Death stats with distinct formatting
                kd_text = tiny_font.render(f"K/D: {worm.kills}/{worm.deaths}", True, BLACK)
                self.screen.blit(kd_text, (x_start, battery_y + 45))
            else:
                # In unlimited mode, show tools mode and only K/D stats
                tools_text = tiny_font.render("UNLIMITED TOOLS", True, (0, 255, 100))  # Green text
                self.screen.blit(tools_text, (x_start, gas_y))
                
                # === COMBAT STATS SECTION ===
                # Kill/Death stats with distinct formatting
                kd_text = tiny_font.render(f"K/D: {worm.kills}/{worm.deaths}", True, BLACK)
                self.screen.blit(kd_text, (x_start, gas_y + 20))
        
        # Level indicator at top right
        level_text = font.render(f"LEVEL {self.level}", True, BLACK)
        level_rect = level_text.get_rect(right=SCREEN_WIDTH-20, y=15)
        self.screen.blit(level_text, level_rect)
        
        # Battle timer display (if enabled)
        if self.battle_timer_enabled:
            minutes = int(self.battle_timer // 60)
            seconds = int(self.battle_timer % 60)
            timer_text = f"{minutes:02d}:{seconds:02d}"
            
            # Choose color and flash effect for warning
            if self.battle_timer <= BATTLE_TIMER_WARNING_TIME:
                timer_color = RED if self.timer_flash_state else WHITE
            else:
                timer_color = BLACK
            
            # Render timer text (positioned lower to avoid cutoff)
            timer_surface = font.render(timer_text, True, timer_color)
            timer_rect = timer_surface.get_rect(centerx=SCREEN_WIDTH//2, y=35)
            self.screen.blit(timer_surface, timer_rect)
            
            # Add "TIME" label above the timer
            time_label = small_font.render("TIME", True, timer_color)
            time_label_rect = time_label.get_rect(centerx=SCREEN_WIDTH//2, y=15)
            self.screen.blit(time_label, time_label_rect)
    
    def _render_pause_menu(self):
        """Render the pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.quit_menu_active:
            # Quit confirmation box
            box_width = 400
            box_height = 200
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            
            # Box background
            pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, BLACK, (box_x, box_y, box_width, box_height), 3)
            
            # Title
            font = pygame.font.Font(None, 36)
            title_text = font.render("Quit to Main Menu?", True, BLACK)
            title_rect = title_text.get_rect(centerx=SCREEN_WIDTH//2, y=box_y + 30)
            self.screen.blit(title_text, title_rect)
            
            # Buttons
            button_font = pygame.font.Font(None, 32)
            button_width = 120
            button_height = 50
            button_y = box_y + 120
            
            # No button
            no_x = box_x + 70
            no_color = (100, 200, 100) if self.quit_menu_selection == 0 else (150, 150, 150)
            pygame.draw.rect(self.screen, no_color, (no_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, BLACK, (no_x, button_y, button_width, button_height), 2)
            no_text = button_font.render("No", True, BLACK)
            no_rect = no_text.get_rect(center=(no_x + button_width//2, button_y + button_height//2))
            self.screen.blit(no_text, no_rect)
            
            # Yes button
            yes_x = box_x + 210
            yes_color = (200, 100, 100) if self.quit_menu_selection == 1 else (150, 150, 150)
            pygame.draw.rect(self.screen, yes_color, (yes_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, BLACK, (yes_x, button_y, button_width, button_height), 2)
            yes_text = button_font.render("Yes", True, BLACK)
            yes_rect = yes_text.get_rect(center=(yes_x + button_width//2, button_y + button_height//2))
            self.screen.blit(yes_text, yes_rect)
            
            # Instructions
            instruction_font = pygame.font.Font(None, 24)
            instruction_text = instruction_font.render("Use ← → to select, ENTER to confirm, ESC to cancel", True, BLACK)
            instruction_rect = instruction_text.get_rect(centerx=SCREEN_WIDTH//2, y=box_y + box_height - 25)
            self.screen.blit(instruction_text, instruction_rect)
        else:
            # Simple pause message
            font = pygame.font.Font(None, 72)
            pause_text = font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(pause_text, pause_rect)
            
            instruction_font = pygame.font.Font(None, 36)
            instruction_text = instruction_font.render("Press ESC to resume", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(instruction_text, instruction_rect)
    
    def _render_fps(self):
        """Render FPS counter in bottom right corner"""
        if self.fps_values:
            # Calculate average FPS
            avg_fps = sum(self.fps_values) / len(self.fps_values)
            
            # Choose color based on FPS
            if avg_fps >= 50:
                fps_color = GREEN
            elif avg_fps >= 30:
                fps_color = YELLOW
            else:
                fps_color = RED
            
            # Render FPS text
            fps_font = pygame.font.Font(None, 28)
            fps_text = fps_font.render(f"FPS: {avg_fps:.1f}", True, fps_color)
            fps_rect = fps_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
            
            # Add background for better readability
            bg_rect = fps_rect.copy()
            bg_rect.inflate_ip(10, 4)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
            
            self.screen.blit(fps_text, fps_rect)
    
    def get_game_stats(self):
        """
        Collect and return game statistics for all players
        """
        stats = {}
        for i, worm in enumerate(self.worms):
            stats[i] = {
                'name': getattr(worm, 'name', f'Player {i+1}'),
                'color': getattr(worm, 'color', (255, 255, 255)),
                'kills': worm.kills,
                'deaths': worm.deaths,
                'fall_deaths': getattr(worm, 'fall_deaths', 0),
                'self_deaths': getattr(worm, 'self_deaths', 0)
            }
        return stats