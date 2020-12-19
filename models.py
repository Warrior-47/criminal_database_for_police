from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

    police = db.relationship('Police_officers', backref='Users', uselist=False)


class Police_officers(db.Model):
    Username = db.Column(db.String(128), db.ForeignKey('users.Username'))
    Officer_id = db.Column(db.String(8),unique=True,
        nullable=False, primary_key=True)
    Station = db.Column(db.String(32), nullable=True)
    Rank = db.Column(db.String(32), nullable=True)
    Supervisor_id = db.Column(db.String(128), db.ForeignKey('Police_officers.Officer_id'))

    criminals_caught = db.relationship('Caught_by',backref='Police_officers')
    investigations = db.relationship('Investigate_by',backref='Police_officers')


class Criminal(db.Model):
    Criminal_id = db.Column(db.Integer(),primary_key=True,
        nullable=False)
    Name = db.Column(db.String(128), nullable=False)
    Age = db.Column(db.Integer(), nullable=False)
    Nationality = db.Column(db.String(32))
    NID_No = db.Column(db.String(10), unique=True)
    Photo = db.Column(db.String(256))
    Motive = db.Column(db.String(64))
    Phone_No = db.Column(db.String(64))
    Address = db.Column(db.String(128))

    remarks = db.relationship('Remark',backref='Criminal')
    medicals = db.relationship('Medical_History',backref='Criminal')
    polices_caught = db.relationship('Caught_by',backref='Criminal')
    crimes_commited = db.relationship('Committed_by',backref='Criminal')


class Crime(db.Model):
    Case_No = db.Column(db.Integer(),primary_key=True,
        nullable=False)
    Crime_date = db.Column(db.DateTime(), default=datetime.utcnow())
    End_date = db.Column(db.DATE())
    Address = db.Column(db.String(128))

    evidence = db.relationship('Crime_evidence', backref='Crime')
    murder = db.relationship('Murder', backref='Crime', uselist=False)
    fraud = db.relationship('Fraud', backref='Crime', uselist=False)
    drug_trafficking = db.relationship('Drug_trafficking', backref='Crime', uselist=False)
    human_trafficking = db.relationship('Human_trafficking', backref='Crime', uselist=False)
    rape = db.relationship('Rape', backref='Crime', uselist=False)
    investigations = db.relationship('Investigate_by', backref='Crime')
    victims = db.relationship('Victim', backref='Crime')
    victimed = db.relationship('Victimized', backref='Crime')
    witnesses = db.relationship('Witness', backref='Crime')
    witnessed = db.relationship('Witnessed', backref='Crime')
    criminal_commited = db.relationship('Committed_by',backref='Crime')


class Crime_evidence(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key=True)
    Description = db.Column(db.String(128))
    Collection_date = db.Column(db.DateTime(), default=datetime.utcnow())
    location = db.Column(db.String(128))


class Murder(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Murder_type = db.Column(db.String(32))


class Fraud(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Amount = db.Column(db.Integer())


class Drug_trafficking(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)

    drugs = db.relationship('Drugs', backref='Drug_trafficking')


class Drugs(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Drug_trafficking.Case_No'), primary_key = True)
    Drug = db.Column(db.String(32), primary_key = True)


class Human_trafficking(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Destination = db.Column(db.String(64))


class Rape(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)


class Criminal_Remarks(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Criminal.Criminal_id'), primary_key=True)
    Remark = db.Column(db.String(64),primary_key=True)


class Medical_History(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Criminal.Criminal_id'), primary_key=True)
    Criminal_name = db.Column(db.String(128), primary_key=True, index=True)
    Doctor_name = db.Column(db.String(128), nullable=False)
    Doctor_No = db.Column(db.String(11))

    diseases = db.relationship('Criminal_diseases',backref='Medical_History')
    disabilities = db.relationship('Criminal_disability',backref='Medical_History')


class Criminal_diseases(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Medical_History.Criminal_id'),
        primary_key=True)
    Criminal_name = db.Column(db.String(128), db.ForeignKey('Medical_History.Criminal_name'),
        primary_key=True)
    Disease = db.Column(db.String(32), primary_key=True)


class Criminal_disability(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Medical_History.Criminal_id'),
        primary_key=True)
    Criminal_name = db.Column(db.String(128), db.ForeignKey('Medical_History.Criminal_name'),
        primary_key=True)
    Disability = db.Column(db.String(64), primary_key=True)


class Caught_by(db.Model):
    Officer_id = db.Column(db.String(8), db.ForeignKey('Police_officers.officer_id'), primary_key=True)
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Criminal.Criminal_id'), primary_key=True)
    Start_date = db.Column(db.DateTime(), default=datetime.utcnow())
    End_date = db.Column(db.DateTime())


class Investigate_by(db.Model):
    Officer_id = db.Column(db.String(8), db.ForeignKey('Police_officers.officer_id'), primary_key=True)
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)


class Committed_by(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey('Criminal.Criminal_id'), primary_key=True)
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)


class Victim(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key=True)
    Name = db.Column(db.String(128),primary_key=True, index=True)
    Age = db.Column(db.Integer(), nullable=False)
    Phone_No = db.Column(db.String(11))
    Address = db.Column(db.String(128))

    victimized = db.relationship('Victimized',backref='Victim')


class Witness(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Name = db.Column(db.String(128),primary_key=True, index=True)
    Age = db.Column(db.Integer(), nullable=False)
    Phone_No = db.Column(db.String(11))
    Address = db.Column(db.String(128))

    witnessed = db.relationship('Witnessed',backref='Witness')


class Witnessed(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Name = db.Column(db.String(128), db.ForeignKey('Witness.Name'), primary_key=True)


class Victimized(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey('Crime.Case_No'), primary_key = True)
    Name = db.Column(db.String(128), db.ForeignKey('Victim.Name'), primary_key=True)
