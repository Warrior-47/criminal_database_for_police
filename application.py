from datetime import datetime
from flask import Flask , render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.utils import secure_filename

from wtform_fields import *
from models import *

app = Flask(__name__)  # Creating the server app
app.secret_key = 'replace later'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/criminal_database'   # Connecting to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)   # Creating the database object

log_in = LoginManager(app)   # Configuring flask-login
log_in.init_app(app)


@log_in.user_loader
def load_user(username):
    return Users.query.filter_by(Username=username).first()


# The url of the page. '/' means url will be 127.0.0.1:port/
# index Method is called when '127.0.0.1:port/' this url is used.
@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form= RegistrationForm()   # The form used to make the registration page.

    # Checks if the form was submitted with no ValidationError
    if reg_form.validate_on_submit():

        # Storing the info taken from Registration_Page
        fullname = reg_form.fullname.data
        sex = reg_form.sex.data
        phone_number = reg_form.phone_number.data
        personal_email = reg_form.personal_email.data
        dept_email = reg_form.department_email.data
        nid_no = reg_form.national_id_card_number.data
        rank = reg_form.rank.data
        station = reg_form.station.data
        officer_id = reg_form.officer_id.data
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_pswd = pbkdf2_sha256.hash(password)   # Hashed Password

        # Making Users and police_officers table object to insert into the database
        user = Users(Username=username, Name=fullname, NID_No=nid_no,
            Gender=sex[0], Pass=hashed_pswd, Phone_No=phone_number,
            Personal_email=personal_email, Department_email=dept_email,
            privilege = 0)

        officer = police_officers(Username=username, Officer_id=officer_id,
            Station=station, Rank=rank)

        # Inserting into the database
        db.session.add(user)
        db.session.add(officer)
        db.session.commit()

        flash('Registered successfully. Please Login.', 'success')
        return redirect(url_for('Login'))   # Taking the user to login page when successfully registered.

    return render_template("Registration_Page.html", form=reg_form)   # The html page to load when going to '127.0.0.1:port/'


# login Method is called when '127.0.0.1:port/login' this url is used.
@app.route('/login', methods=['GET', 'POST'])
def Login():
    login_form = LoginForm()   # The form used to make the Login page

    # Checking if the user is logged in or not. If so, redirecting to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Checks if the username and the corresponding passwords exists in the database
    if login_form.validate_on_submit():

        user_obj = Users.query.filter_by(Username=login_form.username.data).first()
        login_user(user_obj)

        ''' Shows the dashboard after successful login '''
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=login_form)   # The html page to load when going to '127.0.0.1:port/login'


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('Logged Out Successfully', 'success')
    return redirect(url_for('Login'))


# login Method is called when '127.0.0.1:port/dashboard' this url is used.
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if not current_user.is_authenticated:

        flash('Please Login first.','danger')

        return redirect(url_for('Login'))

    return render_template('dashboard.html')   # The html page to load when going to '127.0.0.1:port/dashboard'


# login Method is called when '127.0.0.1:port/dashboard/criminals' this url is used.
@app.route('/dashboard/criminals', methods=['GET','POST'])
def showcriminals():
    search = SearchForm()
    if not current_user.is_authenticated:
        flash('Please Login first.','danger')
        return redirect(url_for('Login'))

    if request.method == 'POST':
        crim_id = request.form['update_id']
        crim = criminal.query.filter_by(Criminal_id=crim_id).first()
        if crim:
            photo = request.files['photo']
            photo_name = secure_filename(photo.filename)
            crim.Photo = photo_name
            db.session.merge(crim)
            db.session.commit()
            photo.save('static/criminal_images/'+photo_name)


    stmt = 'Select c.Photo, c.Criminal_id,c.Name,c.Age,c.Nationality,c.Nid_No,c.Motive,c.Phone_No,c.Address,cr.Remark from criminal c, Criminal_Remarks cr where c.Criminal_id = cr.Criminal_id'
    crims = db.session.execute(stmt).fetchall()
    return render_template('dashboard-criminal.html', form=search, data=crims, head=crims[0].keys(), flag='show')


@app.route('/dashboard/criminals/insert', methods=['GET','POST'])
def insert_criminal():
    insert_info = CriminalForm()
    if insert_info.validate_on_submit():
        name = insert_info.name.data
        age = insert_info.age.data
        nationality = insert_info.nationality.data
        motive = insert_info.motive.data
        phone_number = insert_info.phone_number.data
        address = insert_info.address.data
        remark = insert_info.remark.data
        nid_no = insert_info.nid_no.data
        photo_name = secure_filename(insert_info.photo.data.filename)
        insert_info.photo.data.save('static/criminal_images/'+photo_name)

        crim = criminal(Name=name, Age=age, Nationality=nationality,
            Motive=motive, Phone_No=phone_number, Address=address,NID_No=nid_no, Photo=photo_name)
        db.session.add(crim)
        db.session.commit()

        latest_crim = criminal.query.filter_by(NID_No=nid_no).first()
        crim_remark = criminal_remarks(Criminal_id=latest_crim.Criminal_id, Remark=remark)
        db.session.add(crim_remark)
        db.session.commit()

        return redirect(url_for('showcriminals'))

    return render_template('dashboard-criminal.html', flag='insert', form=insert_info)


@app.route('/dashboard/criminals/query', methods=['GET','POST'])
def query():
    search = SearchForm()

    if search.validate_on_submit():
        query = search.query.data
        stmt = "Select Photo, Criminal_id, Name, Age, Nationality, NID_No, Phone_No, Address from criminal where Photo = '"+query+"'"
        data = db.session.execute(stmt).fetchall()
        if data:
            return render_template('dashboard-criminal.html',flag='query', form=search, data=data, head=data[0].keys())

    flash('No Photo Found.', 'danger')
    return redirect(url_for('showcriminals'))

if __name__ == "__main__":
    app.run(debug=True)   # Running the server with Debug mode on
