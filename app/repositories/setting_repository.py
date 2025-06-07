from app.models import Setting
from app.extensions import db

class SettingRepository:
    @staticmethod
    def get_all():
        return Setting.query.all()

    @staticmethod
    def get_by_key(key):
        return Setting.query.filter_by(key=key).first()

    @staticmethod
    def create(key, value):
        setting = Setting(key=key, value=value)
        db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def update(setting, new_key, new_value):
        setting.key = new_key
        setting.value = new_value
        db.session.commit()
        return setting

    @staticmethod
    def delete(setting):
        db.session.delete(setting)
        db.session.commit()
