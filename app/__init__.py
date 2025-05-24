import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User loader for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes.main import main
    from .routes.admin import admin
    from .routes.events import events
    from .routes.pages import pages
    from .routes.posts import posts
    from .routes.categories import categories
    from .routes.announcements import announcements
    from .routes.menus import menus
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(events, url_prefix='/admin')
    app.register_blueprint(pages, url_prefix='/admin')
    app.register_blueprint(posts, url_prefix='/admin')
    app.register_blueprint(categories, url_prefix='/admin')
    app.register_blueprint(announcements, url_prefix='/admin')
    app.register_blueprint(menus, url_prefix='/admin')
    app.register_blueprint(auth)

    # Create upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create database tables
    with app.app_context():
        db.create_all()

    return app