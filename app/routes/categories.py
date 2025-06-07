from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required, editor_required
from app.repositories.category_repository import CategoryRepository

categories = Blueprint('categories', __name__)

# Khởi tạo repository
category_repo = CategoryRepository()

@categories.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')

        if not name or not slug:
            flash('All fields are required.', 'danger')
        elif category_repo.get_by_slug(slug):
            flash('Slug already exists.', 'danger')
        else:
            category_repo.create(name, slug)
            flash('Category created successfully!', 'success')
            return redirect(url_for('categories.manage_categories'))

    categories = category_repo.get_all()
    return render_template('admin/categories.html', categories=categories)

@categories.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = category_repo.get_by_id(id)

    if request.method == 'POST':
        category.name = request.form.get('name')
        new_slug = request.form.get('slug')

        if not category.name or not new_slug:
            flash('All fields are required.', 'danger')
        elif new_slug != category.slug and category_repo.get_by_slug(new_slug):
            flash('Slug already exists.', 'danger')
        else:
            category_repo.update(category, category.name, new_slug)
            flash('Category updated successfully!', 'success')
            return redirect(url_for('categories.manage_categories'))

    categories = category_repo.get_all()
    return render_template('admin/categories.html', categories=categories, editing_category=category)

@categories.route('/categories/delete/<int:id>')
@admin_required
def delete_category(id):
    category = category_repo.get_by_id(id)
    category_repo.delete(category)
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories.manage_categories'))