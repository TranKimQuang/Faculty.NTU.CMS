from app.models import Category
from app.extensions import db # Đảm bảo import db từ app.extensions

class CategoryRepository:
    @staticmethod
    def get_all(order_by='name', direction='asc'):
        return Category.query.order_by(getattr(Category, order_by).asc() if direction == 'asc' else getattr(Category, order_by).desc()).all()

    @staticmethod
    def get_by_id(id):
        return Category.query.get_or_404(id)

    @staticmethod
    def get_by_slug(slug):
        return Category.query.filter_by(slug=slug).first()

    @staticmethod
    def create(name, slug):
        category = Category(name=name, slug=slug)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update(category, name, slug):
        category.name = name
        category.slug = slug
        db.session.commit()
        return category

    @staticmethod
    def delete(category):
        db.session.delete(category)
        db.session.commit()
