"""
Authentication & Authorization Routes Module.

Purpose:
Handles user login, credential verification using Werkzeug password hashing,
session creation, and sign-out actions.
"""

from typing import Any
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/auth/login", methods=["GET", "POST"])
def auth_login() -> Any:
    """Authenticates users via credentials stored in the SQLite database."""
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        # Query user from SQLite database
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["logged_in"] = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username.title()}! ({user.role})", "success")
            return redirect(url_for("web_bp.dashboard"))
        else:
            flash("Invalid credentials! Try demo account: admin / admin123", "danger")

    return render_template("login.html")


@auth_bp.route("/auth/logout", methods=["GET"])
def auth_logout() -> Any:
    """Terminates session and redirects to sign-in."""
    session.clear()
    flash("Successfully signed out.", "info")
    return redirect(url_for("web_bp.login"))
