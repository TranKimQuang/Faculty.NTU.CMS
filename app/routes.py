from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Page, Category, Post, Announcement, Event, Menu
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    announcements = Announcement.query.filter(
        Announcement.start_date <= datetime.now(),
        Announcement.end_date >= datetime.now()
    ).all()
    events = Event.query.filter(Event.event_date >= datetime.now()).order_by(Event.event_date).all()
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(6).all()
    pages = Page.query.order_by(Page.created_at.desc()).limit(6).all()
    categories = Category.query.order_by(Category.name).all()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/index.html',
                         announcements=announcements,
                         events=events,
                         posts=posts,
                         pages=pages,
                         categories=categories,
                         menus=menus)

@main.route('/page/<slug>')
def page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/page.html', page=page, menus=menus)

@main.route('/posts/<slug>')
def posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, is_published=True).all()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/posts.html', category=category, posts=posts, menus=menus)

@main.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/post.html', post=post, menus=menus)

@main.route('/events')
def events():
    events = Event.query.filter(Event.event_date >= datetime.now()).order_by(Event.event_date).all()
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/events.html', events=events, menus=menus)

@main.route('/search')
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
    menus = Menu.query.filter_by(parent_id=None).order_by(Menu.order).all()
    return render_template('public/search.html', query=query, results=results, menus=menus)

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(main.config['UPLOAD_FOLDER'], filename)

@main.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@main.route('/admin/pages', methods=['GET', 'POST'])
@login_required
def manage_pages():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        content = request.form['content']
        page = Page(title=title, slug=slug, content=content)
        db.session.add(page)
        db.session.commit()
        flash('Page created successfully!')
        return redirect(url_for('main.manage_pages'))
    pages = Page.query.all()
    return render_template('admin/pages.html', pages=pages)

@main.route('/admin/posts', methods=['GET', 'POST'])
@login_required
def manage_posts():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        slug = request.form['slug']
        content = request.form['content']
        category_id = request.form['category_id']
        is_published = 'is_published' in request.form
        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(main.config['UPLOAD_FOLDER'], filename))
            image_path = f'uploads/{filename}'
        post = Post(title=title, slug=slug, content=content, category_id=category_id, is_published=is_published, image=image_path)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('main.manage_posts'))
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('admin/posts.html', posts=posts, categories=categories)

@main.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        category = Category(name=name, slug=slug)
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!')
        return redirect(url_for('main.manage_categories'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@main.route('/admin/announcements', methods=['GET', 'POST'])
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
        flash('Announcement created successfully!')
        return redirect(url_for('main.manage_announcements'))
    announcements = Announcement.query.all()
    return render_template('admin/announcements.html', announcements=announcements)

@main.route('/admin/events', methods=['GET', 'POST'])
@login_required
def manage_events():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_date = datetime.strptime(request.form['event_date'], '%Y-%m-%d')
        location = request.form['location']
        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(main.config['UPLOAD_FOLDER'], filename))
            image_path = f'uploads/{filename}'
        event = Event(title=title, description=description, event_date=event_date, location=location, image=image_path)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!')
        return redirect(url_for('main.manage_events'))
    events = Event.query.all()
    return render_template('admin/events.html', events=events)

@main.route('/admin/menus', methods=['GET', 'POST'])
@login_required
def manage_menus():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        parent_id = request.form['parent_id'] or None
        order = request.form['order']
        menu = Menu(name=name, url=url, parent_id=parent_id, order=order)
        db.session.add(menu)
        db.session.commit()
        flash('Menu created successfully!')
        return redirect(url_for('main.manage_menus'))
    menus = Menu.query.all()
    return render_template('admin/menus.html', menus=menus)