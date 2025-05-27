from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from app import db
from app.decorators import admin_required
from app.models import Event
from datetime import datetime
import os
from werkzeug.utils import secure_filename

events = Blueprint('events', __name__)


@events.route('/events', methods=['GET', 'POST'])

def manage_events():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        image = request.files.get('image')

        if not title or not description or not event_date or not location:
            flash('All fields are required.', 'danger')
        else:
            event = Event(
                title=title,
                description=description,
                event_date=datetime.strptime(event_date, '%Y-%m-%d'),
                location=location
            )
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                event.image = f'uploads/{filename}'

            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('events.manage_events'))

    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', events=events)


@events.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_event(id):
    event = Event.query.get_or_404(id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event_date = request.form.get('event_date')
        event.location = request.form.get('location')
        image = request.files.get('image')

        if not event.title or not event.description or not event_date or not event.location:
            flash('All fields are required.', 'danger')
        else:
            event.event_date = datetime.strptime(event_date, '%Y-%m-%d')
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                event.image = f'uploads/{filename}'
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events.manage_events'))

    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', events=events, editing_event=event)


@events.route('/events/delete/<int:id>')
@admin_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    if event.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1])):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], event.image.split('/')[-1]))
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.manage_events'))