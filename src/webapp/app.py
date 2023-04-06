from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime, timedelta

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


@app.route('/')
def index():
    seinastu_artiklar_dbRaw = artiklar.query.order_by(artiklar.created_stamp.desc()).limit(10).all()
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
        print("request form",request.form)
        
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
                created_stamp = datetime.utcnow()
                )
            db.session.add(nytt_skriv)
            db.session.commit()

        art = artiklar.query.filter_by(id=session_id).first()
        art_dict = rowToDict(art)

        return render_template('framsyning.html',picture_path=art.picture_path,art_dict=art_dict)
    
    session_id = str(uuid.uuid4())[:8]
    return render_template('skriva.html', session_id=session_id)

@app.route('/upload', methods=['POST'])
def upload():
    if 'picture' not in request.files:
        return jsonify({'error': 'No picture provided'}), 400

    picture = request.files['picture']
    session_id = request.form['session_id']
    picture.save('static/uploads/'+ session_id + "-" + picture.filename)
    nyggj_mynd = artiklar(
        id=session_id,
        picture_path=session_id + "-" + picture.filename)
    db.session.add(nyggj_mynd)
    db.session.commit()

    return jsonify({'success': True}), 200

@app.cli.command('initdb')
def initdb_command():
    """Create the database tables."""
    with app.app_context():
        db.create_all()
    print('Initialized the database.')    

if __name__ == "__main__":
    app.run(debug=True)

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
