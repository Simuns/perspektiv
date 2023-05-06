from webapp.database import db, UserModel
from webapp.app import app

def set_vangi(vangi, force=False):
    with app.app_context():

        if isinstance(vangi, list):
            vangi = vangi[0].lower() + "." + vangi[1].lower()
        else:
            vangi = vangi.lower()

        if force:
            user = UserModel.query.filter_by(vangi=vangi).first()
            if user:
                #make sure there is no other vangi with this name 
                count = 0
                while user:
                    count += 1
                    cur_vangi = vangi + str(count)
                    # execute the database query to get the first user
                    user = UserModel.query.filter_by(vangi=cur_vangi).first()

                    # if no user is found, do something else, e.g. sleep or run other code
                    if not user:
                        return cur_vangi
            else: return vangi
        else:
            #See if available
            user = UserModel.query.filter_by(vangi=vangi).first()
            if user: return False
            else: return True