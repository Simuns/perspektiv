import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import random
from webapp.settings import app_config
from webapp.database import db, artiklar,UserModel, Verification
from webapp.app import app


# Load configurations
app_config = app_config()

def send_verification(id, context, method, recipients, resend=False):

    with app.app_context():
        verification = db.session.query(Verification).filter((Verification.article_id == id) | (Verification.user_id == id)).first()
        if resend is False:
            if verification:
                # Delete previous verifications set by this user or article
                db.session.delete(verification)
                # Create new verification
            verification = Verification(status='pending', method=method)

        if context == "user":
            verification.user_id = id
    
        if context == "article":
            verification.article_id = id

                
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
    code = random.randint(100000, 999999)
    sg = sendgrid.SendGridAPIClient(api_key=app_config['verify_apiKey'])
    from_email = Email(app_config['verify_senderMail'])  # Change to your verified sender

    if verifyType == "sms":
        to_email = To(recipient+'@'+app_config['verify_receiver'])  # Change to your recipient
        subject = "SMS FRÁ perspektiv.fo"
        content = Content("text/plain", f"Vátta við kodu: {code}")

    if verifyType == 'email':
        from_email = Email(app_config['verify_senderMail'])  # Change to your verified sender
        to_email = To(recipient)  # Change to your recipient
        subject = "perspektiv.fo Váttan"
        content = Content("text/plain", f"Vátta við kodu: {code}")

    mail = Mail(from_email, to_email, subject, content)
    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
    return code


def verify(id, method, code):
    with app.app_context():
        verify = db.session.query(Verification).filter((Verification.article_id == id) | (Verification.user_id == id)).first()

        if method == "sms" and verify.code_sms == code:
            verify.status = "verified"
            db.session.commit()
            return "verified"

        elif method == "email" and verify.code_email == code:
            verify.status = "verified"
            db.session.commit()
            return "verified"

        elif verify.method == "both":
            if verify.status == "pending" and method == "email" and verify.code_email == code:
                verify.status = "email"
                db.session.commit()
                return "verified"
            
            elif verify.status == "pending" and method == "sms" and verify.code_sms == code:
                verify.status = "sms"
                db.session.commit()
                return "verified"
            
            elif verify.status == "sms" and method == "email" and verify.code_email == code:
                verify.status = "verified"
                db.session.commit()
                return "verified"

            elif verify.status == "email" and method == "sms" and verify.code_sms == code:
                verify.status = "verified"
                db.session.commit()
                return "verified"
    return "unverified"