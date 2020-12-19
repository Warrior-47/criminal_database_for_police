from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    Username = db.Column(db.String(128), primary_key=True,
        unique=True, nullable=False)
    Name = db.Column(db.String(128),unique=True,
        nullable=False)
    NID_No = db.Column(db.String(10), unique=True, nullable=True)
    Gender = db.Column(db.String(1), nullable=False)
    Pass = db.Column(db.String(64), nullable=False)
    Phone_No = db.Column(db.String(11), nullable=True)
    Personal_email = db.Column(db.String(128), unique=True,
        nullable=False)
    Department_email = db.Column(db.String(128), unique=True,
        nullable=False)
    privilege = db.Column(db.SmallInteger(), nullable=False)
    police = db.relationship('Police_officers', backref='users', uselist=False)


class Police_officers(db.Model):
    Username = db.Column(db.String(128), db.ForeignKey('users.Username'))
    Officer_id = db.Column(db.String(8),unique=True,
        nullable=False, primary_key=True)
    Station = db.Column(db.String(32), nullable=True)
    Rank = db.Column(db.String(32), nullable=True)
    Supervisor_id = db.Column(db.String(128), db.ForeignKey('Police_officers.Officer_id'))
    
