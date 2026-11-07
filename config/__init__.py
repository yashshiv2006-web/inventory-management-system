"""
Configuration package initialization.
Exports Config, DevelopmentConfig, TestingConfig, and config_by_name dictionary.
"""

from .config import Config, DevelopmentConfig, TestingConfig, config_by_name

__all__ = ["Config", "DevelopmentConfig", "TestingConfig", "config_by_name"]
