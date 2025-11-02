import json
import pygame
from typing import Dict, Any, Optional

class GameInfoManager:
    """
    Manages loading and displaying game information based on current game mode.
    Provides centralized access to all game mechanics, controls, and tips.
    """
    
    def __init__(self):
        self.info_data: Dict[str, Any] = {}
        self.current_mode: str = "battle"  # Default mode
        self.load_info()
    
    def load_info(self) -> bool:
        """Load game information from JSON file."""
        try:
            with open("game_info.json", "r", encoding="utf-8") as file:
                self.info_data = json.load(file)
            return True
        except FileNotFoundError:
            print("Warning: game_info.json not found. Using fallback data.")
            self._create_fallback_data()
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing game_info.json: {e}")
            self._create_fallback_data()
            return False
    
    def _create_fallback_data(self):
        """Create minimal fallback data if JSON file is unavailable."""
        self.info_data = {
            "game_modes": {
                "battle": {"title": "Battle Mode", "description": "Competitive PvP mode"},
                "coop": {"title": "Co-op Mode", "description": "Collaborative mode"}
            },
            "controls": {
                "movement": {"left": "A", "right": "D", "jump": "W"},
                "tools": {"drill": {"key": "F"}, "laser": {"key": "Mouse"}}
            }
        }
    
    def set_game_mode(self, mode: str):
        """Set the current game mode for info display."""
        if mode in self.info_data.get("game_modes", {}):
            self.current_mode = mode
        else:
            print(f"Warning: Unknown game mode '{mode}', keeping '{self.current_mode}'")
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get information specific to current game mode."""
        return self.info_data.get("game_modes", {}).get(self.current_mode, {})
    
    def get_controls_info(self) -> Dict[str, Any]:
        """Get all control information."""
        return self.info_data.get("controls", {})
    
    def get_mechanics_info(self) -> Dict[str, Any]:
        """Get all game mechanics information."""
        return self.info_data.get("mechanics", {})
    
    def get_ui_info(self) -> Dict[str, Any]:
        """Get UI element descriptions."""
        return self.info_data.get("ui_information", {})
    
    def get_tips(self, category: Optional[str] = None) -> list:
        """Get tips for current mode or specific category."""
        tips_data = self.info_data.get("tips", {})
        
        if category:
            return tips_data.get(category, [])
        else:
            # Return tips for current mode, fallback to general
            mode_tips = tips_data.get(self.current_mode, [])
            general_tips = tips_data.get("general", [])
            return mode_tips + general_tips
    
    def get_tool_damage_values(self) -> Dict[str, int]:
        """Get quick reference of tool damage values."""
        controls = self.get_controls_info()
        tools = controls.get("tools", {})
        
        damage_values = {}
        for tool_name, tool_info in tools.items():
            if "damage" in tool_info:
                # Extract numeric damage value from description
                damage_text = tool_info["damage"]
                if "50" in damage_text:
                    damage_values[tool_name] = 50
                elif "10" in damage_text:
                    damage_values[tool_name] = 10
                elif "30" in damage_text:
                    damage_values[tool_name] = 30
                elif "70" in damage_text:
                    damage_values[tool_name] = "70-distance"
        
        return damage_values
    
    def format_info_for_display(self, section: str, max_width: int = 80) -> list:
        """Format information section for display with word wrapping."""
        lines = []
        
        if section == "mode":
            mode_info = self.get_mode_info()
            lines.append(f"=== {mode_info.get('title', 'Game Mode')} ===")
            lines.append(mode_info.get('description', ''))
            lines.append(f"Objective: {mode_info.get('objective', 'N/A')}")
            lines.append("")
            
        elif section == "controls":
            lines.append("=== Controls ===")
            controls = self.get_controls_info()
            
            # Movement
            movement = controls.get("movement", {})
            lines.append("Movement:")
            for action, key in movement.items():
                if action != "description":
                    lines.append(f"  {action.title()}: {key}")
            lines.append("")
            
            # Tools
            tools = controls.get("tools", {})
            lines.append("Tools:")
            for tool_name, tool_info in tools.items():
                key = tool_info.get("key", "Unknown")
                damage = tool_info.get("damage", "")
                lines.append(f"  {tool_name.title()}: {key}")
                if damage:
                    lines.append(f"    Damage: {damage}")
            lines.append("")
            
        elif section == "mechanics":
            lines.append("=== Game Mechanics ===")
            mechanics = self.get_mechanics_info()
            
            # Health system
            health = mechanics.get("health_system", {})
            lines.append(f"Health: {health.get('max_hp', 100)} HP maximum")
            
            # Fall damage
            fall_dmg = mechanics.get("fall_damage", {})
            lines.append(f"Fall Damage: Starts at {fall_dmg.get('threshold', '50px')} drops")
            lines.append("")
            
        elif section == "tips":
            lines.append("=== Tips ===")
            tips = self.get_tips()
            for i, tip in enumerate(tips[:10], 1):  # Limit to 10 tips
                lines.append(f"{i}. {tip}")
            lines.append("")
        
        # Simple word wrapping
        wrapped_lines = []
        for line in lines:
            if len(line) <= max_width:
                wrapped_lines.append(line)
            else:
                # Basic word wrapping
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= max_width:
                        current_line += (" " if current_line else "") + word
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                        current_line = word
                if current_line:
                    wrapped_lines.append(current_line)
        
        return wrapped_lines

# Global instance for easy access
game_info = GameInfoManager()