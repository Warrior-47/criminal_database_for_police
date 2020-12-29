from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from application import db

""" The Model for my entire database """


class Users(UserMixin, db.Model):
    Username = db.Column(db.String(128), primary_key=True,
                         unique=True, nullable=False)

    def get_id(self):
        return self.Username
    Name = db.Column(db.String(128), unique=True,
                     nullable=False)
    NID_No = db.Column(db.String(10), unique=True, nullable=True)
    Gender = db.Column(db.String(1), nullable=False)
    Pass = db.Column(db.String(96), nullable=False)
    Phone_No = db.Column(db.String(11), nullable=True)
    Personal_email = db.Column(db.String(128), unique=True,
                               nullable=False)
    Department_email = db.Column(db.String(128), unique=True,
                                 nullable=False)
    privilege = db.Column(db.SmallInteger(), nullable=False)

    police = db.relationship("police_officers", backref="Users", uselist=False)


class police_officers(db.Model):
    Username = db.Column(db.String(128), db.ForeignKey("users.Username"))
    Officer_id = db.Column(db.String(8), unique=True,
                           nullable=False, primary_key=True)
    Station = db.Column(db.String(32), nullable=True)
    Rank = db.Column(db.String(32), nullable=True)
    Supervisor_id = db.Column(db.String(128), db.ForeignKey("police_officers.Officer_id"))
    Clearance = db.Column(db.Integer(), nullable=False, default=10)

    criminals_caught = db.relationship("Caught_by", backref="police_officers")
    investigations = db.relationship("Investigate_by", backref="police_officers")


class criminal(db.Model):
    Criminal_id = db.Column(db.Integer(), primary_key=True,
                            nullable=False)
    Name = db.Column(db.String(128), nullable=False)
    Age = db.Column(db.Integer(), nullable=False)
    Nationality = db.Column(db.String(32))
    NID_No = db.Column(db.String(10), unique=True)
    Photo = db.Column(db.String(256))
    Motive = db.Column(db.String(64))
    Phone_No = db.Column(db.String(64))
    Address = db.Column(db.String(128))

    remarks = db.relationship("criminal_remarks", backref="criminal")
    medicals = db.relationship("medical_history", backref="criminal")
    polices_caught = db.relationship("Caught_by", backref="criminal")
    crimes_commited = db.relationship("Committed_by", backref="criminal")


class crime(db.Model):
    Case_No = db.Column(db.Integer(), primary_key=True,
                        nullable=False)
    Crime_date = db.Column(db.DateTime(), default=datetime.utcnow())
    End_date = db.Column(db.DATE())
    Address = db.Column(db.String(128))
    Clearance = db.Column(db.Integer(), nullable=False, default=10)

    evidence = db.relationship("Crime_evidence", backref="crime")
    murder = db.relationship("Murder", backref="crime", uselist=False)
    fraud = db.relationship("Fraud", backref="crime", uselist=False)
    drug_trafficking = db.relationship("drug_trafficking", backref="crime", uselist=False)
    human_trafficking = db.relationship("Human_trafficking", backref="crime", uselist=False)
    rape = db.relationship("Rape", backref="crime", uselist=False)
    investigations = db.relationship("Investigate_by", backref="crime")
    victims = db.relationship("victim", backref="crime")
    victimed = db.relationship("Victimized", backref="crime")
    witnesses = db.relationship("witness", backref="crime")
    witnessed = db.relationship("Witnessed", backref="crime")
    criminal_commited = db.relationship("Committed_by", backref="crime")


class Crime_evidence(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Description = db.Column(db.String(128))
    Collection_date = db.Column(db.DateTime(), default=datetime.utcnow())
    location = db.Column(db.String(128))


class Murder(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Murder_type = db.Column(db.String(32))


class Fraud(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Amount = db.Column(db.Integer())


class drug_trafficking(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)

    drugs = db.relationship("Drugs", backref="drug_trafficking")


class Drugs(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("drug_trafficking.Case_No"), primary_key=True)
    Drug = db.Column(db.String(32), primary_key=True)


class Human_trafficking(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Destination = db.Column(db.String(64))


class Rape(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)


class criminal_remarks(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("criminal.Criminal_id"), primary_key=True)
    Remark = db.Column(db.String(64), primary_key=True)


class medical_history(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("criminal.Criminal_id"), primary_key=True)
    Criminal_name = db.Column(db.String(128), primary_key=True, index=True)
    Doctor_name = db.Column(db.String(128), nullable=False)
    Doctor_No = db.Column(db.String(11))

    diseases = db.relationship("Criminal_diseases", backref="medical_history",
                               primaryjoin="and_(medical_history.Criminal_id==Criminal_diseases.Criminal_id, medical_history.Criminal_name==Criminal_diseases.Criminal_name)")
    disabilities = db.relationship("Criminal_disability", backref="medical_history",
                                   primaryjoin="and_(medical_history.Criminal_id==Criminal_disability.Criminal_id, medical_history.Criminal_name==Criminal_disability.Criminal_name)")


class Criminal_diseases(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("medical_history.Criminal_id"),
                            primary_key=True)
    Criminal_name = db.Column(db.String(128), db.ForeignKey("medical_history.Criminal_name"),
                              primary_key=True)
    Disease = db.Column(db.String(32), primary_key=True)


class Criminal_disability(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("medical_history.Criminal_id"),
                            primary_key=True)
    Criminal_name = db.Column(db.String(128), db.ForeignKey("medical_history.Criminal_name"),
                              primary_key=True)
    Disability = db.Column(db.String(64), primary_key=True)


class Caught_by(db.Model):
    Officer_id = db.Column(db.String(8), db.ForeignKey(
        "police_officers.Officer_id"), primary_key=True)
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("criminal.Criminal_id"), primary_key=True)
    Start_date = db.Column(db.DateTime(), default=datetime.utcnow())
    End_date = db.Column(db.DateTime())


class Investigate_by(db.Model):
    Officer_id = db.Column(db.String(8), db.ForeignKey(
        "police_officers.Officer_id"), primary_key=True)
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)


class Committed_by(db.Model):
    Criminal_id = db.Column(db.Integer(), db.ForeignKey("criminal.Criminal_id"), primary_key=True)
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)


class victim(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Name = db.Column(db.String(128), primary_key=True, index=True)
    Age = db.Column(db.Integer(), nullable=False)
    Phone_No = db.Column(db.String(11))
    Address = db.Column(db.String(128))

    victimized = db.relationship("Victimized", backref="victim")


class witness(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Name = db.Column(db.String(128), primary_key=True, index=True)
    Age = db.Column(db.Integer(), nullable=False)
    Phone_No = db.Column(db.String(11))
    Address = db.Column(db.String(128))

    witnessed = db.relationship("Witnessed", backref="witness")


class Witnessed(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Name = db.Column(db.String(128), db.ForeignKey("witness.Name"), primary_key=True)


class Victimized(db.Model):
    Case_No = db.Column(db.Integer(), db.ForeignKey("crime.Case_No"), primary_key=True)
    Name = db.Column(db.String(128), db.ForeignKey("victim.Name"), primary_key=True)
