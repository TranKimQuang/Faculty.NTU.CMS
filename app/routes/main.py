from os import abort
from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required, editor_required
from app.models import Page, Category, Post, Announcement, Event, Menu, Setting
from collections import defaultdict
from app.routes.settings import settings

main = Blueprint('main', __name__)

def get_common_data():
    """Phần dữ liệu chung cho các route công cộng, bao gồm menu động."""
    current_date = datetime.now()

    # Phần xử lý menu động
    all_menus = Menu.query.order_by(Menu.order).all()
    menu_tree = defaultdict(list)
    menu_items_by_id = {menu.id: menu for menu in all_menus}
    root_menus = []
    for menu in all_menus:
        if menu.parent_id is None:
            root_menus.append(menu)
        else:
            if menu.parent_id in menu_items_by_id:
                menu_tree[menu.parent_id].append(menu)
    final_menus_for_template = []
    for root_menu in sorted(root_menus, key=lambda m: m.order):
        root_menu_dict = {
            'id': root_menu.id,
            'name': root_menu.name,
            'url': root_menu.url,
            'order': root_menu.order,
            'parent_id': root_menu.parent_id
        }
        root_menu_dict['children'] = sorted(menu_tree[root_menu.id], key=lambda m: m.order)
        final_menus_for_template.append(root_menu_dict)

    return {
        'dynamic_menus': final_menus_for_template,
        'pages': Page.query.order_by(Page.created_at.desc()).all(),
        'categories': Category.query.order_by(Category.name).all(),
        'announcements': Announcement.query.filter(
            Announcement.start_date <= current_date,
            Announcement.end_date >= current_date
        ).all(),
        'events': Event.query.filter(Event.event_date >= current_date).order_by(Event.event_date).all(),
        'settings_map': {setting.key: setting.value for setting in Setting.query.all()}
    }

# Phần route cho trang chính
@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    common_data = get_common_data()
    return render_template('public/index.html', posts=posts, **common_data)

# Phần route cho danh sách thông báo
@main.route('/announcements')
def announcements():
    current_date = datetime.now()
    common_data = get_common_data()
    return render_template('public/announcements.html', **common_data)

# Phần route cho danh sách trang
@main.route('/pages')
def pages():
    common_data = get_common_data()
    return render_template('public/pages.html', **common_data)

# Phần route cho chi tiết trang
@main.route('/page/<slug>')
def page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    common_data = get_common_data()
    return render_template('public/page_detail.html', page=page, **common_data)

# Phần route cho danh sách bài viết theo danh mục
@main.route('/posts/<slug>')
def posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, is_published=True).all()
    common_data = get_common_data()
    return render_template('public/posts.html', category=category, posts=posts, **common_data)

# Phần route cho tất cả bài viết
@main.route('/all-posts')
def all_posts():
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    common_data = get_common_data()
    return render_template('public/posts.html', posts=posts, **common_data)

# Phần route cho chi tiết bài viết
@main.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    common_data = get_common_data()
    other_posts = Post.query.filter(
        Post.id != post.id,
        Post.is_published == True
    ).order_by(Post.created_at.desc()).limit(2).all()
    return render_template('public/post_detail.html', post=post, **common_data, other_posts=other_posts)

# Phần route cho danh sách sự kiện
@main.route('/events')
def events():
    common_data = get_common_data()
    return render_template('public/events.html', **common_data)

# Phần route cho tìm kiếm
@main.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        pages = Page.query.filter(Page.title.contains(query) | Page.content.contains(query)).all()
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query), Post.is_published == True).all()
        events = Event.query.filter(Event.title.contains(query) | Event.description.contains(query)).all()
        results = [{'type': 'page', 'item': page} for page in pages] + \
                  [{'type': 'post', 'item': post} for post in posts] + \
                  [{'type': 'event', 'item': event} for event in events]
    common_data = get_common_data()
    return render_template('public/search.html', query=query, results=results, **common_data)