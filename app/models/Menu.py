from app.extensions import db


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    order = db.Column(db.Integer, default=0)
    parent = db.relationship('Menu', remote_side=[id], backref='children')