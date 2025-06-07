from os import abort
from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required, editor_required
from app.models import Page, Category, Post, Announcement, Event, Menu, Setting
from collections import defaultdict # RẤT QUAN TRỌNG: Đảm bảo dòng này đã được thêm

main = Blueprint('main', __name__)

def get_common_data():
    """
    Hàm trợ giúp để lấy dữ liệu chung cho tất cả các route công cộng.
    Bao gồm cả logic để xây dựng cấu trúc menu động (cha-con).
    """
    current_date = datetime.now()

    # --- Bắt đầu logic xử lý menu động ---
    all_menus = Menu.query.order_by(Menu.order).all()

    # Bước 1: Khởi tạo defaultdict để lưu trữ các menu con theo ID của menu cha
    menu_tree = defaultdict(list)
    # Bước 2: Tạo một mapping từ ID menu đến đối tượng menu để truy cập nhanh
    menu_items_by_id = {menu.id: menu for menu in all_menus}

    # Bước 3: Phân loại các menu gốc và gán các menu con vào cây
    root_menus = []
    for menu in all_menus:
        if menu.parent_id is None:
            # If there's no parent_id, this is a root menu
            root_menus.append(menu)
        else:
            # If there's a parent_id, add it to the list of children of the parent menu
            # Ensure the parent menu exists before adding a child (to prevent invalid parent_id issues)
            if menu.parent_id in menu_items_by_id:
                menu_tree[menu.parent_id].append(menu)

    # Step 4: Sort root menus and attach their sorted children lists
    final_menus_for_template = []
    for root_menu in sorted(root_menus, key=lambda m: m.order):
        # Convert SQLAlchemy object to a dictionary to safely add 'children' attribute
        # (This is a safe way to manipulate without affecting SQLAlchemy's session)
        root_menu_dict = {
            'id': root_menu.id,
            'name': root_menu.name,
            'url': root_menu.url,
            'order': root_menu.order,
            'parent_id': root_menu.parent_id
        }
        # Get the list of child menus and sort them by their order
        root_menu_dict['children'] = sorted(menu_tree[root_menu.id], key=lambda m: m.order)
        final_menus_for_template.append(root_menu_dict)
    # --- End of dynamic menu processing logic ---

    return {
        'dynamic_menus': final_menus_for_template, # This variable will be passed to the template
        'pages': Page.query.order_by(Page.created_at.desc()).all(),
        'categories': Category.query.order_by(Category.name).all(),
        'announcements': Announcement.query.filter(
            Announcement.start_date <= current_date,
            Announcement.end_date >= current_date
        ).all(),
        'events': Event.query.filter(Event.event_date >= current_date).order_by(Event.event_date).all(),
        'settings_map': {setting.key: setting.value for setting in Setting.query.all()}
    }

# Your routes - ensure all of them call get_common_data() and pass the common data
@main.route('/')
def index():
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(6).all()
    common_data = get_common_data() # Get common data
    return render_template('public/index.html',
                         posts=posts,
                         **common_data) # Pass common data to the template

@main.route('/announcements')
def announcements():
    current_date = datetime.now()
    common_data = get_common_data()
    # FIX: Remove direct passing of 'announcements' variable as it's already in **common_data
    return render_template('public/announcements.html', **common_data)


@main.route('/pages')
def pages():
    common_data = get_common_data()
    return render_template('public/pages.html', **common_data)

@main.route('/page/<slug>')
def page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    common_data = get_common_data()
    return render_template('public/page_detail.html', page=page, **common_data) # Usually page_detail.html for a specific page

# Route for managing settings (creating new ones)
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    editing_setting = None # No setting is being edited initially

    if request.method == 'POST':
        key = request.form.get('key')
        value = request.form.get('value')

        if not key or not value:
            flash('Key and Value are required.', 'danger')
        else:
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                flash(f'Setting with key "{key}" already exists. Use edit to change it.', 'warning')
            else:
                setting = Setting(key=key, value=value)
                db.session.add(setting)
                db.session.commit()
                flash('Setting created successfully.', 'success')
            return redirect(url_for('main.settings'))

    settings = Setting.query.all()
    return render_template('admin/settings.html', settings=settings, editing_setting=editing_setting)

# Route for editing a setting
@main.route('/settings/edit/<string:key>', methods=['GET', 'POST'])
@login_required
def edit_setting(key):
    setting = Setting.query.filter_by(key=key).first_or_404()

    if request.method == 'POST':
        new_key = request.form.get('key')
        new_value = request.form.get('value')

        if not new_key or not new_value:
            flash('Key and Value are required.', 'danger')
        else:
            # Check if the new key is different from the old key AND if the new key already exists
            if new_key != key and Setting.query.filter_by(key=new_key).first():
                flash(f'Cannot change key to "{new_key}" as it already exists.', 'danger')
            else:
                setting.key = new_key
                setting.value = new_value
                db.session.commit()
                flash('Setting updated successfully.', 'success')
                return redirect(url_for('main.settings'))

    settings = Setting.query.all() # Need to pass the list of settings to display the table
    return render_template('admin/settings.html', settings=settings, editing_setting=setting)

# Route for deleting a setting
@main.route('/settings/delete/<string:key>')
@admin_required
def delete_setting(key):
    setting = Setting.query.filter_by(key=key).first_or_404()
    db.session.delete(setting)
    db.session.commit()
    flash(f'Setting "{key}" deleted successfully.', 'success')
    return redirect(url_for('main.settings'))


@main.route('/posts/<slug>')
def posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category_id=category.id, is_published=True).all()
    common_data = get_common_data()
    return render_template('public/posts.html', category=category, posts=posts, **common_data)

@main.route('/all-posts')
def all_posts():
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    common_data = get_common_data()
    return render_template('public/posts.html', posts=posts, **common_data)

@main.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    common_data = get_common_data()
    return render_template('public/post_detail.html', post=post, **common_data)

@main.route('/events')
def events():
    common_data = get_common_data()
    return render_template('public/events.html', **common_data)

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
    common_data = get_common_data()
    return render_template('public/search.html', query=query, results=results, **common_data)
