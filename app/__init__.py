import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager # Import từ tệp extensions mới

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    # db và login_manager được khởi tạo ở app/extensions.py
    # và giờ chúng ta liên kết chúng với ứng dụng 'app'
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User loader for Flask-Login
    # Import Model sau khi db đã được khởi tạo
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
    from app.routes.settings import settings_bp as settings

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(events, url_prefix='/admin')
    app.register_blueprint(pages, url_prefix='/admin')
    app.register_blueprint(posts, url_prefix='/admin')
    app.register_blueprint(categories, url_prefix='/admin')
    app.register_blueprint(announcements, url_prefix='/admin')
    app.register_blueprint(menus, url_prefix='/admin')
    app.register_blueprint(auth)
    app.register_blueprint(settings, url_prefix='/admin')

    # Create upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
