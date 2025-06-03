from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.decorators import admin_required
from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash # Đảm bảo cả hai đều được import

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
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
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists.', 'danger')
                return redirect(url_for('auth.users'))
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully.', 'success')
        elif 'update' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get_or_404(user_id)
            user.username = request.form.get('username')
            user.role = request.form.get('role')
            password = request.form.get('password')
            if password:
                user.set_password(password)
            db.session.commit()
            flash('User updated successfully.', 'success')
        elif 'delete' in request.form:
            user_id = request.form.get('user_id')
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully.', 'success')
        return redirect(url_for('auth.users'))

    users = User.query.all()
    return render_template('auth/users.html', users=users)