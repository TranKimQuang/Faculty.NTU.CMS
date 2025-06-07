from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.decorators import admin_required
from app.repositories.user_repository import UserRepository
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# Khởi tạo repository
user_repo = UserRepository()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_repo.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    if request.method == 'POST':
        if 'create' in request.form:
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            existing_user = user_repo.get_by_username(username)
            if existing_user:
                flash('Username already exists.', 'danger')
                return redirect(url_for('auth.users'))
            user_repo.create(username, role, password)
            flash('User created successfully.', 'success')
        elif 'update' in request.form:
            user_id = request.form.get('user_id')
            user = user_repo.get_by_id(user_id)
            username = request.form.get('username')
            role = request.form.get('role')
            password = request.form.get('password')
            user_repo.update(user, username, role, password)
            flash('User updated successfully.', 'success')
        elif 'delete' in request.form:
            user_id = request.form.get('user_id')
            user = user_repo.get_by_id(user_id)
            user_repo.delete(user)
            flash('User deleted successfully.', 'success')
        return redirect(url_for('auth.users'))

    users = user_repo.get_all()
    return render_template('auth/users.html', users=users)