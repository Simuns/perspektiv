#flask and database support
from flask import Flask, send_from_directory
#loading settings defined in the settings.yaml file
from webapp.settings import app_config 
from datetime import datetime

from webapp.database import db, Grein, UserModel, login
from sqlalchemy import exc, text
import os

app = Flask(__name__)

## import all the routes ##
from webapp.user.routes import user_bp
from webapp.post.routes import post_bp
from webapp.content.routes import content_bp
from webapp.main.routes import main_bp
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(content_bp)

#importing webapp after initialization of app
from webapp.verify import whitelist

app_config = app_config()
# THE SECRET IS USED FOR CREATING CLIENT SESSIONS AND ENCRYPTING THEM
app.secret_key = app_config['secret_key']
app.config['WTF_CSRF_ENABLED'] = True
# Get the current working directory
current_dir = os.getcwd()

#create data folders if they dont exsist
folders_to_create = [f"{current_dir}/database", f"{current_dir}/static/uploads"]
for create_folder in folders_to_create:    
    if not os.path.exists(create_folder):
        os.mkdir(create_folder)

# Set the database URI using string formatting


app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{current_dir}/database/database.db'
# THIS SETTING MAKES DATABASE FASTER AND MORE RELIABLE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

current_dir = os.getcwd()

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

"""Create the database tables if the database exists."""
with app.app_context():
    try:
        with db.engine.connect() as connection:
            connection.execute(text('SELECT * FROM artiklar'))
            print('Database already exists.')
    except exc.OperationalError:
        db.create_all()
        print('Initialized the database.')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main_bp.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')



## BY RUNNING COMMAND 'flask initdb' within app folder,  ##
## this creates an sql database instance                 ##
@app.cli.command('initdb')
def initdb_command():
    """Create the database tables if the database exists."""
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                connection.execute(text('SELECT * FROM artiklar'))
                print('Database already exists.')
        except exc.OperationalError:
            db.create_all()
            print('Initialized the database.')

@app.cli.command('cmdb')
def cmdb():

    # Generate mock database entries
    rootdir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    file_path = os.path.join(rootdir, "loremipsum.txt")
    with open(file_path, 'r') as file:
        loremipsum = file.read().replace('\n', '')
    print(loremipsum)

#
    fornavn = ["Micheal", "Janus", "Jónsvein", "Arnold", "Dánjal"]
    efturnavn = ["Jackson","Kamban", "Joensen", "Astalavista", "Højgaard"]
    stovnur = ["Jarðmóður","javnaðarflokkurin", "Sambandsflokkurin", "Lesandi", "Løgfrøðinur"]
    telefon = ["126232","438303","238603","196824","143876"]
    skriv = loremipsum
    picture_path = ["3dcdeb74-MJ.jpg", "87457ab892-headshot.jpg", "87457ab892-headshot2.jpg", "87457ab892-arnold.jpg", "b641ab7e-simun.jpg"]
    user_id = ["1000000001","1000000002","1000000003","1000000004","1000000005"]
    # retrieve the row to duplicate

    import random
    # create 20 duplicates of the row with new IDs
    for i in range(5):
        brukari = UserModel(
            user_id = user_id[i],
            email=fornavn[i].lower()+efturnavn[i].lower()+"@gmail.com",
            fornavn=fornavn[i],
            efturnavn=efturnavn[i],
            password_hash="pbkdf2:sha256:260000$3hjD7rW3L63l86KR$d940ec3b88828b1d40564cee66be73234a235859c1896037f3cffd5583d82425",
            telefon=telefon[i],
            stovnur=stovnur[i],
            picture_path=picture_path[i],
            created_stamp = datetime.utcnow(),
            vangi = f"{fornavn[i].lower()}.{efturnavn[i].lower()}"
        )
        db.session.add(brukari)
        db.session.commit()
    for i in user_id:
        whitelist(str(i), "whitelist")
        
    for i in range(20):

        random_number = random.randint(0, 4)
        new_id = 10000000 + i + 1  # generate a new ID for each duplicate


        nyggj_grein = Grein(
            grein_id=str(new_id),
            yvirskrift=f"Yvirskrift Nummar {i}",
            grein="<p>"+loremipsum+"</p>",
            author_id = user_id[random_number]
            )
        db.session.add(nyggj_grein)
        db.session.commit()
        #whitelist(str(new_id), "whitelist")
if __name__ == "__main__":
    app.run(debug=True)