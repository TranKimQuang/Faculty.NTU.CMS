from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models import Category

categories = Blueprint('categories', __name__)


@categories.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')

        if not name or not slug:
            flash('All fields are required.', 'danger')
        elif Category.query.filter_by(slug=slug).first():
            flash('Slug already exists.', 'danger')
        else:
            category = Category(name=name, slug=slug)
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('categories.manage_categories'))

    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)


@categories.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.name = request.form.get('name')
        new_slug = request.form.get('slug')

        if not category.name or not new_slug:
            flash('All fields are required.', 'danger')
        elif new_slug != category.slug and Category.query.filter_by(slug=new_slug).first():
            flash('Slug already exists.', 'danger')
        else:
            category.slug = new_slug
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('categories.manage_categories'))

    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories, editing_category=category)


@categories.route('/categories/delete/<int:id>')
@login_required
@admin_required
def delete_category(id):
    if current_user.role != 'Admin':
        flash('You do not have permission to delete categories.', 'danger')
        return redirect(url_for('categories.manage_categories'))

    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories.manage_categories'))