from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Page, Post, Event, Announcement
from app.routes.announcements import announcements

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def dashboard():
    page_count = Page.query.count()
    post_count = Post.query.count()
    event_count = Event.query.count()
    announcements_count = Announcement.query.count()

    return render_template('admin/dashboard.html',
                           page_count=page_count,
                           post_count=post_count,
                           event_count=event_count,
                           announcements_count=announcements_count)
