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
    ALIASES_PATH = Path(__file__).parent.parent / "config" / "model-aliases.yaml"
    VALID_STRATEGIES = ["wholefile", "udiff", "searchreplace"]

    def __init__(self):
        """Initialize the profile loader."""
        self.profiles = {}
        self.model_aliases = self._load_model_aliases() # Load aliases first
        self._load_profiles(ProfileType.ANALYZER, 'analyzer-profiles.yaml')
        self._load_profiles(ProfileType.COMMENTER, 'commenter-profiles.yaml')


    def _load_model_aliases(self) -> Dict[str, str]:
        """Load model aliases from the YAML configuration file."""
        if not self.ALIASES_PATH.exists():
            myLogger.warning(f"Model aliases file not found: {self.ALIASES_PATH}")
            return {}
        try:
            with open(self.ALIASES_PATH, 'r') as file:
                data = yaml.safe_load(file)
                if not isinstance(data, dict):
                    myLogger.error(f"Invalid format in model aliases file: {self.ALIASES_PATH}. Expected a dictionary.")
                    return {}
                return data if data else {}
        except Exception as e:
            myLogger.error(f"Error loading model aliases from {self.ALIASES_PATH}: {e}")
            return {}

    def _load_profiles(self, profile_type: ProfileType, filename: str) -> None:
        """
        Load profiles from the YAML configuration file.
        """
        file_path = self.PROFILES_DIR_PATH / filename
        if not file_path.exists():
            myLogger.warning(f"Profile file not found: {file_path}")
            self.profiles[profile_type] = {}
            return

        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                if not data or 'profiles' not in data or not isinstance(data['profiles'], dict):
                    myLogger.warning(f"Invalid profiles file format in {filename}. Expected 'profiles' key with a dictionary.")
                    self.profiles[profile_type] = {}
                    return

                self.profiles[profile_type] = data['profiles']
                myLogger.debug(f"Loaded {len(data['profiles'])} profiles from {filename}")

        except Exception as e:
            myLogger.error(f"Error loading profiles from {filename}: {e}")
            self.profiles[profile_type] = {}


    def get_profile(self, profile_type: ProfileType, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by name, resolving the model alias.

        Args:
            profile_type: The type of profile (Commenter or Analyzer).
            name: Profile name.

        Returns:
            Dict or None: Profile configuration with resolved model name, or None if not found.
        """
        profile_data = self.profiles.get(profile_type, {}).get(name)

        if not profile_data:
            myLogger.warning(f"Profile '{name}' not found in {profile_type.value} profiles")
            return None

        # Make a copy to avoid modifying the original loaded dict
        resolved_profile = profile_data.copy()

        # Resolve model alias
        model_alias = resolved_profile.get("model")
        if model_alias and model_alias in self.model_aliases:
            resolved_model = self.model_aliases[model_alias]
            resolved_profile["model"] = resolved_model
            myLogger.debug(f"Resolved model alias '{model_alias}' to '{resolved_model}' for profile '{name}'")
        elif model_alias:
            # If it's not an alias, assume it might be a direct model identifier
            # Add a check to ensure it looks like a valid identifier (contains '/')
            if "/" not in model_alias:
                 myLogger.warning(f"Model '{model_alias}' in profile '{name}' is not a known alias and seems to be missing a provider prefix (e.g., 'provider/model-name').")
            else:
                 myLogger.debug(f"Using direct model identifier '{model_alias}' for profile '{name}' (not found in aliases).")
        else:
             myLogger.warning(f"Profile '{name}' is missing the 'model' key.")
             # Decide if you want to return None or the profile without a model
             # return None # Option 1: Consider profile invalid without a model
             pass # Option 2: Allow profile without model (might fail later)


        # Validate strategy
        strategy = resolved_profile.get("strategy")
        if not strategy:
             myLogger.warning(f"Profile '{name}' is missing the 'strategy' key.")
        elif strategy not in self.VALID_STRATEGIES:
             myLogger.warning(f"Invalid strategy '{strategy}' in profile '{name}'. Valid strategies are: {', '.join(self.VALID_STRATEGIES)}")
             # Decide how to handle invalid strategy (e.g., return None, use default)
             # return None # Option 1: Consider profile invalid

        return resolved_profile


    def get_available_profiles(self, profile_type: ProfileType) -> List[str]:
        """
        Get a list of available profile names for a specific type.

        Returns:
            List[str]: List of profile names.
        """
        return list(self.profiles.get(profile_type, {}).keys())


# Singleton instance
profile_loader = ProfileLoader()