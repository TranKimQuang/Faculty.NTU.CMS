from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app
from flask_login import login_required
from app.extensions import db
from app.decorators import admin_required, editor_required
from app.repositories.setting_repository import SettingRepository
from werkzeug.utils import secure_filename
import os

# Tạo blueprint cho settings
settings_bp = Blueprint('settings_bp', __name__)

# Khởi tạo repository
setting_repo = SettingRepository()

# Dictionary ánh xạ key sang tên hiển thị
FIELD_NAMES = {
    'site_name': 'Tên trang web',
    'site_title': 'Tiêu đề trang',
    'email': 'Email',
    'phone': 'Số điện thoại',
    'site_welcome': 'Lời chào',
    'gradient_start_color': 'Màu gradient bắt đầu',
    'gradient_end_color': 'Màu gradient kết thúc',
    'site_logo_url': 'Logo',
    'address': 'Địa chỉ'
}

@settings_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """
    Xử lý trang quản lý cài đặt: Tạo hoặc cập nhật cài đặt khi POST, hiển thị danh sách khi GET.
    """
    if request.method == 'POST':
        key = request.form.get('key')
        if key:
            if key == 'site_logo_url':
                site_logo_url = request.files.get('site_logo_url')
                if site_logo_url and site_logo_url.filename:
                    filename = secure_filename(site_logo_url.filename)
                    upload_folder = os.path.join(current_app.root_path, 'static/uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    image_path = os.path.join(upload_folder, filename)
                    site_logo_url.save(image_path)
                    new_value = f'uploads/{filename}'
                else:
                    existing_setting = setting_repo.get_by_key(key)
                    new_value = existing_setting.value if existing_setting else ''
            else:
                new_value = request.form.get(key)
                # Validation cơ bản
                if not new_value:
                    flash(f'Vui lòng nhập giá trị cho {FIELD_NAMES.get(key, key)}', 'danger')
                    return redirect(url_for('settings_bp.settings'))
                if key == 'email' and '@' not in new_value:
                    flash('Email phải chứa ký tự "@"', 'danger')
                    return redirect(url_for('settings_bp.settings'))
                if key == 'phone' and not new_value.isdigit():
                    flash('Số điện thoại phải là số', 'danger')
                    return redirect(url_for('settings_bp.settings'))

            existing_setting = setting_repo.get_by_key(key)
            if existing_setting:
                try:
                    setting_repo.update(existing_setting, key, new_value)
                    flash(f'{FIELD_NAMES.get(key, key)} đã được cập nhật!', 'success')
                except Exception as e:
                    print(f"ERROR: Failed to update setting: {e}")
                    flash(f'Error updating setting: {e}', 'danger')
                    db.session.rollback()
            else:
                try:
                    setting_repo.create(key, new_value)
                    flash(f'{FIELD_NAMES.get(key, key)} đã được tạo!', 'success')
                except Exception as e:
                    print(f"ERROR: Failed to create setting: {e}")
                    flash(f'Error creating setting: {e}', 'danger')
                    db.session.rollback()
            return redirect(url_for('settings_bp.settings'))

    settings_list = setting_repo.get_all()
    # Kiểm tra cấu trúc dữ liệu
    if not isinstance(settings_list, list) or not all(hasattr(s, 'key') and hasattr(s, 'value') for s in settings_list):
        print("Error: settings_list is not a list of objects with 'key' and 'value' attributes:", settings_list)
        settings_list = []  # Gán giá trị mặc định nếu lỗi
    return render_template('admin/settings.html', settings=settings_list)

@settings_bp.route('/settings/edit/<string:key>', methods=['GET', 'POST'])
@login_required
def edit_setting(key):
    """
    Xử lý chỉnh sửa cài đặt: Hiển thị form chỉnh sửa khi GET, cập nhật khi POST.
    """
    setting = setting_repo.get_by_key(key)
    if not setting:
        flash(f'Setting with key "{key}" not found.', 'danger')
        return redirect(url_for('settings_bp.settings'))

    if request.method == 'POST':
        if key == 'site_logo_url':
            site_logo_url = request.files.get('site_logo_url')
            if site_logo_url and site_logo_url.filename:
                filename = secure_filename(site_logo_url.filename)
                upload_folder = os.path.join(current_app.root_path, 'static/uploads')
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                site_logo_url.save(image_path)
                new_value = f'uploads/{filename}'
                if setting.value and os.path.exists(os.path.join(upload_folder, setting.value.split('/')[-1])):
                    os.remove(os.path.join(upload_folder, setting.value.split('/')[-1]))
            else:
                new_value = setting.value
        else:
            new_value = request.form.get(key)
            if not new_value:
                flash(f'Vui lòng nhập giá trị cho {FIELD_NAMES.get(key, key)}', 'danger')
                return redirect(url_for('settings_bp.edit_setting', key=key))
            if key == 'email' and '@' not in new_value:
                flash('Email phải chứa ký tự "@"', 'danger')
                return redirect(url_for('settings_bp.edit_setting', key=key))
            if key == 'phone' and not new_value.isdigit():
                flash('Số điện thoại phải là số', 'danger')
                return redirect(url_for('settings_bp.edit_setting', key=key))

        try:
            setting_repo.update(setting, key, new_value)
            flash(f'{FIELD_NAMES.get(key, key)} đã được cập nhật!', 'success')
            return redirect(url_for('settings_bp.settings'))
        except Exception as e:
            print(f"ERROR: Failed to update setting: {e}")
            flash(f'Error updating setting: {e}', 'danger')
            db.session.rollback()

    settings_list = setting_repo.get_all()
    return render_template('admin/settings.html', settings=settings_list, editing_setting=setting)

@settings_bp.route('/settings/delete/<string:key>')
@admin_required
def delete_setting(key):
    """
    Xử lý xóa cài đặt: Xóa setting nếu tồn tại, hiển thị thông báo.
    """
    setting = setting_repo.get_by_key(key)
    if not setting:
        flash(f'Setting with key "{key}" not found.', 'danger')
    else:
        if setting.key == 'site_logo_url' and setting.value:
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            if os.path.exists(os.path.join(upload_folder, setting.value.split('/')[-1])):
                os.remove(os.path.join(upload_folder, setting.value.split('/')[-1]))
        try:
            setting_repo.delete(setting)
            flash(f'Cài đặt "{FIELD_NAMES.get(key, key)}" đã được xóa!', 'success')
        except Exception as e:
            print(f"ERROR: Failed to delete setting: {e}")
            flash(f'Error deleting setting: {e}', 'danger')
            db.session.rollback()
    return redirect(url_for('settings_bp.settings'))