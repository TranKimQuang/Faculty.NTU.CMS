from app.models import Menu
from app.extensions import db

class MenuRepository:
    @staticmethod
    def get_all(order_by='order', direction='asc'):
        return Menu.query.order_by(getattr(Menu, order_by).asc() if direction == 'asc' else getattr(Menu, order_by).desc()).all()

    @staticmethod
    def get_by_id(id):
        return Menu.query.get_or_404(id)

    @staticmethod
    def create(name, url, order, parent_id=None):
        menu = Menu(name=name, url=url, order=int(order), parent_id=parent_id)
        db.session.add(menu)
        db.session.commit()
        return menu

    @staticmethod
    def update(menu, name, url, order, parent_id=None):
        menu.name = name
        menu.url = url
        menu.order = int(order)
        menu.parent_id = parent_id
        db.session.commit()
        return menu

    @staticmethod
    def delete(menu):
        db.session.delete(menu)
        db.session.commit()