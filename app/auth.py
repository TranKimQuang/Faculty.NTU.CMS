from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash # Đảm bảo cả hai đều được import

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_app.config.get('LOGIN_ENABLED', True):
        flash('Tính năng đăng nhập hiện đang được bảo trì. Vui lòng thử lại sau.', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting login with username: {username}")
        user = User.query.filter_by(username=username).first()

        if user:
            print(f"User found: {user.username}, role: {user.role}")
            print(f"Hash in DB: {user.password_hash}")

            # ****** DEBUGGING CỰC KỲ CHI TIẾT TẠI ĐÂY ******
            print(f"DEBUG: Type of 'password' input: {type(password)}")
            print(f"DEBUG: Representation of 'password' input: {repr(password)}") # In raw representation
            print(f"DEBUG: Length of 'password' input: {len(password)}")

            # Chuyển đổi mật khẩu thành bytes và rồi decode lại để kiểm tra encoding (chỉ gỡ lỗi)
            try:
                password_bytes = password.encode('utf-8')
                password_decoded_back = password_bytes.decode('utf-8')
                print(f"DEBUG: Decoded password (utf-8): {repr(password_decoded_back)}")
                print(f"DEBUG: Length of decoded password: {len(password_decoded_back)}")
            except Exception as e:
                print(f"DEBUG: Error encoding/decoding password: {e}")
            # ****** END DEBUGGING ******

            is_password_correct = check_password_hash(user.password_hash, password)
            print(f"Result of check_password_hash: {is_password_correct}")

            hashed_input_password_for_debug = generate_password_hash(password)
            print(f"Hash of input password (debug): {hashed_input_password_for_debug}")

            if is_password_correct:
                print("Password check passed (from debug variable)")
                login_user(user)
                flash('Login successful!')
                return redirect(url_for('main.admin_dashboard'))
            else:
                print("Password check failed (from debug variable)")
                flash('Invalid username or password.')
        else:
            print(f"No user found for username: {username}")
            flash('Invalid username or password.')
    return render_template('admin/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))