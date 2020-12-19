from flask import Flask , render_template
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
    log_form = LoginForm()
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

        user_obj = Users.query.filter_by(Username=username).first()
        if user_obj:
            return 'Username Exists'

        user = Users(Username=username, Name=fullname, NID_No=nid_no,
            Gender=sex[0], Pass=password, Phone_No=phone_number,
            Personal_email=personal_email, Department_email=dept_email,
            privilege = 0)
        db.session.add(user)
        db.session.commit()
        return render_template('index.html',form=log_form)
    return render_template("Registration_Page.html", form=reg_form)


if __name__ == "__main__":

    app.run(debug=True)
