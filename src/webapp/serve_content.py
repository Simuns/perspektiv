from datetime import datetime, timedelta
from webapp.database import db, Grein, UserModel, Stubbi, Verification
import re
from sqlalchemy import desc
def serve_content(db_qureryContent):
    content_dict = latest_articles_dict(db_qureryContent)
    for content in content_dict:
        print(content)
        if 'grein_id' in content_dict[content].keys():
            content  = serve_grein(content_dict[content])
        elif 'stubbi_id' in content_dict[content].keys():
            content = serve_stubbi(content_dict[content])
        else:
            print(content_dict[content])
            return False
    return content_dict

def serve_grein(content):
    user = UserModel.query.join(Grein.author).filter(Grein.grein_id == content['grein_id']).first()
    ## add user specific information to the contents
    content["vangi"] = user.vangi
    content["fornavn"] = user.fornavn
    content["efturnavn"] = user.efturnavn
    content["picture_path"] = user.picture_path
    content["stovnur"] = user.stovnur
    time_delta = timeDelta(content["created_stamp"])
    content["time_delta"] = time_delta

    preview_text = preview_article(content["grein"])
    content["preview_text"] = preview_text
    return content


def serve_stubbi(content):
    user = UserModel.query.join(Stubbi.author).filter(Stubbi.stubbi_id == content['stubbi_id']).first()
    ## add user specific information to the contents
    content["vangi"] = user.vangi
    content["fornavn"] = user.fornavn
    content["efturnavn"] = user.efturnavn
    content["picture_path"] = user.picture_path
    time_delta = timeDelta(content["created_stamp"])
    content["time_delta"] = time_delta

    preview_text = preview_article(content["stubbi"])
    content["preview_text"] = preview_text
    return content


### sort out if query is of type union with multiple content types included ###
def sort_unionQuery(db_qureryContent):
    query_list = []
    for result in db_qureryContent.all():
        if len(result[0]) == 8:
            content = Grein.query.filter_by(grein_id=result[0]).first()
        elif len(result[0]) == 9:
            content = Stubbi.query.filter_by(stubbi_id=result[0]).first()
        query_list.append(content)
    return query_list

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


## USED TO HANDLE DATABASE TABLE INPUT ##
## AND CLEAN DATA OUTPUT IN DICTIONARY ##      
def rowToDict(row):
    newDict = row.__dict__
    del newDict['_sa_instance_state']
    return newDict

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
    

def query_latest_content(user=False, limit_Nr=10, status="verified"):
    grein_query = db.session.query(
        Grein.grein_id,
        Grein.created_stamp,
        Grein.author_id,
    ).join(Verification, Grein.grein_id == Verification.article_id)
    
    grein_query = grein_query.filter(Verification.status == status)

    if user:
        grein_query = grein_query.filter(Grein.author_id == user)

    stubbi_query = db.session.query(
        Stubbi.stubbi_id,
        Stubbi.created_stamp,
        Stubbi.author_id,
    )
    if user:
        stubbi_query = stubbi_query.filter(Stubbi.author_id == user)

    latest_content = (
        grein_query.union(stubbi_query)
        .order_by(desc(Grein.created_stamp), desc(Stubbi.created_stamp))
        .limit(limit_Nr)
    )
    return latest_content