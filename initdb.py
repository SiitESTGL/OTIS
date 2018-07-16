from app_core import db
from models import User, Images, API_Key
from app_admin_function import generate_hash_key

print("Initializing database...")
db.drop_all()
db.create_all()

user = User.create (
    username = "admin",
    password = "admin",
    email = "email@email.com",
    admin = 1,
    superadmin = 1
)

user_key = API_Key(key = generate_hash_key())
        
user.user_key.append(user_key)

image = Images (
    img_descrip = "placeholder",
    original_img = "1920x486.png",
    copy_img = "copy_1920x486.png",
    img_check = False
)

db.session.add(user)
db.session.add(image)
db.session.commit()

print("Finished")

