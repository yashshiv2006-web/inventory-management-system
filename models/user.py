"""
User Model Module.

Purpose:
Represents retail system users (store managers, cashiers, administrators) who operate
the platform, create catalog items, and process transactions.

Why this file exists:
In enterprise database architectures, every business record must have an audit trail
identifying which user created or modified it. The User model establishes identity,
secures credentials using industry-standard hashing (Werkzeug), and provides a 1-to-Many
relationship with Products ('User creates Products').
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db


class User(db.Model):
    """
    Represents an authorized user account in the retail management system.

    Attributes:
        id (int): Primary key, auto-incrementing unique user ID.
        username (str): Unique username used for authentication.
        email (str): Unique email address for notifications and contact.
        password_hash (str): Securely hashed password (PBKDF2/SHA256).
        role (str): Access level ('manager', 'cashier', 'admin').
        created_at (datetime): Account creation timestamp.
    """

    __tablename__ = "users"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Unique credentials
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Role-based authorization
    role = db.Column(db.String(50), default="manager", nullable=False)

    # Audit timestamp
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # --- Relationships ---
    # 1-to-Many relationship: One User can create Many Products.
    products = db.relationship(
        "Product",
        back_populates="created_by_user",
        lazy=True,
    )

    def __init__(
        self,
        username: str,
        email: str,
        password: str = "admin123",
        role: str = "manager",
    ) -> None:
        """
        Constructor to initialize a new User account.

        Args:
            username (str): Unique login username.
            email (str): Unique email address.
            password (str, optional): Raw plain-text password to hash. Defaults to 'admin123'.
            role (str, optional): Role designation. Defaults to 'manager'.
        """
        self.username = username.strip().lower()
        self.email = email.strip().lower()
        self.set_password(password)
        self.role = role.strip()

    def set_password(self, password: str) -> None:
        """Hashes plain-text password using Werkzeug's secure hashing algorithm."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies supplied plain-text password against stored cryptographic hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes user object into a dictionary (safely excludes password hash)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "products_created_count": len(self.products) if self.products else 0,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"
