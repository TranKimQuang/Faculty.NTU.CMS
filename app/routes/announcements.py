from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required, editor_required
from app.repositories.announcement_repository import AnnouncementRepository
from datetime import datetime
import os
from werkzeug.utils import secure_filename

announcements = Blueprint('announcements', __name__)

# Khởi tạo repository
announcement_repo = AnnouncementRepository()

@announcements.route('/announcements', methods=['GET', 'POST'])
@login_required
def manage_announcements():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')  # Sửa lỗi: bỏ dấu phẩy thừa
        created_by = current_user.id

        if not title or not content or not start_date or not end_date:
            flash('All fields are required.', 'danger')
        else:
            announcement = announcement_repo.create(title, content, start_date, end_date)
            flash('Announcement created successfully!', 'success')
            return redirect(url_for('announcements.manage_announcements'))

    announcements = announcement_repo.get_all()
    return render_template('admin/announcements.html', announcements=announcements)

@announcements.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    announcement = announcement_repo.get_by_id(id)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        image = request.files.get('image')

        if not title or not content or not start_date or not end_date:
            flash('All fields are required.', 'danger')
        else:
            announcement = announcement_repo.update(announcement, title, content, start_date, end_date)
            # Xử lý image (nếu cần) vẫn để trong route vì chưa có trong repository
            db.session.commit()  # Commit nếu có thay đổi từ image
            flash('Announcement updated successfully!', 'success')
            return redirect(url_for('announcements.manage_announcements'))

    announcements = announcement_repo.get_all()
    return render_template('admin/announcements.html', announcements=announcements, editing_announcement=announcement)

@announcements.route('/announcements/delete/<int:id>')
@admin_required
def delete_announcement(id):
    announcement = announcement_repo.get_by_id(id)
    announcement_repo.delete(announcement)
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('announcements.manage_announcements'))