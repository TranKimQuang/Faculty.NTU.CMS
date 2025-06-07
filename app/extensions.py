from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Khởi tạo các thể hiện extension mà chưa liên kết với ứng dụng cụ thể
db = SQLAlchemy()
login_manager = LoginManager()