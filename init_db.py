from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Kiểm tra và thêm người dùng nếu chưa tồn tại
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin_password')
        db.session.add(admin)

    if not User.query.filter_by(username='editor').first():
        editor = User(username='editor', role='editor')
        editor.set_password('editor_password')
        db.session.add(editor)

    if not User.query.filter_by(username='viewer').first():
        viewer = User(username='viewer', role='viewer')
        viewer.set_password('viewer_password')
        db.session.add(viewer)

    # Lưu các thay đổi
    db.session.commit()
    print("Users created successfully!")