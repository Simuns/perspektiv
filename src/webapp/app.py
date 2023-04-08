#flask and database support
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, text
# Used for creating id's for articles
import uuid
#datetime for timestampings
from datetime import datetime, timedelta
# Verify phone number with email sending
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import yaml
# generate code
import random
# Used for picture reduction in size
from PIL import Image


#### load configurations ####
# Get the absolute path of the grandparent directory (3 layers up)
rootdir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
# Load the file from the grandparent directory
file_path = os.path.join(rootdir, "config.yaml")
with open(file_path, "r") as file:
    # Read the contents of the file
    config = yaml.safe_load(file)






app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artiklar.db'
db = SQLAlchemy(app)



#db = SQLAlchemy(app)
class artiklar(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    fornavn = db.Column(db.String(50), nullable=True)
    efturnavn = db.Column(db.String(50), nullable=True)
    stovnur = db.Column(db.String(120), nullable=True)
    telefon = db.Column(db.String(6), nullable=True)
    yvirskrift = db.Column(db.String(120), nullable=True)
    skriv = db.Column(db.Text)
    picture_path = db.Column(db.String(length=120), nullable=True)
    created_stamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    verified = db.Column(db.Boolean, default=False)
    vercode = db.Column(db.String(6), nullable=True)

@app.route('/')
def index():
    article_count = artiklar.query.count()
    if article_count == 0:
        session_id = str(uuid.uuid4())[:8]
        return render_template('skriva.html', session_id=session_id)
    #seinastu_artiklar_dbRaw = artiklar.query.order_by(artiklar.created_stamp.desc()).limit(10).all()
    seinastu_artiklar_dbRaw = artiklar.query.filter_by(verified=True).order_by(artiklar.created_stamp.desc()).limit(10).all()
    seinastu_artiklar_dict = latest_articles_dict(seinastu_artiklar_dbRaw)
    for article in seinastu_artiklar_dict:
        time_delta = timeDelta(seinastu_artiklar_dict[article]["created_stamp"])
        seinastu_artiklar_dict[article]["time_delta"] = time_delta

        
        preview_text = preview_article(seinastu_artiklar_dict[article]["skriv"])
        seinastu_artiklar_dict[article]["preview_text"] = preview_text

    return render_template('index.html',art=seinastu_artiklar_dict)

@app.route('/brøv/<string:article_id>')
def show_article(article_id):
    art = artiklar.query.filter_by(id=article_id).first()
    if art is None:
        return render_template('error.html',error="Brævið finst ikki")
    if art.verified:
        art_dict = rowToDict(art)
        date_string = art_dict["created_stamp"].strftime('%Y-%m-%d')
        art_dict["date_string"] = date_string
        return render_template('article.html',art_dict=art_dict)
    else:
        return render_template('error.html',error="Brævið er ikki váttað enn")

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
        print("request form",request.form)
        
        if config["verifyPhone"]:
            #generate code
            code = random.randint(100000, 999999)
        art = artiklar.query.filter_by(id=session_id).first()
        if art:
            print("USER FOUND WITH SESSION ID:",session_id,"updating user")
            art.fornavn=fornavn
            art.efturnavn=efturnavn
            art.stovnur=stovnur
            art.telefon=telefon
            art.yvirskrift=yvirskrift
            art.skriv=quill_data
            art.created_stamp = datetime.utcnow()
            if config["verifyPhone"]:
                art.vercode=code
            else:
                art.verified=True
            db.session.commit()
        else:
            print("NO USER FOUND WITH USER ID",session_id)
            nytt_skriv = artiklar(
                id=session_id,
                fornavn=fornavn,
                efturnavn=efturnavn,
                stovnur=stovnur,
                telefon=telefon,
                yvirskrift=yvirskrift,
                skriv=quill_data,
                created_stamp = datetime.utcnow(),
                vercode = code if config["verifyPhone"] else None,
                verified = False if config["verifyPhone"] else True
                )

            db.session.add(nytt_skriv)
            db.session.commit()

        if config["verifyPhone"]:
            verifyPhone(config, telefon, code)
            return render_template('verify.html', session_id=session_id, telefon=telefon)
        else:
            return redirect(url_for('index'))
    session_id = str(uuid.uuid4())[:8]
    return render_template('skriva.html', session_id=session_id)

@app.route('/upload', methods=['POST'])
def upload():
    if 'picture' not in request.files:
        return jsonify({'error': 'No picture provided'}), 400

    picture = request.files['picture']
    session_id = request.form['session_id']
    picture_filename = session_id + "-" + picture.filename
    large_picture_filename =  "large-" + picture_filename
    picture.save('static/uploads/'+ large_picture_filename)


    ## Process image ##
    open_raw_picture_filename = Image.open('static/uploads/' + large_picture_filename)
    width, height = open_raw_picture_filename.size
    TARGET_WIDTH = 100
    coefficient = width / 100
    new_height = height / coefficient
    small_picture = open_raw_picture_filename.resize((int(TARGET_WIDTH),int(new_height)),Image.ANTIALIAS)
    small_picture_filename='small-' + os.path.splitext(picture_filename)[0] + '.jpg'
    small_picture.save(f"static/uploads/{small_picture_filename}")

    nyggj_mynd = artiklar(
        id=session_id,
        picture_path=picture_filename)
    db.session.add(nyggj_mynd)
    db.session.commit()

    return jsonify({'success': True}), 200







@app.route('/verify_status',methods=['POST', 'GET'])
def verify_status():
    if request.method == 'POST':
        session_id = request.form['session_id']
        verified_code = request.form['verification_code']
        art = artiklar.query.filter_by(id=session_id).first()
        if verified_code == art.vercode:
            if art:
                print("USER FOUND WITH SESSION ID:",session_id,"updating verified status")
                art.verified=True
                db.session.commit()

            return render_template('verify_success.html')
        else:
            return render_template('verify.html', session_id=session_id, telefon=art.telefon, status="Kodan var skeiv, prøva umaftur!")

@app.route('/send_sms', methods=['POST'])
def send_sms():
    if request.method == 'POST':
        if config["verifyPhone"]:
            data = request.get_json()
            session_id = data.get('session_id')
            art = artiklar.query.filter_by(id=session_id).first()
            verifyPhone(config, art.telefon, art.vercode)
            return jsonify({'success': True}), 200
        else:
            return jsonify({'Phone number sms verification not activated': True}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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


def rowToDict(row):
    newDict = row.__dict__
    del newDict['_sa_instance_state']
    return newDict


def latest_articles_dict(databaseOutput):
    # Create a list of dictionaries and number each one
    print("heybreyð",databaseOutput)
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

def preview_article(text, preview_lenght=40):
    import re

    ###THIS SECTION REMOVES ALL HTML SYNTAX FROM TEXT###
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


def verifyPhone(config, phoneNumber, code):
    if config['verifyPhone']:
        sg = sendgrid.SendGridAPIClient(api_key=config['verify_apiKey'])
        from_email = Email(config['verify_senderMail'])  # Change to your verified sender
        to_email = To(phoneNumber+'@'+config['verify_receiver'])  # Change to your recipient
        subject = "Perspektiv Koda"
        content = Content("text/plain", f"Verification code is: {code}")
        mail = Mail(from_email, to_email, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)
        print(response.status_code)
        print(response.headers)

if __name__ == "__main__":
    app.run(debug=True)