#flask and database support
from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, send_from_directory
#loading settings defined in the settings.yaml file
from webapp.settings import app_config
# handling of verification
# database dependencies
from webapp.database import db, artiklar, Verification, UserModel, login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, text

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


app_config = app_config()
# THE SECRET IS USED FOR CREATING CLIENT SESSIONS AND ENCRYPTING THEM
app.secret_key = app_config['secret_key']
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
    article_count = artiklar.query.count()
    if article_count == 0:
        session_id = str(uuid.uuid4())[:8]
        return render_template('skriva.html', session_id=session_id)
    seinastu_artiklar_dbRaw = artiklar.query.join(Verification).filter(Verification.status == 'verified').order_by(artiklar.created_stamp.desc()).limit(10).all()
    seinastu_artiklar_dict = latest_articles_dict(seinastu_artiklar_dbRaw)
    for article in seinastu_artiklar_dict:
        time_delta = timeDelta(seinastu_artiklar_dict[article]["created_stamp"])
        seinastu_artiklar_dict[article]["time_delta"] = time_delta

        preview_text = preview_article(seinastu_artiklar_dict[article]["skriv"])
        seinastu_artiklar_dict[article]["preview_text"] = preview_text

    return render_template('index.html',art=seinastu_artiklar_dict)

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

@app.route('/skriva', methods=['POST', 'GET'])
def skriva():

    if request.method == 'POST':

        session_id = request.form['session_id']
        fornavn = request.form['fornavn']
        efturnavn = request.form['efturnavn']
        stovnur = request.form['stovnur']
        telefon = request.form['telefon']
        yvirskrift = request.form['yvirskrift']
        quill_data = request.form.get('text')
        print(request.form.get('text'))
        art = artiklar.query.filter_by(art_id=session_id).first()
        if art:
            print("USER FOUND WITH SESSION ID:",session_id,"updating user")
            art.fornavn=fornavn
            art.efturnavn=efturnavn
            art.stovnur=stovnur
            art.telefon=telefon
            art.yvirskrift=yvirskrift
            art.skriv=quill_data
            art.created_stamp = datetime.utcnow()

        else:
            print("NO USER FOUND WITH USER ID",session_id)
            nytt_skriv = artiklar(
                art_id=session_id,
                fornavn=fornavn,
                efturnavn=efturnavn,
                stovnur=stovnur,
                telefon=telefon,
                yvirskrift=yvirskrift,
                skriv=quill_data,
                created_stamp = datetime.utcnow(),
                )

            db.session.add(nytt_skriv)
        db.session.commit()

        if app_config["verifyPhone"]:
            send_verification(session_id, "article", "sms", telefon)
            return render_template('verify.html', session_id=session_id, telefon=telefon)
        else:
            whitelist(session_id)
            return redirect(url_for('index'))
    session_id = str(uuid.uuid4())[:8]
    return render_template('skriva.html', session_id=session_id)

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
        return redirect('/profilur')

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
            return render_template('ritainn.html')
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
            return redirect('/profilur')
    return render_template('ritainn.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/profilur')

@app.route('/profilur')
@login_required
def profilur():

    user = UserModel.query.filter_by(user_id=current_user.user_id).first()
    seinastu_artiklar_dbRaw = artiklar.query.join(Verification).filter(Verification.status == 'verified').join(artiklar.author).filter_by(telefon=user.telefon).all()
    if len(seinastu_artiklar_dbRaw) == 0:
        seinastu_artiklar_dict = False
    else:
        seinastu_artiklar_dict = latest_articles_dict(seinastu_artiklar_dbRaw)
        for article in seinastu_artiklar_dict:
            seinastu_artiklar_dict[article]["created_stamp"] = seinastu_artiklar_dict[article]["created_stamp"].strftime('%Y-%m-%d')


    return render_template('profilur.html', art=seinastu_artiklar_dict)


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


#@app.route('/b/<string:user>')


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


## USED TO HANDLE DATABASE TABLE INPUT ##
## AND CLEAN DATA OUTPUT IN DICTIONARY ##      
def rowToDict(row):
    newDict = row.__dict__
    del newDict['_sa_instance_state']
    return newDict


## USED TO GET NESTED ARTICLE DICTIONARY FROM DATABASE OUTPUT ##
## CAN BE PARSED DIRECTLY INTO HTML AND USED WITH JINJA       ##
def latest_articles_dict(databaseOutput):
    # Create a list of dictionaries and number each one
    dict_list = []
    for i in databaseOutput:
        artikkul_dict = rowToDict(i)
        dict_list.append(artikkul_dict)
    for i, d in enumerate(dict_list):
        dict_list[i] = {i+1: d}

    # Combine the list of dictionaries into a nested dictionary
    nested_dict = {}
    for d in dict_list:
        nested_dict.update(d)
    return nested_dict

## USED TO ADD REALTIME TIMEDELTA TO HTML BASED ON TIMESTAMPING##
def timeDelta(timestamp):
    now = datetime.utcnow()
    delta = now - timestamp
    if delta < timedelta(days=1):
        if delta < timedelta(hours=1):
            return "Beint nú"
        else:
            hours_ago = int(delta.total_seconds() // 3600)
            return f"{hours_ago} tímar síðan"
    else:
        if delta > timedelta(days=1) and delta < timedelta(days=2):
            return "Í gjár"
        else:
            days_ago = delta.days
            return f"{days_ago} dagar síðani"


    ###THIS SECTION REMOVES ALL HTML SYNTAX FROM TEXT###
def preview_article(text, preview_lenght=40):
    print("text",text)
    # Define the regular expression pattern to search for
    pattern = r"<[^>]+>"
    # Define the replacement string
    replacement = ''
    # Replace all occurrences of the pattern in the text with the replacement string
    clean_text = re.sub(pattern, replacement, text)

    ### THIS SECTION CUTS THE TEXT TO PREVIEW ###
    words = clean_text.split()
    if len(words) < preview_lenght:
        return "<p>"+clean_text+"</p>"
    else:
        shortened_text = " ".join(words[:preview_lenght])
        return "<p>"+shortened_text+"..."+"</p>"


## THIS LOADS CONTENT THAT IS AVAILABLE ON ALL PAGES ##
## I NEED USER AUTHENTICATION STATUS TO BE AWARE IF  ##
## LOGIN BUTTON SHOULD EXSIST OR NOT                 ##
@app.context_processor
def inject_auth():
    if current_user.is_authenticated:
        user = UserModel.query.get(current_user.user_id)
        if user.picture_path:
            return {'authenticated': True, 
                    'picture': user.picture_path}
        else:
            initials = user.fornavn[0].upper() + user.efturnavn[0].upper()
            return {'authenticated': True, 
                    'initials': initials}
    return {'authenticated': False}



@app.cli.command('dbq')
def dbq():
    pass
if __name__ == "__main__":
    app.run(debug=True)