from os import abort
from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models import Page, Category, Post, Announcement, Event, Menu, Setting, Comment

main = Blueprint('main', __name__)

def get_common_data():
    """Helper function to get common data for all public routes."""
    return {
        'menus': Menu.query.filter_by(parent_id=None).order_by(Menu.order).all(),
        'pages': Page.query.order_by(Page.created_at.desc()).all(),
        'categories': Category.query.order_by(Category.name).all()
    }

@main.route('/')

def index():
    announcements = Announcement.query.filter(
        Announcement.start_date <= datetime.now(),
        Announcement.end_date >= datetime.now()
    ).all()
    events = Event.query.filter(Event.event_date >= datetime.now()).order_by(Event.event_date).all()
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(6).all()
    common_data = get_common_data()
    return render_template('public/index.html',
                         announcements=announcements,
                         events=events,
                         posts=posts,
                         **common_data)

@main.route('/announcements')
@login_required
def announcements():
    current_date = datetime.now()
    announcements = Announcement.query.filter(
        Announcement.start_date <= current_date,
        Announcement.end_date >= current_date
    ).order_by(Announcement.start_date.desc()).all()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/announcements.html', announcements=announcements, menus=menus)

@main.route('/page/<slug>')
@login_required
def page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    common_data = get_common_data()
    return render_template('public/page.html', page=page, **common_data)

@main.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        key = request.form.get('key')
        value = request.form.get('value')
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        flash('Setting updated successfully.', 'success')
        return redirect(url_for('main.settings'))

    settings = Setting.query.all()
    return render_template('admin/settings.html', settings=settings)

@main.route('/posts/<slug>')
@login_required
def posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, is_published=True).all()
    common_data = get_common_data()
    return render_template('public/posts.html', category=category, posts=posts, **common_data)

@main.route('/post/<slug>', methods=['GET', 'POST'])
@login_required
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to log in to comment.', 'danger')
            return redirect(url_for('auth.login'))

        content = request.form.get('content')
        if not content:
            flash('Comment cannot be empty.', 'danger')
        else:
            comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added successfully.', 'success')
        return redirect(url_for('main.post_detail', slug=slug))

    common_data = get_common_data()
    return render_template('public/post_detail.html', post=post, comments=comments, **common_data)

@main.route('/events')
@login_required
def events():
    events = Event.query.filter(Event.event_date >= datetime.now()).order_by(Event.event_date).all()
    common_data = get_common_data()
    return render_template('public/events.html', events=events, **common_data)

@main.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        pages = Page.query.filter(Page.title.contains(query) | Page.content.contains(query)).all()
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query), Post.is_published==True).all()
        events = Event.query.filter(Event.title.contains(query) | Event.description.contains(query)).all()
        results = [{'type': 'page', 'item': page} for page in pages] + \
                  [{'type': 'post', 'item': post} for post in posts] + \
                  [{'type': 'event', 'item': event} for event in events]
    common_data = get_common_data()
    return render_template('public/search.html', query=query, results=results, **common_data)