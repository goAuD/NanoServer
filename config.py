"""
NanoServer - Configuration Module
Handles saving/loading user preferences to JSON file.
Cross-platform compatible (Windows/Linux/macOS).
"""

import json
import os
import logging
import functools
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Decorator Factory for Execution Tracing ---
def trace_execution(func):
    """Decorator that logs function entry/exit with execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"→ Entering {func.__name__}")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.debug(f"← Exiting {func.__name__} ({elapsed:.3f}s)")
            return result
        except Exception as e:
            logger.error(f"✗ {func.__name__} raised {type(e).__name__}: {e}")
            raise
    return wrapper


class Config:
    """
    Configuration manager that persists settings to a JSON file.
    Stores: last project folder, port, window geometry.
    """
    
    DEFAULT_CONFIG = {
        "last_project": "",
        "port": 8000,
        "window_geometry": "700x600",
    }
    
    def __init__(self, config_dir: str = None):
        """
        Initialize config manager.
        
        Args:
            config_dir: Directory to store config file. 
                        Defaults to user's home directory.
        """
        if config_dir is None:
            # Cross-platform: use home directory
            config_dir = Path.home() / ".nanoserver"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self._data = self.DEFAULT_CONFIG.copy()
        
        self._ensure_dir()
        self.load()
    
    def _ensure_dir(self):
        """Create config directory if it doesn't exist."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Could not create config directory: {e}")
    
    @trace_execution
    def load(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            logger.info("No config file found, using defaults")
            return self._data
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with defaults (in case new keys were added)
                self._data = {**self.DEFAULT_CONFIG, **loaded}
                logger.info(f"Loaded config from {self.config_file}")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            self._data = self.DEFAULT_CONFIG.copy()
        
        return self._data
    
    @trace_execution
    def save(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved config to {self.config_file}")
            return True
        except OSError as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get a config value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set a config value and auto-save."""
        self._data[key] = value
        self.save()
    
    @property
    def last_project(self) -> str:
        return self._data.get("last_project", "")
    
    @last_project.setter
    def last_project(self, value: str):
        self.set("last_project", value)
    
    @property
    def port(self) -> int:
        return self._data.get("port", 8000)
    
    @port.setter
    def port(self, value: int):
        self.set("port", value)
