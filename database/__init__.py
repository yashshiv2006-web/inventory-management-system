"""
Database package initialization.
Exports the shared db instance and the init_db helper function.
"""

from .db import db, init_db

__all__ = ["db", "init_db"]
