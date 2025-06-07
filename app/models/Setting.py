from app import db


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'
