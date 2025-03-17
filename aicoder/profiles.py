# profiles.py
import os
from enum import Enum

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from .utils.logger import myLogger


class ProfileType(Enum):
    COMMENTER = "commenter"
    ANALYZER = "analyzer"


class ProfileLoader:
    """
    Handles loading and validating profiles from YAML configuration.
    
    Profiles define preset combinations of model and strategy settings
    that can be selected via the CLI.
    """
    
    PROFILES_DIR_PATH = Path(__file__).parent.parent / "config" / "profiles/"
    VALID_STRATEGIES = ["wholefile", "udiff", "searchreplace"]
    
    def __init__(self):
        """Initialize the profile loader."""
        self.profiles = {}
        self._load_profiles(ProfileType.ANALYZER, 'analyzer-profiles.yaml')
        self._load_profiles(ProfileType.COMMENTER, 'commenter-profiles.yaml')

    def _load_profiles(self, profile_type: ProfileType, filename: str) -> None:
        """
        Load profiles from the YAML configuration file.
        """

        # Load profiles from file
        with open(self.PROFILES_DIR_PATH / filename, 'r') as file:
            data = yaml.safe_load(file)
            if not data or 'profiles' not in data:
                myLogger.warning("Invalid profiles file format.")

            self.profiles[profile_type] = data['profiles']

    # def _create_default_profiles(self) -> None:
    #     """Create default profiles configuration file."""
    #     default_profiles = {
    #         'profiles': {
    #             'default': {
    #                 'model': 'openrouter/google/gemini-2.0-flash-exp:free',
    #                 'strategy': 'wholefile'
    #             },
    #             'udiff': {
    #                 'model': 'openrouter/anthropic/claude-3.5-sonnet',
    #                 'strategy': 'udiff'
    #             },
    #             'searchreplace': {
    #                 'model': 'openrouter/qwen/qwen-2.5-coder-32b-instruct',
    #                 'strategy': 'searchreplace'
    #             }
    #         }
    #     }
    #
    #     with open(self.PROFILES_PATH, 'w') as file:
    #         yaml.dump(default_profiles, file, default_flow_style=False)
    

    def get_profile(self, profile_type: ProfileType, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Dict or None: Profile configuration or None if not found
        """
        if name in self.profiles[profile_type]:
            return self.profiles[profile_type][name]
        
        myLogger.warning(f"Profile '{name}' not found in {profile_type} profiles")
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