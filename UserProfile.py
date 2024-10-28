import os
from werkzeug.utils import secure_filename


user_data = {
"name": "John Doe",
"email": "jh@example.com",
"nickname": "JH",
"profile_picture": "default.jpg"
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/profile_pics'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_email(new_email):
    user_data['email'] = new_email
    return True

def update_nickname(new_nickname):
    user_data['nickname'] = new_nickname
    return True

def update_profile_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        user_data['profile_picture'] = filename
        return True, filename
    return False, None
    
def get_user():
    return user_data