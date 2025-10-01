#!/usr/bin/env python3
"""
Configuration management for Timestamp Adjuster.
Handles loading configuration from base config, user config, environment variables, and defaults.

Configuration Priority (highest to lowest):
1. Command line arguments
2. Environment variables
3. User configuration file (config.user.yaml) - git ignored
4. Legacy configuration files (config.yaml) - for backward compatibility
5. Base configuration file (config.base.yaml) - git tracked defaults
6. Hardcoded defaults
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class Config:
    """Configuration manager for timestamp adjuster."""
    
    def __init__(self, config_file: Optional[str] = None, ignore_user_config: bool = False, test_mode: bool = False):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to config file. If None, uses default locations.
            ignore_user_config: If True, skips loading user configuration (useful for tests)
            test_mode: If True, only loads the specified config file and defaults (for isolated testing)
        """
        self.config_data = {}
        self.ignore_user_config = ignore_user_config
        self.test_mode = test_mode
        self.load_config(config_file)
    
    def load_config(self, config_file: Optional[str] = None):
        """
        Load configuration from base config, user config, environment variables, and defaults.
        Priority: Environment vars > User config > Legacy config > Base config > Hardcoded defaults
        """
        # Start with hardcoded defaults
        self.config_data = self._get_defaults()
        
        # In test mode, only load the specified config file
        if self.test_mode:
            if config_file and Path(config_file).exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        test_config = yaml.safe_load(f) or {}
                    self._merge_config(self.config_data, test_config)
                    print(f"Loaded test configuration from: {config_file}")
                except Exception as e:
                    print(f"Warning: Could not load test config file {config_file}: {e}")
            return
        
        # Load base configuration (application defaults)
        base_config_path = self._find_base_config()
        if base_config_path and base_config_path.exists():
            try:
                with open(base_config_path, 'r', encoding='utf-8') as f:
                    base_config = yaml.safe_load(f) or {}
                self._merge_config(self.config_data, base_config)
                print(f"Loaded base configuration from: {base_config_path}")
            except Exception as e:
                print(f"Warning: Could not load base config file {base_config_path}: {e}")
        
        # Load legacy config for backward compatibility (lower priority than user config)
        legacy_config_path = self._find_legacy_config()
        if legacy_config_path and legacy_config_path.exists():
            try:
                with open(legacy_config_path, 'r', encoding='utf-8') as f:
                    legacy_config = yaml.safe_load(f) or {}
                self._merge_config(self.config_data, legacy_config)
                print(f"Loaded legacy configuration from: {legacy_config_path}")
                print("Warning: Legacy config files are deprecated. Consider migrating to config.user.yaml")
            except Exception as e:
                print(f"Warning: Could not load legacy config file {legacy_config_path}: {e}")
        
        # Load user configuration (overrides legacy config) - skip if ignore_user_config is True
        if not self.ignore_user_config:
            user_config_path = self._find_user_config(config_file)
            if user_config_path and user_config_path.exists():
                try:
                    with open(user_config_path, 'r', encoding='utf-8') as f:
                        user_config = yaml.safe_load(f) or {}
                    self._merge_config(self.config_data, user_config)
                    print(f"Loaded user configuration from: {user_config_path}")
                except Exception as e:
                    print(f"Warning: Could not load user config file {user_config_path}: {e}")
        
        # Override with environment variables
        self._load_env_vars()
    
    def _find_base_config(self) -> Optional[Path]:
        """Find base configuration file."""
        possible_locations = [
            Path("config.base.yaml"),  # Current directory
            Path("config.base.yml"),   # Alternative extension
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None
    
    def _find_user_config(self, config_file: Optional[str] = None) -> Optional[Path]:
        """Find user configuration file."""
        if config_file:
            return Path(config_file)
        
        # Check in order of preference
        possible_locations = [
            Path("config.user.yaml"),  # Current directory
            Path("config.user.yml"),   # Alternative extension
            Path.home() / ".config" / "timestamp-adjuster" / "config.yaml",  # User config dir
            Path.home() / ".timestamp-adjuster.yaml",  # User home dir
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None
    
    def _find_legacy_config(self) -> Optional[Path]:
        """Find legacy configuration files for backward compatibility."""
        possible_locations = [
            Path("config.yaml"),  # Current directory
            Path("config.yml"),   # Alternative extension
            Path("timestamp-adjuster.yaml"),  # Current directory alternative
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "timestamp": {
                "input_formats": [
                    {
                        "pattern": r'\[(\d{2}):(\d{2}):(\d{2})\]',
                        "name": "bracketed_hms",
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": True
                    },
                    {
                        "pattern": r'(\d{2}):(\d{2}):(\d{2})',
                        "name": "simple_hms", 
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": True
                    },
                    {
                        "pattern": r'\[(\d{1,2}):(\d{2}):(\d{2})\]',
                        "name": "bracketed_hms_flex",
                        "groups": ["hours", "minutes", "seconds"],
                        "enabled": False
                    }
                ],
                "output_format": "[{hours:02d}:{minutes:02d}:{seconds:02d}]",
                "default_format": "bracketed_hms"
            },
            "files": {
                "input_dir": "inputs",
                "output_dir": "outputs", 
                "encoding": "utf-8",
                "create_backup": False
            },
            "output_naming": {
                "template": "{basename}_{sign}{adjustment}s{extension}",
                "positive_sign": "plus",
                "negative_sign": "minus"
            },
            "processing": {
                "negative_handling": "zero",
                "preserve_formatting": True
            }
        }
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Timestamp format override
        if env_format := os.getenv("TIMESTAMP_FORMAT"):
            self.config_data["timestamp"]["output_format"] = env_format
        
        # Input/output directories
        if env_input_dir := os.getenv("TIMESTAMP_INPUT_DIR"):
            self.config_data["files"]["input_dir"] = env_input_dir
            
        if env_output_dir := os.getenv("TIMESTAMP_OUTPUT_DIR"):
            self.config_data["files"]["output_dir"] = env_output_dir
        
        # File encoding
        if env_encoding := os.getenv("TIMESTAMP_ENCODING"):
            self.config_data["files"]["encoding"] = env_encoding
    
    def get(self, key_path: str, default=None):
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path like "timestamp.output_format"
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_timestamp_formats(self) -> List[Dict[str, Any]]:
        """Get list of enabled timestamp input formats."""
        all_formats = self.get("timestamp.input_formats", [])
        # Filter to only return enabled formats
        enabled_formats = [fmt for fmt in all_formats if fmt.get("enabled", True)]
        return enabled_formats
    
    def get_all_timestamp_formats(self) -> List[Dict[str, Any]]:
        """Get list of all timestamp input formats (including disabled ones)."""
        return self.get("timestamp.input_formats", [])
    
    def get_output_format(self) -> str:
        """Get timestamp output format template."""
        return self.get("timestamp.output_format", "[{hours:02d}:{minutes:02d}:{seconds:02d}]")
    
    def get_input_dir(self) -> str:
        """Get default input directory."""
        return self.get("files.input_dir", "inputs")
    
    def get_output_dir(self) -> str:
        """Get default output directory."""
        return self.get("files.output_dir", "outputs")
    
    def get_encoding(self) -> str:
        """Get file encoding."""
        return self.get("files.encoding", "utf-8")
    
    def get_output_template(self) -> str:
        """Get output filename template."""
        return self.get("output_naming.template", "{basename}_{sign}{adjustment}s{extension}")
    
    def get_positive_sign(self) -> str:
        """Get positive adjustment sign."""
        return self.get("output_naming.positive_sign", "plus")
    
    def get_negative_sign(self) -> str:
        """Get negative adjustment sign."""
        return self.get("output_naming.negative_sign", "minus")


# Global config instance
_config_instance = None

def get_config(config_file: Optional[str] = None) -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None or config_file is not None:
        _config_instance = Config(config_file)
    return _config_instance
