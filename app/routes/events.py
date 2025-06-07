from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required, editor_required
from app.repositories.event_repository import EventRepository
from datetime import datetime
import os
from werkzeug.utils import secure_filename

events = Blueprint('events', __name__)

# Khởi tạo repository
event_repo = EventRepository()

@events.route('/events', methods=['GET', 'POST'])
@login_required
def manage_events():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        image = request.files.get('image')
        created_by = current_user.id

        if not title or not description or not event_date or not location:
            flash('All fields are required.', 'danger')
        else:
            image_path = None
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_path = f'uploads/{filename}'

            event = event_repo.create(title, description, event_date, location, image_path)
            flash('Event created successfully!', 'success')
            return redirect(url_for('events.manage_events'))

    events = event_repo.get_all()
    return render_template('admin/events.html', events=events)

@events.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = event_repo.get_by_id(id)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        image = request.files.get('image')

        if not title or not description or not event_date or not location:
            flash('All fields are required.', 'danger')
        else:
            image_path = event.image  # Giữ ảnh cũ nếu không thay đổi
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_path = f'uploads/{filename}'
                # Xóa ảnh cũ nếu tồn tại
                if event.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1])):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1]))

            event_repo.update(event, title, description, event_date, location, image_path)
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events.manage_events'))

    events = event_repo.get_all()
    return render_template('admin/events.html', events=events, editing_event=event)

@events.route('/events/delete/<int:id>')
@admin_required
def delete_event(id):
    event = event_repo.get_by_id(id)
    # Xóa ảnh nếu tồn tại
    if event.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1])):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1]))
    event_repo.delete(event)
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.manage_events'))