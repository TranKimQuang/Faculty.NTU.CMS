from app.models import Post
from app.extensions import db
from datetime import datetime

class PostRepository:
    @staticmethod
    def get_all(order_by='created_at', direction='desc'):
        return Post.query.order_by(getattr(Post, order_by).desc() if direction == 'desc' else getattr(Post, order_by).asc()).all()

    @staticmethod
    def get_by_id(id):
        return Post.query.get_or_404(id)

    @staticmethod
    def create(title, slug, content, category_id, is_published, created_by):
        post = Post(
            title=title,
            slug=slug,
            content=content,
            category_id=category_id,
            is_published=is_published,
            created_at=datetime.now(),
            created_by=created_by
        )
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def update(post, title, slug, content, category_id, is_published, image=None):
        post.title = title
        post.slug = slug
        post.content = content
        post.category_id = category_id
        post.is_published = is_published
        if image:
            post.image = image
        db.session.commit()
        return post

    @staticmethod
    def delete(post):
        db.session.delete(post)
        db.session.commit()