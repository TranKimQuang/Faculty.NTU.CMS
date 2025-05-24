from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Category

categories = Blueprint('categories', __name__)

@categories.route('/categories', methods=['GET', 'POST'])
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
        flash('Category created successfully!', 'success')
        return redirect(url_for('categories.manage_categories'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)