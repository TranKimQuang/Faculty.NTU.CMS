from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models import Announcement
from datetime import datetime
import os
from werkzeug.utils import secure_filename

announcements = Blueprint('announcements', __name__)


@announcements.route('/announcements', methods=['GET', 'POST'])
@admin_required
def manage_announcements():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date'),
        created_by = current_user.id

        if not title or not content or not start_date or not end_date:
            flash('All fields are required.', 'danger')
        else:
            announcement = Announcement(title=title, content=content,
                                        start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                                        end_date=datetime.strptime(end_date, '%Y-%m-%d'))

            db.session.add(announcement)
            db.session.commit()
            flash('Announcement created successfully!', 'success')
            return redirect(url_for('announcements.manage_announcements'))

    announcements = Announcement.query.order_by(Announcement.start_date.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)


@announcements.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)

    if request.method == 'POST':
        announcement.title = request.form.get('title')
        announcement.content = request.form.get('content')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        image = request.files.get('image')

        if not announcement.title or not announcement.content or not start_date or not end_date:
            flash('All fields are required.', 'danger')
        else:
            announcement.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            announcement.end_date = datetime.strptime(end_date, '%Y-%m-%d')

            db.session.commit()
            flash('Announcement updated successfully!', 'success')
            return redirect(url_for('announcements.manage_announcements'))

    announcements = Announcement.query.order_by(Announcement.start_date.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements, editing_announcement=announcement)


@announcements.route('/announcements/delete/<int:id>')
@admin_required
def delete_announcement(id):
    if current_user.role != 'admin':
        flash('You do not have permission to delete announcements.', 'danger')
        return redirect(url_for('announcements.manage_announcements'))

    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('announcements.manage_announcements'))