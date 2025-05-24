from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Menu

menus = Blueprint('menus', __name__)

@menus.route('/menus', methods=['GET', 'POST'])
@login_required
def manage_menus():
    if not current_user.has_permission('create'):
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        parent_id = request.form['parent_id'] or None
        order = request.form['order']
        menu = Menu(name=name, url=url, parent_id=parent_id, order=order)
        db.session.add(menu)
        db.session.commit()
        flash('Menu created successfully!', 'success')
        return redirect(url_for('menus.manage_menus'))
    menus = Menu.query.all()
    return render_template('admin/menus.html', menus=menus)