from flask_sqlalchemy import SQLAlchemy
# USED FOR TIMESTAMPING
from datetime import datetime
# USED FOR HASHING PASSWORDS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Define Database
db = SQLAlchemy()

## DEFINE ARTILCE TABLE ##
class artiklar(db.Model):
    art_id = db.Column(db.String(8), primary_key=True)
    fornavn = db.Column(db.String(50), nullable=True)
    efturnavn = db.Column(db.String(50), nullable=True)
    stovnur = db.Column(db.String(120), nullable=True)
    telefon = db.Column(db.String(6), nullable=True)
    yvirskrift = db.Column(db.String(120), nullable=True)
    skriv = db.Column(db.Text)
    picture_path = db.Column(db.String(length=120), nullable=True)
    created_stamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    verify = db.relationship("Verification", back_populates="article")


## DEFINE USER TABLE
class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    fornavn = db.Column(db.String(50), nullable=True)
    efturnavn = db.Column(db.String(50), nullable=True)
    telefon = db.Column(db.String(6), nullable=True)
    password_hash = db.Column(db.String())
    created_stamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    
    verify = db.relationship("Verification", back_populates="user")


    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Verification(db.Model):
    __tablename__ = 'verify'

    id = db.Column(db.Integer, primary_key=True)
    code_sms = db.Column(db.String)
    code_email = db.Column(db.String)
    method = db.Column(db.String)
    status = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    article_id = db.Column(db.String, db.ForeignKey('artiklar.art_id'), nullable=True)
    
    user = db.relationship("UserModel", back_populates="verify")
    article = db.relationship("artiklar", back_populates="verify")


from flask_login import LoginManager
login = LoginManager()

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


