from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from app import db
from app.decorators import admin_required
from app.models import Post, Category
from datetime import datetime
import os
from werkzeug.utils import secure_filename

posts = Blueprint('posts', __name__)


@posts.route('/posts', methods=['GET', 'POST'])
@login_required
def manage_posts():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        is_published = 'is_published' in request.form
        image = request.files.get('image')

        if not title or not slug or not content or not category_id:
            flash('All fields are required.', 'danger')
        else:
            post = Post(
                title=title,
                slug=slug,
                content=content,
                category_id=category_id,
                is_published=is_published,
                created_at=datetime.now()
            )
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                post.image = f'uploads/{filename}'

            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('posts.manage_posts'))

    posts = Post.query.order_by(Post.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('public/post_detail.html', posts=posts, categories=categories)


@posts.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.slug = request.form.get('slug')
        post.content = request.form.get('content')
        post.category_id = request.form.get('category_id')
        post.is_published = 'is_published' in request.form
        image = request.files.get('image')

        if not post.title or not post.slug or not post.content or not post.category_id:
            flash('All fields are required.', 'danger')
        else:
            if image and image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                post.image = f'uploads/{filename}'
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('posts.manage_posts'))

    posts = Post.query.order_by(Post.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/posts.html', posts=posts, categories=categories, editing_post=post)


@posts.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.image and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1])):
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image.split('/')[-1]))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.manage_posts'))