import functools
import re

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from paralogia.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("index"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
        )


@bp.route("/signup", methods=("GET", "POST"))
def signup():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    session.pop('_flashes', None)
    if request.method == "POST":
        print('hi')
        username = request.form["username"]
        password = request.form["password"]

        print(username)
        print(password)
        
        db = get_db()
        error = None

        if len(username) > 16:
            error = "Your username is too big, try to keep it under 16 characters."

        # Minimum eight characters, at least one letter and one number
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            error = "Passwords must have at least eight characters and contain a number."

        if not re.match(r"^[A-Za-z0-9]{4,}$",username):
            error = "Usernames must have at least 4 characters and no symbols."

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        session.pop('_flashes', None)
        flash(error)

    return render_template("auth/signup.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect username or password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["user_id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))


@bp.route("/change_password", methods=("GET", "POST"))
@login_required
def change_password():

    if request.method == "POST":
        db = get_db()
        error = None

        username = g.user['username']
        password = request.form['password']
        new_password = request.form['newPassword']
        
        user = db.execute(
        "SELECT password FROM user WHERE username = ?", (username,)
        ).fetchone()

        if not check_password_hash(user['password'],password):
            error = "Incorrect password."

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", new_password):
            error = "Passwords must have at least eight characters and contain a number."

        if error is None:
            db.execute(
                "UPDATE user SET password=? WHERE username=?", (generate_password_hash(new_password),username)
            )
            db.commit()


            session.clear()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/change_password.html")


@bp.route("/delete_account", methods=("GET", "POST"))
@login_required
def delete_account():

    if request.method == "POST":
        db = get_db()
        error = None

        username = g.user['username']
        password = request.form['password']
        password_confirm = request.form['passwordConfirm']

        print(username)
        print(password)
        print(password_confirm)

        user = db.execute(
        "SELECT password FROM user WHERE username = ?", (username,)
        ).fetchone()

        if password != password_confirm:
            error = "The password was not confirmed correctly."

        if not check_password_hash(user['password'],password):
            error = "Incorrect password."

        if error is None:

            db.execute(
                "DELETE FROM user WHERE username = ? ", (username,)
            )
            db.commit()

            session.clear()
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/delete_account.html")
