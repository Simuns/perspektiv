from flask import Blueprint, request, render_template, redirect, jsonify, url_for
from webapp.database import db, Grein, Verification, UserModel, login, Stubbi
import uuid
from webapp.serve_content import serve_content, query_latest_content, sort_unionQuery
from webapp.verify import send_verification
from flask_login import login_required, current_user, login_user, logout_user
from .utils import set_vangi
from webapp.verify import send_verification, verify, whitelist
from webapp.settings import app_config

user_bp = Blueprint(
    'user', 
    __name__, 
    url_prefix='', 
    static_folder='user_static', 
    template_folder='templates'
)


## LOAD SETTINGS FROM SETTINGS YAML FILE
app_config = app_config()


@user_bp.route('/register', methods=['POST', 'GET'])
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
            return redirect(url_for('user.login'))
    else:
        return render_template('register.html')

@user_bp.route('/ritainn', methods = ['POST', 'GET'])
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

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@user_bp.route('/um_meg', methods=['POST', 'GET'])
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

@user_bp.route("/um_meg/open")
@login_required
def um_meg_navn():
    target_id = request.args.get('id')
    user = UserModel.query.get(current_user.user_id)
    return render_template('um_meg-open.html', target_id=target_id, user=user)


@user_bp.route('/@<string:vangi>')
def brukari(vangi):
    user = UserModel.query.filter(UserModel.vangi == vangi).join(Verification).filter(Verification.status == 'verified').first()
    user_owner = False
    if user:
        if current_user.is_authenticated:
            if current_user.user_id == user.user_id:
                user_owner = True
        article_count = Grein.query.join(UserModel).filter(UserModel.user_id == Grein.author_id).order_by(Grein.created_stamp.desc()).count()
        user_content = query_latest_content(user.user_id)
        sorted_user_content = sort_unionQuery(user_content)
        content = serve_content(sorted_user_content)
        return render_template('brukari.html',art=content, user=user, user_owner=user_owner)
    else:
        return render_template('error.html', error=f'{vangi} finst ikki')