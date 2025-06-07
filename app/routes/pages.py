from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import editor_required, admin_required
from app.repositories.page_repository import PageRepository
from datetime import datetime

pages = Blueprint('pages', __name__)

# Khởi tạo repository
page_repo = PageRepository()

@pages.route('/pages', methods=['GET', 'POST'])
@login_required
def manage_pages():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')  # Sửa lỗi: bỏ dấu phẩy thừa
        created_by = current_user.id

        if not title or not slug or not content:
            flash('All fields are required.', 'danger')
        else:
            page_repo.create(title, slug, content)
            flash('Page created successfully!', 'success')
            return redirect(url_for('pages.manage_pages'))

    pages = page_repo.get_all()
    return render_template('admin/pages.html', pages=pages)

@pages.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_page(id):
    page = page_repo.get_by_id(id)

    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')

        if not title or not slug or not content:
            flash('All fields are required.', 'danger')
        else:
            page_repo.update(page, title, slug, content)
            flash('Page updated successfully!', 'success')
            return redirect(url_for('pages.manage_pages'))

    pages = page_repo.get_all()
    return render_template('admin/pages.html', pages=pages, editing_page=page)

@pages.route('/pages/delete/<int:id>')
@admin_required
def delete_page(id):
    page = page_repo.get_by_id(id)
    page_repo.delete(page)
    flash('Page deleted successfully!', 'success')
    return redirect(url_for('pages.manage_pages'))