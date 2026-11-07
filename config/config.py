"""
Configuration Module for Retail Stock Optimization and Sales Intelligence Platform.

Why this file exists:
In professional software development, configuration parameters (such as database URLs,
secret keys, and debug flags) should be decoupled from the core application logic.
This adheres to the "Twelve-Factor App" methodology and makes it easy to switch
between Development, Testing, and Production environments without modifying code.
"""

import os
from typing import Type


class Config:
    """
    Base configuration class containing common settings for all environments.
    Subclasses can override or extend these settings as needed.
    """

    # Secret key used by Flask for session security and cryptographic signing.
    # In production, this should always be loaded from an environment variable.
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-for-retail-platform")

    # Base directory of the project, used to construct absolute file paths.
    BASE_DIR: str = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Path to the SQLite database file stored locally in the instance or root folder.
    # SQLite is serverless, zero-configuration, and stores data in a single file,
    # making it ideal for educational projects and Viva demonstrations.
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'retail_stock.db')}"
    )

    # Disable SQLAlchemy event system tracking modifications to save memory.
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Default inventory threshold for triggering low stock alerts across the system.
    DEFAULT_LOW_STOCK_THRESHOLD: int = 10


class DevelopmentConfig(Config):
    """
    Configuration for local development. Enables debug mode and detailed error logging.
    """
    DEBUG: bool = True
    TESTING: bool = False


class TestingConfig(Config):
    """
    Configuration for automated unit tests. Uses an in-memory SQLite database
    so tests run quickly in isolation without touching real data on disk.
    """
    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


# Dictionary mapping environment names to configuration classes for easy lookup.
config_by_name: dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
