from app.models import User
from app.extensions import db

class UserRepository:
    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def get_by_id(id):
        return User.query.get_or_404(id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create(username, role, password):
        user = User(username=username, role=role)
        user.set_password(password)  # Giả sử model User có phương thức set_password
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user, username, role, password=None):
        user.username = username
        user.role = role
        if password:
            user.set_password(password)
        db.session.commit()
        return user

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()