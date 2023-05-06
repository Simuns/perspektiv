from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from webapp.database import db, Grein, Stubbi
from webapp.verify import whitelist
import uuid
import json


## DEFINE POST BLUEPRINT ##
post_bp = Blueprint(
    'post', __name__, 
    url_prefix='', 
    static_folder='post_static', 
    template_folder='templates'
)


@post_bp.route('/vel-postform')
def vel_postform():
    return render_template('vel-postform.html')

@post_bp.route('/post-grein', methods=['POST', 'GET'])
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

@post_bp.route('/post-stubbi', methods=['POST', 'GET'])
@login_required
def PostStubbi():
    if request.method == 'POST':
        uuid_obj = uuid.uuid1()
        stubbi_id = uuid_obj.hex[:9]
        request_data = request.get_json()
        stubbi = request_data.get('text')
        print("tekstur", stubbi)
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

