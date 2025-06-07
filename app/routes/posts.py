from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from app import db
from app.decorators import admin_required, editor_required
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

posts = Blueprint('posts', __name__)

# Khởi tạo repository
post_repo = PostRepository()
category_repo = CategoryRepository()

@posts.route('/posts', methods=['GET', 'POST'])
@login_required
def manage_posts():
    editing_post = None
    if request.method == 'POST':
        post_id = request.form.get('id')  # Kiểm tra nếu đang chỉnh sửa
        if post_id:
            post = post_repo.get_by_id(post_id)
            title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            category_id = request.form.get('category_id')
            is_published = 'is_published' in request.form
            image = request.files.get('image')
            image_path = post.image if not image else None
            if image and image.filename:
                if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                    os.makedirs(current_app.config['UPLOAD_FOLDER'])
                filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                if post.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1])):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1]))
                image_path = f'uploads/{filename}'
            post_repo.update(post, title, slug, content, category_id, is_published, image_path)
            flash('Post updated successfully!', 'success')
        else:
            title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            category_id = request.form.get('category_id')
            is_published = 'is_published' in request.form
            image = request.files.get('image')

            if not title or not slug or not content or not category_id:
                flash('All fields are required.', 'danger')
            else:
                image_path = None
                if image and image.filename:
                    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                        os.makedirs(current_app.config['UPLOAD_FOLDER'])
                    filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_path = f'uploads/{filename}'
                post_repo.create(title, slug, content, category_id, is_published, current_user.id)
                flash('Post created successfully!', 'success')
        return redirect(url_for('posts.manage_posts'))

    posts = post_repo.get_all()
    categories = category_repo.get_all()
    return render_template('admin/posts.html', posts=posts, categories=categories, editing_post=editing_post)

@posts.route('/admin/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = post_repo.get_by_id(id)
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        is_published = 'is_published' in request.form
        image = request.files.get('image')
        image_path = post.image if not image else None
        if image and image.filename:
            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                os.makedirs(current_app.config['UPLOAD_FOLDER'])
            filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            if post.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1])):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1]))
            image_path = f'uploads/{filename}'
        post_repo.update(post, title, slug, content, category_id, is_published, image_path)
        flash('Post updated successfully!', 'success')
        return redirect(url_for('posts.manage_posts'))

    categories = category_repo.get_all()
    return render_template('admin/posts.html', posts=[post], categories=categories, editing_post=post)

@posts.route('/admin/posts/delete/<int:id>')
@admin_required
def delete_post(id):
    post = post_repo.get_by_id(id)
    if post.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1])):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1]))
    post_repo.delete(post)
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.manage_posts'))