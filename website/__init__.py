from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
from typing import Any


# Set db name
db: SQLAlchemy = SQLAlchemy()
DB_NAME: str = "database.db"


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    app.config["SECRET_KEY"] = "placeholder key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User
    create_database(app)

    login_manager: LoginManager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # This function is needed even though the code editor says it's not used. Do not remove
    # http://flask-login.readthedocs.io/#how-it-works
    @login_manager.user_loader
    def load_user(id) -> Any:
        return User.query.get(int(id))

    return app


def create_database(app: Flask) -> None:
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
