from app import db


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref='pages')