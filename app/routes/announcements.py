from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Announcement
from datetime import datetime

announcements = Blueprint('announcements', __name__)

@announcements.route('/announcements', methods=['GET', 'POST'])
@login_required
def manage_announcements():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        announcement = Announcement(title=title, content=content, start_date=start_date, end_date=end_date)
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('announcements.manage_announcements'))
    announcements = Announcement.query.all()
    return render_template('admin/announcements.html', announcements=announcements)