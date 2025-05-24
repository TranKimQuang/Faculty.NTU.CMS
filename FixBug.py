from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash, generate_password_hash

app = create_app()

with app.app_context():
    # Tìm người dùng 'editor'
    editor_user = User.query.filter_by(username='editor').first()

    if editor_user:
        # *********** ĐẶT MẬT KHẨU CỰC KỲ ĐƠN GIẢN LÀ '1' ***********
        simple_password = '1'

        editor_user.set_password(simple_password)
        db.session.add(editor_user)
        db.session.commit()
        print(f"Mật khẩu cho 'editor' đã được đặt lại thành: '{simple_password}'")
        print(f"Hash mới: {editor_user.password_hash}")

        # *********** KIỂM TRA NGAY LẬP TỨC TRONG CÙNG PHIÊN SHELL ***********
        # Lấy lại đối tượng người dùng để đảm bảo lấy hash từ DB sau commit
        retrieved_editor_user = User.query.filter_by(username='editor').first()
        if retrieved_editor_user:
            is_correct = retrieved_editor_user.check_password(simple_password)
            print(f"Kiểm tra mật khẩu '{simple_password}' cho 'editor' trong shell: {is_correct}")

            if is_correct:
                print("=> Thành công: Mật khẩu khớp trong Flask Shell.")
                print("Bây giờ, hãy khởi động lại server và thử đăng nhập bằng mật khẩu '1'.")
            else:
                print("=> LỖI NGHIÊM TRỌNG: Mật khẩu KHÔNG khớp ngay cả trong Flask Shell.")
                print("Có thể có vấn đề với cài đặt Werkzeug hoặc model User của bạn.")
        else:
            print("Không tìm thấy người dùng 'editor' sau khi cập nhật.")
    else:
        print("Người dùng 'editor' không tồn tại. Không thể cập nhật mật khẩu.")