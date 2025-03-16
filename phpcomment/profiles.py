# profiles.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from .utils.logger import myLogger


class ProfileLoader:
    """
    Handles loading and validating profiles from YAML configuration.
    
    Profiles define preset combinations of model and strategy settings
    that can be selected via the CLI.
    """
    
    PROFILES_PATH = Path(__file__).parent.parent / "config" / "profiles.yaml"
    VALID_STRATEGIES = ["wholefile", "udiff", "searchreplace"]
    
    def __init__(self):
        """Initialize the profile loader."""
        self.profiles = {}
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """
        Load profiles from the YAML configuration file.
        Creates default profiles if the file doesn't exist.
        """
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.PROFILES_PATH), exist_ok=True)
        
        # Check if profiles file exists
        if not self.PROFILES_PATH.exists():
            myLogger.info(f"Creating default profiles at {self.PROFILES_PATH}")
            self._create_default_profiles()
        
        # Load profiles from file
        try:
            with open(self.PROFILES_PATH, 'r') as file:
                data = yaml.safe_load(file)
                if not data or 'profiles' not in data:
                    myLogger.warning("Invalid profiles file format. Creating default profiles.")
                    self._create_default_profiles()
                    with open(self.PROFILES_PATH, 'r') as file:
                        data = yaml.safe_load(file)
                
                self.profiles = data['profiles']
                self._validate_profiles()
        except Exception as e:
            myLogger.error(f"Error loading profiles: {str(e)}")
            myLogger.info("Using default profiles instead")
            self._create_default_profiles()
            with open(self.PROFILES_PATH, 'r') as file:
                data = yaml.safe_load(file)
                self.profiles = data['profiles']
    
    def _create_default_profiles(self) -> None:
        """Create default profiles configuration file."""
        default_profiles = {
            'profiles': {
                'default': {
                    'model': 'openrouter/google/gemini-2.0-flash-exp:free',
                    'strategy': 'wholefile'
                },
                'udiff': {
                    'model': 'openrouter/anthropic/claude-3.5-sonnet',
                    'strategy': 'udiff'
                },
                'searchreplace': {
                    'model': 'openrouter/qwen/qwen-2.5-coder-32b-instruct',
                    'strategy': 'searchreplace'
                }
            }
        }
        
        with open(self.PROFILES_PATH, 'w') as file:
            yaml.dump(default_profiles, file, default_flow_style=False)
    
    def _validate_profiles(self) -> None:
        """Validate all profiles to ensure they have required fields and valid values."""
        invalid_profiles = []
        
        for name, profile in self.profiles.items():
            if not self._validate_profile(name, profile):
                invalid_profiles.append(name)
        
        # Remove invalid profiles
        for name in invalid_profiles:
            myLogger.warning(f"Removing invalid profile: {name}")
            del self.profiles[name]
        
        # Ensure at least one valid profile exists
        if not self.profiles:
            myLogger.warning("No valid profiles found. Creating default profile.")
            self.profiles['default'] = {
                'model': 'openrouter/google/gemini-2.0-flash-exp:free',
                'strategy': 'wholefile'
            }
    
    def _validate_profile(self, name: str, profile: Dict[str, Any]) -> bool:
        """
        Validate a single profile.
        
        Args:
            name: Profile name
            profile: Profile configuration dictionary
            
        Returns:
            bool: True if profile is valid, False otherwise
        """
        # Check required fields
        if 'model' not in profile:
            myLogger.warning(f"Profile '{name}' missing required field: model")
            return False
        
        if 'strategy' not in profile:
            myLogger.warning(f"Profile '{name}' missing required field: strategy")
            return False
        
        # Validate strategy value
        if profile['strategy'].lower() not in self.VALID_STRATEGIES:
            myLogger.warning(
                f"Profile '{name}' has invalid strategy: {profile['strategy']}. "
                f"Valid strategies: {', '.join(self.VALID_STRATEGIES)}"
            )
            return False
        
        # Validate model (basic check - should be a non-empty string)
        if not isinstance(profile['model'], str) or not profile['model'].strip():
            myLogger.warning(f"Profile '{name}' has invalid model: {profile['model']}")
            return False
        
        return True
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Dict or None: Profile configuration or None if not found
        """
        if name in self.profiles:
            return self.profiles[name]
        
        myLogger.warning(f"Profile '{name}' not found")
        return None
    
    def get_available_profiles(self) -> List[str]:
        """
        Get a list of available profile names.
        
        Returns:
            List[str]: List of profile names
        """
        return list(self.profiles.keys())


# Singleton instance
profile_loader = ProfileLoader()