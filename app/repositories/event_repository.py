from app.models import Event
from app.extensions import db
from datetime import datetime

class EventRepository:
    @staticmethod
    def get_all(order_by='event_date', direction='desc'):
        return Event.query.order_by(getattr(Event, order_by).desc() if direction == 'desc' else getattr(Event, order_by).asc()).all()

    @staticmethod
    def get_by_id(id):
        return Event.query.get_or_404(id)

    @staticmethod
    def create(title, description, event_date, location, image=None):
        event = Event(
            title=title,
            description=description,
            event_date=datetime.strptime(event_date, '%Y-%m-%d'),
            location=location,
            image=image
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update(event, title, description, event_date, location, image=None):
        event.title = title
        event.description = description
        event.event_date = datetime.strptime(event_date, '%Y-%m-%d')
        event.location = location
        event.image = image
        db.session.commit()
        return event

    @staticmethod
    def delete(event):
        db.session.delete(event)
        db.session.commit()