from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models import Menu
from app.repositories.menu_repository import MenuRepository

menus = Blueprint('menus', __name__)

# Khởi tạo repository
menu_repo = MenuRepository()

@menus.route('/menus', methods=['GET', 'POST'])
@admin_required
def manage_menus():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        order = request.form.get('order')
        parent_id = request.form.get('parent_id')

        if not name or not url or not order:
            flash('All fields are required.', 'danger')
        else:
            # Chuyển đổi parent_id thành None nếu rỗng, hoặc số nguyên nếu là số
            parent_id = int(parent_id) if parent_id and parent_id.isdigit() else None
            print(f"Saving menu with parent_id: {parent_id}")  # Debug
            menu_repo.create(name, url, order, parent_id)
            flash('Menu created successfully!', 'success')
            return redirect(url_for('menus.manage_menus'))

    menus = menu_repo.get_all()
    return render_template('admin/menus.html', menus=menus)

@menus.route('/menus/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_menu(id):
    menu = menu_repo.get_by_id(id)

    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        order = request.form.get('order')
        parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None

        if not name or not url or not order:
            flash('All fields are required.', 'danger')
        else:
            menu_repo.update(menu, name, url, order, parent_id)
            flash('Menu updated successfully!', 'success')
            return redirect(url_for('menus.manage_menus'))

    menus = menu_repo.get_all()
    return render_template('admin/menus.html', menus=menus, editing_menu=menu, Menu=Menu)

@menus.route('/menus/delete/<int:id>')
@admin_required
def delete_menu(id):
    menu = menu_repo.get_by_id(id)
    menu_repo.delete(menu)
    flash('Menu deleted successfully!', 'success')
    return redirect(url_for('menus.manage_menus'))