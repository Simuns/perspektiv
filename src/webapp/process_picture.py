import os
# Used for picture reduction in size
from PIL import Image
from webapp.database import db, Grein,UserModel
from webapp.app import app

def compress_picture(picture, context_id):
    picture_filename = context_id + "-" + picture.filename

    picture_filename_jpg =            os.path.splitext(picture_filename)[0] + '.jpg'
    small_picture_filename='small-' + os.path.splitext(picture_filename)[0] + '.jpg'
    large_picture_filename='large-' + os.path.splitext(picture_filename)[0] + '.jpg'

    picture.save(f'static/uploads/orig-{picture_filename}')


    ## Process image ##
    open_raw_picture_filename = Image.open(f'static/uploads/orig-{picture_filename}')

    if open_raw_picture_filename.mode == 'RGBA':
        open_raw_picture_filename = open_raw_picture_filename.convert('RGB')


    # Handeling large picture
    width, height = open_raw_picture_filename.size
    TARGET_WIDTH = 1000
    coefficient = width / 1000
    new_height = height / coefficient
    large_picture = open_raw_picture_filename.resize((int(TARGET_WIDTH),int(new_height)),Image.ANTIALIAS)
    large_picture.save(f"static/uploads/{large_picture_filename}")


    # Handeling small picture
    width, height = open_raw_picture_filename.size
    TARGET_WIDTH = 100
    coefficient = width / 100
    new_height = height / coefficient
    small_picture = open_raw_picture_filename.resize((int(TARGET_WIDTH),int(new_height)),Image.ANTIALIAS)
    # saving small picture #
    small_picture.save(f"static/uploads/{small_picture_filename}")
    return picture_filename_jpg

def save_picture(context_id, picture_path):

    with app.app_context():
        
        # Handle as article
        if len(context_id) == 8:
            article = artiklar.query.filter_by(art_id=context_id).first()
            if article:
                article.picture_path = picture_path
                db.session.commit()
                return "Path loaded to database"
            else:
                nyggj_mynd = artiklar(
                    art_id=context_id,
                    picture_path=picture_path)
                db.session.add(nyggj_mynd)
                db.session.commit()
                return "Path loaded to database"
        # Handle as user
        if len(context_id) == 10:
            user = UserModel.query.filter_by(user_id=context_id).first()
            if user:
                user.picture_path = picture_path
                db.session.commit()
            else:
                return "No user found"
