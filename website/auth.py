from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
import re
from .models import User, UserSettings, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm.exc import UnmappedInstanceError
auth = Blueprint("auth", __name__)

data = {}


def get(element_name: str) -> str | None:
    """Shorthand for request.form.get()."""

    return request.form.get(element_name)


@auth.route("/sign-in", methods=["GET", "POST"])
def login() -> str | Response:
    """
    Login view function. Renders the login page (sign_in.html)
    and gets all the values of the input elements in the form,
    gets the user in DB by username and checks the password. Logs-in the user if
    it matches, flash() an error if not. 
    """
    # data = request.form
    if request.method == "POST":

        email = get("email")
        password = get("password")
        remember_me = get("remember-me")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True if remember_me ==
                           "on" else False)
                return redirect(url_for("views.home"))
            else:
                flash("email and password do not match. Please try again",
                      category="error")
        else:
            flash("email does not exist.", category="error")

    return render_template("signin_page.html", user=current_user)


@auth.route("/logout")
@login_required
def logout() -> Response:
    """Logout view function. Logs-out the user from flask-login and redirects the user to the first_page."""
    logout_user()
    return redirect(url_for("views.home"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up() -> str | Response:
    """
    Sign up view function. Renders the sign-up page (sign_up.html) and
    if post request, gets the form elements's values, checks format of
    email address, username and both passwords. If everything checks out,
    it creates a new User in database and also a UserSettings row associated
    the User.
    """

    if request.method == "POST":
        # Get values from inputs
        email = get("email")
        username = get("username")
        first_name = get("first-name")
        last_name = get("last-name")
        password1 = get("password1")
        password2 = get("password2")
        remember_me = get("remember-me")
        promotional_emails = get("promotional-emails")

        teacher = False

        if first_name is not None:
            teacher = True

        # If it finds a user with the email address that the new user inputted,
        # it will tell them that the email already exists. Only 1 account can be
        # associated with an email.
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists", category="error")

        elif len(email) < 7:
            flash("Email address is too short", category="error")

        # The following regex is an expression that matches all emails (source: https://www.tutorialspoint.com/checking-for-valid-email-address-using-regular-expressions-in-java)
        elif email not in re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$").findall(email):
            flash("Email address does not meet standards", category="error")

        elif len(username) < 2:
            flash("Username is too short", category="error")

        elif password1 != password2:
            flash("Passwords do not match", category="error")

        # Password requirements: At least 8 characters and contains at least 1 number AND 1 special characters from below.
        elif len(password1) < 12:
            flash("Password should be min. 12 characters long", category="error")

        else:
            # Create new user filling in the inputted information
            new_user = User(
                username=username,
                first_name="" if not teacher else first_name,
                last_name="" if not teacher else last_name,
                description="",
                email=email,
                password=generate_password_hash(password1, method="pbkdf2:sha256"),
                phone_number="",
                two_FA=False,
                account_type="student" if not teacher else "teacher",
            )

            db.session.add(new_user)
            db.session.commit()

            # To make the UserSettings associated with the User,
            # it is necessary to get the User's id (primary key)
            # Since SQLAlchemy auto-generates an id in the DB, it is necessary to add and commit
            # the new user, so that the id is generated.
            new_user = User.query.filter_by(email=email).first()
            new_settings = UserSettings(
                user_id=new_user.id,
                security_emails=True,
                activity_emails=True,
                promotional_emails=True if promotional_emails == "on" else False
            )

            db.session.add(new_settings)
            db.session.commit()

            login_user(new_user, remember=True if remember_me ==
                       "on" else False)
            return redirect(url_for("views.home"))

    return render_template("signup_page.html", user=current_user)


@auth.route("/account_deletion", methods=["POST", "GET"])
def delete_account() -> str | Response:
    """
    Delete account view function. Renders the delete account page and
    checks inputted information. If it matches, it removes the User's settings,
    the users notifications and the account itself from the DB and redirects the user to first_page.html.
    """
    if request.method == "POST":
        user = User.query.filter_by(id=current_user.id).first()
        password = get("password")
        if check_password_hash(user.password, password):
            db.session.delete(UserSettings.query.filter_by(
                user_id=current_user.id).first())

            # Since the user might not have any of the things listed after when they delete their account,
            # it is possible that the line of code throws an UnmappedInstanceError, hence the try except.
            from .models import Appointment, Message, Post, Comment, PostReaction, CommentReaction
            for model in (Notification, Appointment, Message, Post, Comment, PostReaction, CommentReaction):
                try:
                    model.query.filter_by(user_id=current_user.id).delete()
                except UnmappedInstanceError:
                    continue

            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("views.home"))
        else:
            flash("Incorrect password", category="error")

    return render_template("delete_account.html", user=current_user)


@auth.route("/save", methods=["POST"])
@login_required
def save_information() -> Response:
    """
    This function saves the account information
    that the user might have changed in the account.html page.
    """
    # email is immutable, the user cannot change it because the input is readonly.
    email = get("email")

    user = User.query.filter_by(email=email).first()

    user.username = get("username")
    user.first_name = get("first-name")
    user.last_name = get("last-name")
    user.gender = get("gender")
    user.birthday = get("birthday")
    user.description = get("description")
    user.phone_number = get("number")
    db.session.commit()

    return redirect(url_for("views.account"))


@auth.route("/forgot_password", methods=["POST", "GET"])
def forgot_password() -> str:
    """
    Unfinished function. Renders the forget_password.html page.
    """
    data["email"] = get("email")
    try:
        User.query.filter_by(email=data["email"]).first()
    except KeyError:
        flash("Email address doesn't exist", category="error")

    return render_template("forgot_password.html", user=current_user)


@auth.route("/verify_code", methods=["POST", "GET"])
def verify_code() -> str:
    """
    Renders the verify_code.html page.
    """
    return render_template("verify_code.html", user=current_user)


@auth.route("/reset_password", methods=["POST", "GET"])
def reset_password() -> str:
    """
    Unfinished function. Similar to auth.change_password (next function).
    Renders the reset_password.html page and would let the user change their password
    after having verified their identity by sending them an verification code via email.
    """
    if request.method == "POST":
        # email = get("email")
        password1 = get("password1")
        password2 = get("password2")

        if password1 != password2:
            flash("Passwords do not match", category="error")
        else:
            user = User.query.filter_by(email=data["email"]).first()
            user.password = generate_password_hash(password1, method="sha256")
            db.session.commit()

    return render_template("reset_password.html", user=current_user)


@auth.route("/change_password", methods=["POST", "GET"])
def change_password() -> str:
    """
    Renders the change_password.html page from the account.html page,
    which asks for the user's current password and their new password.
    If everything checks out, the old password is replaced by the new one.
    """
    if request.method == "POST":
        user = User.query.filter_by(email=current_user.email).first()

        password = get("password")
        if check_password_hash(user.password, password):
            password1 = get("password1")
            password2 = get("password2")
            if password1 != password2:
                flash("New passwords do not match", category="error")

            elif len(password1) < 7 or not any(chr.isdigit() for chr in password1) or not any(chr in "@&#?!*%_-" for chr in password1):
                flash(
                    "Password should be min. 8 characters long and have at least a number and a special character", category="error")

            else:
                user.password = generate_password_hash(
                    password1, method="sha256")
                db.session.commit()
            return render_template("account.html", user=current_user)

        else:
            flash("Incorrect password", category="error")

    return render_template("change_password.html", user=current_user)
