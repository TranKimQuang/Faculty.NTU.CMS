from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Page
from datetime import datetime

pages = Blueprint('pages', __name__)


@pages.route('/pages', methods=['GET', 'POST'])
def manage_pages():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content'),
        created_by = current_user.id

        if not title or not slug or not content:
            flash('All fields are required.', 'danger')
        else:
            page = Page(title=title, slug=slug, content=content, created_at=datetime.now())
            db.session.add(page)
            db.session.commit()
            flash('Page created successfully!', 'success')
            return redirect(url_for('pages.manage_pages'))

    pages = Page.query.order_by(Page.created_at.desc()).all()
    return render_template('admin/pages.html', pages=pages)


@pages.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
def edit_page(id):
    page = Page.query.get_or_404(id)

    if request.method == 'POST':
        page.title = request.form.get('title')
        page.slug = request.form.get('slug')
        page.content = request.form.get('content')

        if not page.title or not page.slug or not page.content:
            flash('All fields are required.', 'danger')
        else:
            db.session.commit()
            flash('Page updated successfully!', 'success')
            return redirect(url_for('pages.manage_pages'))

    return render_template('admin/pages.html', pages=Page.query.order_by(Page.created_at.desc()).all(),
                           editing_page=page)


@pages.route('/pages/delete/<int:id>')
def delete_page(id):
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'success')
    return redirect(url_for('pages.manage_pages'))