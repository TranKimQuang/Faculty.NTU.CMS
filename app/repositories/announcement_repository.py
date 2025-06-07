from app.models import Announcement
from app.extensions import db
from datetime import datetime

class AnnouncementRepository:
    @staticmethod
    def get_all(order_by='start_date', direction='desc'):
        return Announcement.query.order_by(getattr(Announcement, order_by).desc() if direction == 'desc' else getattr(Announcement, order_by).asc()).all()

    @staticmethod
    def get_by_id(id):
        return Announcement.query.get_or_404(id)

    @staticmethod
    def create(title, content, start_date, end_date):
        announcement = Announcement(title=title, content=content,
                                   start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                                   end_date=datetime.strptime(end_date, '%Y-%m-%d'))
        db.session.add(announcement)
        db.session.commit()
        return announcement

    @staticmethod
    def update(announcement, title, content, start_date, end_date):
        announcement.title = title
        announcement.content = content
        announcement.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        announcement.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        db.session.commit()
        return announcement

    @staticmethod
    def delete(announcement):
        db.session.delete(announcement)
        db.session.commit()