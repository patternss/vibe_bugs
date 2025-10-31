"""
Terrain System
Handles the destructible terrain/map that worms can dig through
"""

import pygame
import random
import math
from src.config import *

class TerrainType:
    EMPTY = 0
    DIRT = 1
    ROCK = 2
    METAL = 3

class ItemType:
    GAS_BOTTLE = 1
    DYNAMITE = 2

class Terrain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TerrainType.EMPTY for _ in range(width)] for _ in range(height)]
        self.items = {}  # Dictionary to store items at (x, y) positions
        
        # Performance optimization: pre-render terrain surface
        self.terrain_surface = None
        self.terrain_dirty = True
        
        self.generate_terrain()
        
    def generate_terrain(self):
        """Generate procedural terrain with clear starting area"""
        # Create underground layers
        for y in range(self.height):
            for x in range(self.width):
                # Top area (top 35% should be completely empty for starting area)
                if y < self.height * 0.35:
                    # Keep completely empty above ground level
                    self.tiles[y][x] = TerrainType.EMPTY
                # Underground area (bottom 65%)
                else:
                    # Use simple random generation with some clustering
                    rand_val = random.random()
                    
                    # Add some influence from neighboring tiles for clustering
                    neighbor_influence = 0
                    if x > 0 and self.tiles[y][x-1] != TerrainType.EMPTY:
                        neighbor_influence += 0.2
                    if y > 0 and self.tiles[y-1][x] != TerrainType.EMPTY:
                        neighbor_influence += 0.2
                    
                    rand_val += neighbor_influence
                    
                    if rand_val > 0.7:
                        self.tiles[y][x] = TerrainType.DIRT
                    elif rand_val > 0.4:
                        self.tiles[y][x] = TerrainType.ROCK
                    elif rand_val > 0.1:
                        self.tiles[y][x] = TerrainType.EMPTY
                    else:
                        self.tiles[y][x] = TerrainType.METAL
                        
        # Create a ground level at about 35% down from top
        ground_level_y = int(self.height * 0.35)
        for x in range(self.width):
            # Create solid ground line
            if ground_level_y < self.height:
                self.tiles[ground_level_y][x] = TerrainType.DIRT
                
        # Create some tunnels for gameplay
        self._create_starting_tunnels()
        
        # Add gas bottles and dynamites randomly in the underground area
        self._place_collectible_items()
        
    def _create_starting_tunnels(self):
        """Create some initial tunnels so the game isn't impossible"""
        # Clear the starting area around where worm spawns
        start_clear_size = 5
        start_x = 100 // TILE_SIZE
        start_y = 100 // TILE_SIZE
        
        for dy in range(-start_clear_size, start_clear_size + 1):
            for dx in range(-start_clear_size, start_clear_size + 1):
                tx, ty = start_x + dx, start_y + dy
                if 0 <= tx < self.width and 0 <= ty < self.height:
                    self.tiles[ty][tx] = TerrainType.EMPTY
        
        # Create a horizontal tunnel partway down
        tunnel_y = int(self.height * 0.5)
        for x in range(20, 80):
            if x < self.width and tunnel_y < self.height:
                self.tiles[tunnel_y][x] = TerrainType.EMPTY
                # Clear above and below for easier navigation
                if tunnel_y - 1 >= 0:
                    self.tiles[tunnel_y - 1][x] = TerrainType.EMPTY
                if tunnel_y + 1 < self.height:
                    self.tiles[tunnel_y + 1][x] = TerrainType.EMPTY
                    
        # Create a vertical tunnel on the left side
        tunnel_x = 25
        for y in range(int(self.height * 0.35), int(self.height * 0.7)):
            if tunnel_x < self.width and y < self.height:
                self.tiles[y][tunnel_x] = TerrainType.EMPTY
                # Make it wider
                if tunnel_x + 1 < self.width:
                    self.tiles[y][tunnel_x + 1] = TerrainType.EMPTY
                    
    def _place_collectible_items(self):
        """Place gas bottles and dynamites randomly in accessible areas"""
        num_gas_bottles = 12  # Increased from 5 to 12
        num_dynamites = 8     # Increased from 3 to 8
        placed_gas = 0
        placed_dynamites = 0
        attempts = 0
        max_attempts = 2000   # Increased attempts for more items
        
        while (placed_gas < num_gas_bottles or placed_dynamites < num_dynamites) and attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(int(self.height * 0.4), self.height - 1)  # Only in underground area
            
            # Check if this is an empty space
            if self.tiles[y][x] == TerrainType.EMPTY:
                # Make sure it's not too close to other items
                too_close = False
                for (bx, by) in self.items.keys():
                    if abs(x - bx) < 10 and abs(y - by) < 10:  # Minimum distance
                        too_close = True
                        break
                
                if not too_close:
                    # Randomly decide between gas bottle and dynamite
                    if placed_gas < num_gas_bottles and (placed_dynamites >= num_dynamites or random.random() < 0.6):
                        self.items[(x, y)] = ItemType.GAS_BOTTLE
                        placed_gas += 1
                    elif placed_dynamites < num_dynamites:
                        self.items[(x, y)] = ItemType.DYNAMITE
                        placed_dynamites += 1
                    
            attempts += 1
            
    def get_tile(self, x, y):
        """Get terrain type at pixel coordinates"""
        terrain_y_offset = UI_HEIGHT  # Top space offset for UI
        adjusted_y = y - terrain_y_offset  # Subtract offset to get terrain-relative coordinates
        
        tile_x = int(x // TILE_SIZE)
        tile_y = int(adjusted_y // TILE_SIZE)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x]
        
        # Allow falling through bottom edge by returning EMPTY below terrain
        if tile_y >= self.height:
            return TerrainType.EMPTY
        
        # Other boundaries (left, right, top) are still unbreakable
        return TerrainType.METAL  # Boundaries are unbreakable
        
    def check_for_items(self, x, y, radius):
        """Check for items in the given area and return them"""
        terrain_y_offset = UI_HEIGHT  # Top space offset for UI
        adjusted_y = y - terrain_y_offset  # Subtract offset to get terrain-relative coordinates
        
        found_items = []
        tile_x = int(x // TILE_SIZE)
        tile_y = int(adjusted_y // TILE_SIZE)
        tile_radius = max(1, int(radius // TILE_SIZE))
        
        for dy in range(-tile_radius, tile_radius + 1):
            for dx in range(-tile_radius, tile_radius + 1):
                if dx*dx + dy*dy <= tile_radius*tile_radius:
                    tx, ty = tile_x + dx, tile_y + dy
                    if (tx, ty) in self.items:
                        found_items.append(((tx, ty), self.items[(tx, ty)]))
                        del self.items[(tx, ty)]  # Remove collected item
                        
        return found_items
        
    def dig(self, x, y, radius, tool_type="drill", direction_angle=0):
        """Dig a hole at the specified location"""
        terrain_y_offset = UI_HEIGHT  # Top space offset for UI
        adjusted_y = y - terrain_y_offset  # Subtract offset to get terrain-relative coordinates
        
        tile_x = int(x // TILE_SIZE)
        tile_y = int(adjusted_y // TILE_SIZE)
        
        if tool_type == "drill":
            # Drill digs a wide vertical shaft below the starting point
            drill_width_tiles = max(1, int(DRILL_WIDTH // TILE_SIZE))
            drill_depth_tiles = max(1, int(DRILL_DEPTH // TILE_SIZE))
            
            # Center the drill horizontally around the target point
            start_x = tile_x - drill_width_tiles // 2
            end_x = tile_x + drill_width_tiles // 2
            
            for dy in range(drill_depth_tiles):
                ty = tile_y + dy
                for tx in range(start_x, end_x + 1):
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        current_tile = self.tiles[ty][tx]
                        if self._can_dig(current_tile, tool_type):
                            self.tiles[ty][tx] = TerrainType.EMPTY
        elif tool_type == "torch":
            # Torch creates a cone shape in the specified direction
            cone_length = int(radius // TILE_SIZE)
            cone_angle = math.radians(TORCH_CONE_ANGLE)
            
            for distance in range(1, cone_length + 1):
                # Calculate cone width at this distance
                cone_width = int(distance * math.tan(cone_angle / 2))
                
                # Calculate center point at this distance
                center_x = tile_x + int(distance * math.cos(direction_angle))
                center_y = tile_y + int(distance * math.sin(direction_angle))
                
                # Dig in a circle around the center point
                for dy in range(-cone_width, cone_width + 1):
                    for dx in range(-cone_width, cone_width + 1):
                        if dx*dx + dy*dy <= cone_width*cone_width:
                            tx, ty = center_x + dx, center_y + dy
                            if 0 <= tx < self.width and 0 <= ty < self.height:
                                current_tile = self.tiles[ty][tx]
                                if self._can_dig(current_tile, tool_type):
                                    self.tiles[ty][tx] = TerrainType.EMPTY
        else:
            # Regular circular digging for other tools
            tile_radius = max(1, int(radius // TILE_SIZE))
            for dy in range(-tile_radius, tile_radius + 1):
                for dx in range(-tile_radius, tile_radius + 1):
                    if dx*dx + dy*dy <= tile_radius*tile_radius:
                        tx, ty = tile_x + dx, tile_y + dy
                        if 0 <= tx < self.width and 0 <= ty < self.height:
                            current_tile = self.tiles[ty][tx]
                            if self._can_dig(current_tile, tool_type):
                                self.tiles[ty][tx] = TerrainType.EMPTY
        
        # Mark terrain as needing re-rendering after any digging
        self._mark_terrain_dirty()
                            
    def _can_dig(self, terrain_type, tool_type):
        """Check if a tool can dig through a terrain type"""
        if terrain_type == TerrainType.EMPTY:
            return False
            
        if tool_type == "drill":
            return terrain_type in [TerrainType.DIRT, TerrainType.ROCK]
        elif tool_type == "dynamite":
            return terrain_type in [TerrainType.DIRT, TerrainType.ROCK, TerrainType.METAL]
        elif tool_type == "laser":
            return terrain_type in [TerrainType.ROCK, TerrainType.METAL]
        elif tool_type == "torch":
            return terrain_type in [TerrainType.DIRT, TerrainType.ROCK]  # Torch can dig both
            
        return False
        
    def is_solid(self, x, y):
        """Check if a position is solid (blocks movement)"""
        return self.get_tile(x, y) != TerrainType.EMPTY
    
    def _rebuild_terrain_surface(self):
        """Rebuild the pre-rendered terrain surface for optimal performance"""
        # Create surface to hold the entire terrain
        self.terrain_surface = pygame.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE))
        self.terrain_surface.set_colorkey(BLACK)  # Make black transparent
        self.terrain_surface.fill(BLACK)  # Fill with transparent color
        
        # Render all solid tiles to the surface
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.tiles[y][x]
                if tile_type != TerrainType.EMPTY:
                    color = self._get_tile_color(tile_type)
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.terrain_surface, color, rect)
        
        self.terrain_dirty = False
    
    def _mark_terrain_dirty(self):
        """Mark terrain as needing re-rendering"""
        self.terrain_dirty = True
        
    def render(self, screen, camera_x=0, camera_y=0):
        """Render the terrain to the screen using optimized surface blitting"""
        terrain_y_offset = UI_HEIGHT  # Top space offset for UI
        
        # Draw sky gradient background for the area between UI and terrain
        self._draw_sky_gradient(screen)
        
        # Rebuild terrain surface if dirty
        if self.terrain_dirty or self.terrain_surface is None:
            self._rebuild_terrain_surface()
        
        # Blit the entire terrain surface (much faster than individual rectangles)
        screen.blit(self.terrain_surface, (-camera_x, terrain_y_offset - camera_y))
                    
        # Render items (gas bottles and dynamites)
        for (x, y), item_type in self.items.items():
            screen_x = x * TILE_SIZE + TILE_SIZE // 2 - camera_x
            screen_y = y * TILE_SIZE + TILE_SIZE // 2 + terrain_y_offset - camera_y
            
            # Only render if visible
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                if item_type == ItemType.GAS_BOTTLE:
                    # Draw gas bottle as a bigger cylinder
                    bottle_width = 12  # Doubled from 6 to 12
                    bottle_height = 18  # Increased from 10 to 18
                    
                    # Bottle body (gray)
                    bottle_rect = pygame.Rect(screen_x - bottle_width//2, screen_y - bottle_height//2, 
                                            bottle_width, bottle_height)
                    pygame.draw.rect(screen, (128, 128, 128), bottle_rect)
                    
                    # Bottle top (darker gray)
                    top_rect = pygame.Rect(screen_x - bottle_width//2, screen_y - bottle_height//2, 
                                         bottle_width, 5)  # Increased from 3 to 5
                    pygame.draw.rect(screen, (64, 64, 64), top_rect)
                    
                    # Gas indicator (blue)
                    gas_rect = pygame.Rect(screen_x - bottle_width//2 + 2, screen_y - bottle_height//2 + 5, 
                                         bottle_width - 4, bottle_height - 7)  # Adjusted margins
                    pygame.draw.rect(screen, (0, 150, 255), gas_rect)
                    
                elif item_type == ItemType.DYNAMITE:
                    # Draw bigger dynamite stick
                    stick_width = 14  # Increased from 8 to 14
                    stick_height = 8   # Doubled from 4 to 8
                    
                    # Dynamite body (red)
                    stick_rect = pygame.Rect(screen_x - stick_width//2, screen_y - stick_height//2,
                                           stick_width, stick_height)
                    pygame.draw.rect(screen, (200, 0, 0), stick_rect)
                    
                    # Fuse (black line) - made longer
                    fuse_start_x = screen_x + stick_width//2
                    fuse_end_x = fuse_start_x + 6  # Increased from 4 to 6
                    fuse_y = screen_y - stick_height//2 - 3  # Adjusted position
                    pygame.draw.line(screen, (0, 0, 0), (fuse_start_x, fuse_y), (fuse_end_x, fuse_y), 2)
                    
                    # Spark at end of fuse (yellow)
                    pygame.draw.circle(screen, (255, 255, 0), (fuse_end_x, fuse_y), 2)
                    
    def _draw_sky_gradient(self, screen):
        """Draw a graduated sky background with 30 smooth shades of blue"""
        # Calculate the area for the sky (between UI and terrain)
        sky_start_y = UI_HEIGHT
        # Sky should only cover the area above the terrain, not the entire screen
        sky_height = min(SCREEN_HEIGHT - UI_HEIGHT, 400)  # Limit sky to reasonable height
        
        # Number of gradient segments for smooth transition
        num_segments = 100
        
        # Calculate segment height for each shade
        segment_height = sky_height / num_segments
        
        # Draw each shade as a rectangle with smooth color interpolation
        for i in range(num_segments):
            # Calculate interpolation factor (0.0 at top, 1.0 at bottom)
            factor = i / (num_segments - 1)
            
            # Light blue at top to midnight blue at bottom
            top_color = (173, 216, 230)    # Light blue
            bottom_color = (25, 25, 112)   # Midnight blue
            
            # Interpolate between colors
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
            
            color = (r, g, b)
            
            segment_y = sky_start_y + (i * segment_height)
            segment_rect_height = segment_height
            
            # Make sure the last segment fills to the end
            if i == num_segments - 1:
                segment_rect_height = sky_height - (i * segment_height)
            
            # Draw the segment as one rectangle
            segment_rect = pygame.Rect(0, int(segment_y), SCREEN_WIDTH, int(segment_rect_height) + 1)
            pygame.draw.rect(screen, color, segment_rect)
        
        # Fill the rest of the screen (underground area) with #404040
        underground_start_y = sky_start_y + sky_height
        if underground_start_y < SCREEN_HEIGHT:
            underground_color = (64, 64, 64)  # #404040 - medium gray
            pygame.draw.rect(screen, underground_color, 
                           (0, underground_start_y, SCREEN_WIDTH, SCREEN_HEIGHT - underground_start_y))
                    
    def _get_tile_color(self, tile_type):
        """Get the color for a terrain type"""
        if tile_type == TerrainType.DIRT:
            return BROWN
        elif tile_type == TerrainType.ROCK:
            return GRAY
        elif tile_type == TerrainType.METAL:
            return (64, 64, 64)  # Dark gray
        return BLACK