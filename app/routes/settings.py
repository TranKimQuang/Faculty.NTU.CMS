from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app.extensions import db  # Đúng rồi
from app.decorators import admin_required, editor_required
from app.repositories.setting_repository import SettingRepository

settings_bp = Blueprint('settings_bp', __name__)
setting_repo = SettingRepository()


@settings_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    editing_setting = None
    if request.method == 'POST':
        key = request.form.get('key')
        value = request.form.get('value')

        if not key or not value:
            flash('Key and Value are required.', 'danger')
        else:
            existing_setting = setting_repo.get_by_key(key)  # Giờ trả về None nếu không tìm thấy
            if existing_setting:
                flash(f'Setting with key "{key}" already exists. Use edit to change it.', 'warning')
            else:
                try:
                    setting_repo.create(key, value)
                    flash('Setting created successfully.', 'success')
                except Exception as e:
                    # In lỗi ra console để debug nếu có vấn đề DB khác
                    print(f"ERROR: Failed to create setting: {e}")
                    flash(f'Error creating setting: {e}', 'danger')
                    db.session.rollback()  # Đảm bảo rollback nếu có lỗi DB
            return redirect(url_for('settings_bp.settings'))

    settings_list = setting_repo.get_all()
    return render_template('admin/settings.html', settings=settings_list, editing_setting=editing_setting)


@settings_bp.route('/settings/edit/<string:key>', methods=['GET', 'POST'])
@login_required
def edit_setting(key):
    # Lấy setting; không dùng first_or_404 ở đây vì bạn muốn kiểm soát phản hồi
    setting = setting_repo.get_by_key(key)
    if not setting:  # Xử lý trường hợp không tìm thấy setting
        flash(f'Setting with key "{key}" not found.', 'danger')
        return redirect(url_for('settings_bp.settings'))

    if request.method == 'POST':
        new_key = request.form.get('key')
        new_value = request.form.get('value')
        if not new_key or not new_value:
            flash('Key and Value are required.', 'danger')
        else:
            # Kiểm tra xem key mới đã tồn tại chưa (nếu key thay đổi)
            if new_key != key and setting_repo.get_by_key(new_key):
                flash(f'Cannot change key to "{new_key}" as it already exists.', 'danger')
            else:
                try:
                    setting_repo.update(setting, new_key, new_value)
                    flash('Setting updated successfully.', 'success')
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
    # Lấy setting; không dùng first_or_404 ở đây vì bạn muốn kiểm soát phản hồi
    setting = setting_repo.get_by_key(key)
    if not setting:  # Xử lý trường hợp không tìm thấy setting
        flash(f'Setting with key "{key}" not found.', 'danger')
    else:
        try:
            setting_repo.delete(setting)
            flash(f'Setting "{key}" deleted successfully.', 'success')
        except Exception as e:
            print(f"ERROR: Failed to delete setting: {e}")
            flash(f'Error deleting setting: {e}', 'danger')
            db.session.rollback()
    return redirect(url_for('settings_bp.settings'))
