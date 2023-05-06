from flask import render_template, request, Blueprint
from webapp.database import db, Grein
from datetime import datetime, timedelta

content_bp = Blueprint('content', __name__, url_prefix='', static_folder='content_static', template_folder='templates')

@content_bp.route('/brøv/<string:article_id>')
def show_article(article_id):
    art = artiklar.query.join(Verification).filter(artiklar.art_id == article_id, Verification.status == 'verified').first()
    if art is None:
        return render_template('error.html',error="Brævið finst ikki")
    art_dict = rowToDict(art)
    date_string = art_dict["created_stamp"].strftime('%Y-%m-%d')
    art_dict["date_string"] = date_string
    return render_template('article.html',art_dict=art_dict)

@content_bp.route('/index_loadMore', methods=['POST', 'GET'])
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