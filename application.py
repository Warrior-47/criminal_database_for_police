from flask import Flask , render_template, redirect, url_for
from datetime import datetime

from wtform_fields import *
from models import *

app = Flask(__name__)
app.secret_key = 'replace later'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/criminal_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form= RegistrationForm()
    if reg_form.validate_on_submit():
        fullname = reg_form.fullname.data
        sex = reg_form.sex.data
        phone_number = reg_form.phone_number.data
        personal_email = reg_form.personal_email.data
        dept_email = reg_form.department_email.data
        nid_no = reg_form.national_id_card_number.data
        username = reg_form.username.data
        rank = reg_form.rank.data
        station = reg_form.station.data
        officer_id = reg_form.officer_id.data
        password = reg_form.password.data

        user = Users(Username=username, Name=fullname, NID_No=nid_no,
            Gender=sex[0], Pass=password, Phone_No=phone_number,
            Personal_email=personal_email, Department_email=dept_email,
            privilege = 0)

        officer = police_officers(Username=username, Officer_id=officer_id,
            Station=station, Rank=rank)

        db.session.add(user)
        db.session.add(officer)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("Registration_Page.html", form=reg_form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        return 'yay'

    return render_template('index.html', form=login_form)



if __name__ == "__main__":
    app.run(debug=True)
