#flask and database support
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, send_from_directory
#loading settings defined in the settings.yaml file
from webapp.settings import app_config 
# handling of verification
# database dependencies
from webapp.database import db, Grein, Verification, UserModel, login, Stubbi
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, text
# Used to handle quill editor data, which for some reason doesnt work with request.json
import json
#image commpression

# Used for creating id's for articles
import uuid

#datetime for timestampings
from datetime import datetime, timedelta

import os

# handle login events
from flask_login import login_required, current_user, login_user, logout_user
# Load settings defined in config.yaml
#regex
import re

app = Flask(__name__)
#importing webapp after initialization of app
from webapp.verify import send_verification, verify, whitelist
from webapp.process_picture import compress_picture, save_picture
from webapp.user import set_vangi
from webapp.serve_content import serve_grein, serve_stubbi


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


@app.route('/')
def index():
    art = serve_grein(Grein.query.order_by(Grein.created_stamp.desc()).limit(10).all())
    return render_template('index.html',art=art)

@app.route('/index_loadMore', methods=['POST', 'GET'])
def index_loadMore():
    ## fetch last article when scrolled to bottom of index page ##
    last_floating_box_id = request.form.get('lastFloatingBoxId')
    print("last floating box id",last_floating_box_id)

    ## find older articles than the last one on the page

    entry = artiklar.query.filter_by(art_id=last_floating_box_id).first()
    ## If the entry was found, retrieve the two articles written prior to it ##
    if entry:
        two_articles_prior = artiklar.query.filter(
            artiklar.created_stamp < entry.created_stamp,
            artiklar.verified == True
        ).order_by(artiklar.created_stamp.desc()).limit(2).all()
        seinastu_artiklar_dict = latest_articles_dict(two_articles_prior)


        for article in seinastu_artiklar_dict:
            time_delta = timeDelta(seinastu_artiklar_dict[article]["created_stamp"])
            seinastu_artiklar_dict[article]["time_delta"] = time_delta

            
            preview_text = preview_article(seinastu_artiklar_dict[article]["skriv"])
            seinastu_artiklar_dict[article]["preview_text"] = preview_text

        
        return render_template('base-prev.html', art=seinastu_artiklar_dict)

@app.route('/brøv/<string:article_id>')
def show_article(article_id):
    art = artiklar.query.join(Verification).filter(artiklar.art_id == article_id, Verification.status == 'verified').first()
    if art is None:
        return render_template('error.html',error="Brævið finst ikki")
    art_dict = rowToDict(art)
    date_string = art_dict["created_stamp"].strftime('%Y-%m-%d')
    art_dict["date_string"] = date_string
    return render_template('article.html',art_dict=art_dict)


@app.route('/vel-postform')
def vel_postform():
    return render_template('vel-postform.html')

@app.route('/post-grein', methods=['POST', 'GET'])
@login_required
def postGrein():
    if request.method == 'POST':
        grein_id = str(uuid.uuid4())[:8]
        json_postdata = request.form.get('contents')
        data = json.loads(json_postdata)
        grein = data['ops'][0]['insert']
        nyggj_grein = Grein(
            grein_id=grein_id,
            yvirskrift="Manglar Yvirskrift",
            grein=grein,
            author_id=current_user.user_id,
        )
        whitelist(grein_id)
        db.session.add(nyggj_grein)
        db.session.commit()
        return jsonify({'success': True}), 200        
    else:
        return render_template('post-grein.html')

@app.route('/post-stubbi', methods=['POST', 'GET'])
@login_required
def PostStubbi():
    if request.method == 'POST':
        uuid_obj = uuid.uuid1()
        stubbi_id = uuid_obj.hex[:9]
        request_data = request.get_json()
        stubbi = request_data.get('text')
        print("tekstur", text)
        print(current_user.user_id)
        print(stubbi_id)
        nyggjur_stubbi = Stubbi(
                stubbi_id=stubbi_id,
                stubbi=stubbi,
                author_id=current_user.user_id)
        
        db.session.add(nyggjur_stubbi)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return render_template('post-stubbi.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'picture' not in request.files:
        return jsonify({'error': 'No picture provided'}), 400

    ## fetch data from /upload path ##
    picture = request.files['picture']
    session_id = request.form['session_id']

    ## compress picture
    picture_filename_jpg = compress_picture(picture, session_id )
    ## Save path in database
    print("saving path")
    save_picture(session_id, picture_filename_jpg)
    response_data = {
            'success': True,
            'url': url_for('static', filename="uploads/large-" + picture_filename_jpg)
            }
    response = make_response(jsonify(response_data))
    response.status_code = 200
    return response

@app.route('/verify_status',methods=['POST', 'GET'])
def verify_status():
    if request.method == 'POST':
        session_id = request.form['session_id']
        verified_code = request.form['verification_code']
        verifyStatus = verify(verified_code, session_id)
        if verifyStatus == "verified":
            return render_template('verify_success.html')
        else:
            art = artiklar.query.filter_by(art_id=session_id).first()
            return render_template('verify.html', session_id=session_id, telefon=art.telefon, status="Kodan var skeiv, prøva umaftur!")

@app.route('/aktivera/<string:code_email>')
def aktivera(code_email):
    match = verify(code_email)
    if match == "verified":
        return("success")
    else: 
        return("false")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(f'/@{current_user.vangi}')

    if request.method == 'POST':
        email = request.form['email']
        fornavn = request.form['fornavn']
        efturnavn = request.form['efturnavn']
        telefon = request.form['telefon']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return ('Email finst longu')
        if UserModel.query.filter_by(telefon=telefon).first():
            return ('telefon finst longu')
        # generate id with 10 Characters
        uuid_obj = uuid.uuid4()
        user_id = uuid_obj.hex[:10]
        

        vangi = set_vangi([fornavn,efturnavn], True)
        
        user = UserModel(
            user_id = user_id,
            email=email,
            fornavn=fornavn,
            efturnavn=efturnavn,
            telefon=telefon,
            vangi=vangi)

        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if app_config["verifyPhone"]:
            send_verification(user_id, "both", [telefon, email])
            return render_template('verify.html', session_id=user_id, telefon=telefon)
        else: 
            whitelist(user_id)
            return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/ritainn', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/profilur')
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')
    return render_template('ritainn.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')



@app.route('/um_meg', methods=['POST', 'GET'])
@login_required
def um_meg():
    if request.method == 'POST':
        form_data = request.form  # get the form data

        for key in form_data:
            value = form_data[key]
            print(f"{key}: {value}")
            if key == 'fornavn':
                current_user.fornavn = value
            elif key == 'efturnavn':
                current_user.efturnavn = value
            elif key == 'stovnur':
                current_user.stovnur = value
            elif key == 'telefon':
                if app_config["verifyPhone"]:
                    pass
                else: 
                    current_user.telefon = value
                current_user.telefon = value
            elif key == 'email':
                if app_config["verifyPhone"]:
                    pass
                else: 
                    current_user.email = value
            elif key == 'vangi':
                if set_vangi(value):
                    current_user.vangi = value
                else:
                    return jsonify({'success': False, 'error': "Prøva okkurt annað, hetta er longu tykið"}), 200

            else: return jsonify({'success': False, 'error': "form not found"}), 200
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        user = UserModel.query.get(current_user.user_id)
        return render_template('um_meg.html',user=user)

@app.route("/um_meg/open")
@login_required
def um_meg_navn():
    target_id = request.args.get('id')
    user = UserModel.query.get(current_user.user_id)
    return render_template('um_meg-open.html', target_id=target_id, user=user)
@app.route('/send_sms', methods=['POST'])
def send_sms():
    if request.method == 'POST':
        if app_config["verifyPhone"]:
            data = request.get_json()
            session_id = data.get('session_id')
            telefon = data.get('telefon')
            print(telefon)
            send_verification(session_id, "sms", telefon, True)
            return jsonify({'success': True}), 200
        else:
            return jsonify({'Phone number sms verification not activated': True}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/@<string:vangi>')
def brukari(vangi):
    user = UserModel.query.filter(UserModel.vangi == vangi).join(Verification).filter(Verification.status == 'verified').first()
    user_owner = False
    if user:
        if current_user.is_authenticated:
            if current_user.user_id == user.user_id:
                user_owner = True
        article_count = Grein.query.join(UserModel).filter(UserModel.user_id == Grein.author_id).order_by(Grein.created_stamp.desc()).count()
        if article_count == 0:
            return render_template('brukari.html', art=False, user=user, user_owner=user_owner)
        art = serve_grein(Grein.query.join(UserModel).filter(user.user_id == Grein.author_id).order_by(Grein.created_stamp.desc()).all())
        stubbi = serve_stubbi(Stubbi.query.join(UserModel).filter(user.user_id == Stubbi.author_id).order_by(Stubbi.created_stamp.desc()).all())
        content= {**art, **stubbi}
        return render_template('brukari.html',art=content, user=user, user_owner=user_owner)
    else:
        return render_template('error.html', error=f'{vangi} finst ikki')


        return render_template('brukari.html')
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



## THIS LOADS CONTENT THAT IS AVAILABLE ON ALL PAGES ##
## I NEED USER AUTHENTICATION STATUS TO BE AWARE IF  ##
## LOGIN BUTTON SHOULD EXSIST OR NOT                 ##
@app.context_processor
def inject_auth():
    if current_user.is_authenticated:
        user = UserModel.query.get(current_user.user_id)
        if user.picture_path:
            return {'authenticated': True, 
                    'picture': user.picture_path,
                    'fornavn': user.fornavn,
                    'vangi': user.vangi}
        else:
            initials = user.fornavn[0].upper() + user.efturnavn[0].upper()
            return {'authenticated': True, 
                    'initials': initials,
                    'fornavn': user.fornavn,
                    'vangi': user.vangi}
    return {'authenticated': False}

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