from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Menu

menus = Blueprint('menus', __name__)


@menus.route('/menus', methods=['GET', 'POST'])
@login_required
def manage_menus():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        order = request.form.get('order')
        parent_id = request.form.get('parent_id')

        if not name or not url or not order:
            flash('All fields are required.', 'danger')
        else:
            menu = Menu(name=name, url=url, order=int(order), parent_id=parent_id if parent_id else None)
            db.session.add(menu)
            db.session.commit()
            flash('Menu created successfully!', 'success')
            return redirect(url_for('menus.manage_menus'))

    menus = Menu.query.order_by(Menu.order).all()
    return render_template('admin/menus.html', menus=menus)


@menus.route('/menus/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_menu(id):
    menu = Menu.query.get_or_404(id)

    if request.method == 'POST':
        menu.name = request.form.get('name')
        menu.url = request.form.get('url')
        menu.order = int(request.form.get('order'))
        menu.parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None

        if not menu.name or not menu.url or not menu.order:
            flash('All fields are required.', 'danger')
        else:
            db.session.commit()
            flash('Menu updated successfully!', 'success')
            return redirect(url_for('menus.manage_menus'))

    menus = Menu.query.order_by(Menu.order).all()
    return render_template('admin/menus.html', menus=menus, editing_menu=menu)


@menus.route('/menus/delete/<int:id>')
@login_required
def delete_menu(id):
    if current_user.role != 'Admin':
        flash('You do not have permission to delete menus.', 'danger')
        return redirect(url_for('menus.manage_menus'))

    menu = Menu.query.get_or_404(id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu deleted successfully!', 'success')
    return redirect(url_for('menus.manage_menus'))