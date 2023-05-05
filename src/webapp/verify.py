import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import random
from webapp.settings import app_config
from webapp.database import db, Grein, UserModel, Verification
from webapp.app import app
import uuid
from datetime import datetime

# Load configurations
app_config = app_config()

def send_verification(context_id, method, recipients, resend=False):
    with app.app_context():
        verification = db.session.query(Verification).filter((Verification.article_id == context_id) | (Verification.user_id == context_id)).first()
        if verification is None:
            print(context_id)
            print("no content matching id found")

        if resend is False:
            if verification:
                # Delete previous verifications set by this user or article
                db.session.delete(verification)
                # Create new verification
            verification = Verification(status='pending', method=method)

        if len(context_id) == 8:
            verification.article_id = context_id
        if len(context_id) == 10:
            verification.user_id = context_id
    
                
        if method == "sms": 
            code_sms = send(app_config, recipients, "sms")
            verification.code_sms = code_sms

        if method == "email":
            code_email = send(app_config, recipients, "email")
            verification.code_email = code_email

        if method == "both":
            telefon, email = recipients
            code_sms = send(app_config, telefon, "sms")
            code_email = send(app_config, email, "email")
            verification.code_sms = code_sms
            verification.code_email = code_email

        if resend is False:
            #Merge changes with database
            db.session.add(verification)
        db.session.commit()

## USED TO SEND SMS's TO THE END USER ##
# THIS IS ACHIEVED BY FIRST SENDING MAIL TO MAIL->SMS RELAY #
def send(app_config, recipient, verifyType):
    sg = sendgrid.SendGridAPIClient(api_key=app_config['verify_apiKey'])
    from_email = Email(app_config['verify_senderMail'])  # Change to your verified sender

    if verifyType == "sms":
        code = random.randint(100000, 999999)
        to_email = To(recipient+'@'+app_config['verify_receiver'])  # Change to your recipient
        subject = "SMS FRÁ perspektiv.fo"
        content = Content("text/plain", f"Vátta við kodu: {code}")

    if verifyType == 'email':
        code = str(uuid.uuid4())
        from_email = Email(app_config['verify_senderMail'])  # Change to your verified sender
        to_email = To(recipient)  # Change to your recipient
        subject = "perspektiv.fo Váttan"
        content = Content("text/plain", f"Vátta við at trýsta á leinkjuna: {app_config['verifify_activationPath']}{code}")

    mail = Mail(from_email, to_email, subject, content)
    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
    return code

def verify(code, id=None):
    with app.app_context():
        if len(code) == 36: # Email verification codes are 36 character long
            verify = db.session.query(Verification).filter(Verification.code_email == code).first()
            if not verify:
                return "unverified"
            print("code =",code, "databaseEntry",verify)
            if verify.method == "email":
                verified = True

            if verify.method == "both":
                if verify.status == "pending":
                    verify.status = "email"
                    db.session.commit()
                    return "verified"
                
                elif verify.status == "sms":
                    verified = True


        elif len(code) == 6: # sms verification codes are 6 character long
            verify = db.session.query(Verification).filter((Verification.article_id == id) | (Verification.user_id == id)).first()
            if not verify:
                return "unverified"
            if verify.method == "sms" and verify.code_sms == code:
                verified = True

            elif verify.method == "both":
                if verify.status == "pending" and verify.code_sms == code:
                    verify.status = "sms"
                    db.session.commit()
                    return "verified"
                
                elif verify.status == "email" and verify.code_sms == code:
                    verified = True

                    return "verified"
        if verified:
            verify.status = "verified"
            verify.verified_stamp = datetime.utcnow()
            db.session.commit()
            return "verified"
        
        else: return "unverified"

def whitelist(context_id, method="whitelist"):
    with app.app_context():
        whitelisting = Verification(status='verified', method=method)
        if len(context_id) == 8:
            whitelisting.article_id = context_id
        if len(context_id) == 10:
            whitelisting.user_id = context_id
        whitelisting.verified_stamp = datetime.utcnow()
        db.session.add(whitelisting)
        db.session.commit()
    return "verified"



