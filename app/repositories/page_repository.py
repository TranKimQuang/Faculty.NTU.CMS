from app.models import Page
from app.extensions import db
from datetime import datetime

class PageRepository:
    @staticmethod
    def get_all(order_by='created_at', direction='desc'):
        return Page.query.order_by(getattr(Page, order_by).desc() if direction == 'desc' else getattr(Page, order_by).asc()).all()

    @staticmethod
    def get_by_id(id):
        return Page.query.get_or_404(id)

    @staticmethod
    def create(title, slug, content):
        page = Page(title=title, slug=slug, content=content, created_at=datetime.now())
        db.session.add(page)
        db.session.commit()
        return page

    @staticmethod
    def update(page, title, slug, content):
        page.title = title
        page.slug = slug
        page.content = content
        db.session.commit()
        return page

    @staticmethod
    def delete(page):
        db.session.delete(page)
        db.session.commit()