from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy import DDL
from werkzeug.utils import secure_filename
from flask_caching import Cache

from wtform_fields import *
from models import *
import pickle

app = Flask(__name__)  # Creating the server app
cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'simple'})
app.secret_key = 'replace later'

# Connecting to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/criminal_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 15
app.config['SQLALCHEMY_POOL_RECYCLE'] = 10
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)   # Creating the database object

log_in = LoginManager(app)   # Configuring flask-login
log_in.init_app(app)


@log_in.user_loader
def load_user(username):
    user = 'user_{0}_{1}'.format(username[0], username[1])
    obj = pickle.loads(cache.get(user)) if cache.get(user) else None
    if obj is None:
        query = Users.query.filter_by(Username=username[0]).first()
        obj = pickle.dumps(query)
        cache.set(user, obj, timeout=3600)
        db.session.close()
        return query
    return obj  # Logging in user


# The url of the page. '/' means url will be 127.0.0.1:port/
# index Method is called when '127.0.0.1:port/' this url is used.
@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()   # The form used to make the registration page.

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
                     privilege=0)

        officer = police_officers(Username=username, Officer_id=officer_id,
                                  Station=station, Rank=rank)

        # Inserting into the database
        db.session.add(user)
        db.session.add(officer)
        db.session.commit()
        db.session.close()

        flash('Registered successfully. Please Login.', 'success')
        # Taking the user to login page when successfully registered.
        return redirect(url_for('Login'))

    # The html page to load when going to '127.0.0.1:port/'
    return render_template("Registration.html", form=reg_form)


# login Method is called when '127.0.0.1:port/login' this url is used.
@app.route('/login', methods=['GET', 'POST'])
def Login():
    login_form = LoginForm()   # The form used to make the Login page

    # Checking if the user is logged in or not. If so, redirecting to dashboard
    if current_user.is_authenticated:
        print('asche')
        if current_user.get_id()[1]:
            return redirect(url_for('admin_dashboard'))

        return redirect(url_for('dashboard'))

    # Checks if the username and the corresponding passwords exists in the database
    if login_form.validate_on_submit():

        user_obj = Users.query.filter_by(Username=login_form.username.data).first()
        login_user(user_obj)
        if user_obj.privilege:
            return redirect(url_for('admin_dashboard'))

        return redirect(url_for('dashboard'))

    # The html page to load when going to '127.0.0.1:port/login'
    return render_template('login.html', form=login_form)


# This method allows the user to logout
@app.route('/logout', methods=['GET'])
def logout():
    # So that there is flash message only when user actually logs out
    if not current_user.is_authenticated:
        return redirect(url_for('Login'))

    user = 'user_{}'.format(current_user.get_id()[0])
    cache.delete(user)
    logout_user()

    flash('Logged Out Successfully', 'success')
    return redirect(url_for('Login'))


@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    curr_user = current_user.get_id()
    if not current_user.is_authenticated or not curr_user[1]:
        if curr_user is None or curr_user[1]:
            flash('Please Login first', 'danger')
        return redirect(url_for('Login'))

    dp = ProfileForm()
    if dp.validate_on_submit():
        Name = dp.fullname.data
        sex = dp.sex.data
        personal_email = dp.personal_email.data
        department_email = dp.department_email.data
        phone_number = dp.phone_number.data
        nid = dp.national_id_card_number.data
        rank = dp.rank.data
        station = dp.station.data
        old_pass = dp.old_password.data
        new_pass = dp.new_password.data

        user = Users.query.filter_by(Username=curr_user[0]).first()
        police = police_officers.query.filter_by(Username=curr_user[0]).first()

        if not pbkdf2_sha256.verify(old_pass, user.Pass):
            flash("Password did not Match", "danger")
            return redirect(url_for('admin_dashboard'))

        user.Name = Name
        user.Gender = sex[0]
        user.Personal_email = personal_email
        user.Department_email = department_email
        user.Phone_No = phone_number
        user.NID_No = nid

        if new_pass != '':
            hashed_pass = pbkdf2_sha256.hash(new_pass)
            user.Pass = hashed_pass

        police.Rank = rank
        police.Station = station

        db.session.merge(user)
        db.session.merge(police)
        db.session.commit()

        flash('Updated Successfully', 'success')

    stmt = "SELECT users.Name, users.NID_No, users.Gender, users.Phone_No, users.Personal_email, users.Department_email, police_officers.Officer_id, police_officers.Rank, police_officers.Station, users.privilege FROM users, police_officers where users.Username=police_officers.Username AND users.Username= \'"+curr_user[0] + \
        "'"
    data = db.session.execute(stmt).fetchone()
    db.session.close()

    # The html page to load when going to '127.0.0.1:port/dashboard'
    return render_template('admin-dashboard.html', form_dp=dp, data=data)


# login Method is called when '127.0.0.1:port/dashboard' this url is used.
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Checks if the user is logged in. If not, takes them back to login page.
    if not current_user.is_authenticated:
        flash('Please Login first', 'danger')
        return redirect(url_for('Login'))

    # The html page to load when going to '127.0.0.1:port/dashboard'
    return render_template('dashboard.html')


# login Method is called when '127.0.0.1:port/dashboard/criminals' this url is used.
@app.route('/dashboard/criminals', methods=['GET', 'POST'])
def showcriminals():
    search = SearchForm()
    insert_info = CriminalForm()

    if not current_user.is_authenticated:
        flash('Please Login first.', 'danger')
        return redirect(url_for('Login'))

    if request.method == 'POST':
        # Updating Criminal Photo
        crim_id = request.form['update_id']
        crim = criminal.query.filter_by(Criminal_id=crim_id).first()
        if crim:
            photo = request.files['photo']
            photo_name = secure_filename(photo.filename)
            crim.Photo = photo_name
            db.session.merge(crim)
            db.session.commit()
            db.session.close()
            flash('Updated Successfully', 'success')
            photo.save('static/criminal_images/'+photo_name)
        else:
            flash('No such Criminal', 'danger')

    # Show All criminal Information to Front-end
    stmt = 'Select c.Photo, c.Criminal_id AS "Criminal ID",c.Name,c.Age,c.Nationality,c.Nid_No AS "NID No.",c.Motive,c.Phone_No AS "Phone No.",c.Address,cr.Remark from criminal c left join criminal_remarks cr on c.Criminal_id = cr.Criminal_id'
    res = criminal.query.all()
    crims = db.session.execute(stmt).fetchall()
    db.session.close()
    return render_template('dashboard-criminal.html', form_i=insert_info, form_s=search, data=crims, head=crims[0].keys())


# Route used to insert a Criminal to the database
@app.route('/dashboard/criminals/insert', methods=['POST'])
def insert_criminal():
    insert_info = CriminalForm()

    if insert_info.validate_on_submit():

        # Storing all criminal information about the criminal
        name = insert_info.name.data
        age = insert_info.age.data
        nationality = insert_info.nationality.data
        motive = insert_info.motive.data
        phone_number = insert_info.phone_number.data
        address = insert_info.address.data
        remark = insert_info.remark.data
        nid_no = insert_info.nid_no.data
        photo_name = None

        if insert_info.photo.data:
            photo_name = secure_filename(insert_info.photo.data.filename)
            insert_info.photo.data.save('static/criminal_images/'+photo_name)

        # Inserting criminal into database
        crim = criminal(Name=name, Age=age, Nationality=nationality,
                        Motive=motive, Phone_No=phone_number, Address=address, NID_No=nid_no, Photo=photo_name)
        db.session.add(crim)
        db.session.commit()
        # Inserting the remark for the criminal that was just added if not empty
        if remark != '':
            crim_remark = criminal_remarks(Criminal_id=crim.Criminal_id, Remark=remark)
            db.session.add(crim_remark)
            db.session.commit()
            db.session.close()
        flash('Insert Successful', 'success')

    return redirect(url_for('showcriminals'))


# Route used to query using photo name
@app.route('/dashboard/criminals/query', methods=['GET', 'POST'])
def query():
    search = SearchForm()
    insert_info = CriminalForm()
    if search.validate_on_submit():
        query = search.query.data
        stmt = "Select Photo, Criminal_id, Name, Age, Nationality, NID_No, Phone_No, Address from criminal where Photo = '"+query+"'"
        data = db.session.execute(stmt).fetchall()
        db.session.close()
        if data:
            return render_template('dashboard-criminal.html', form_i=insert_info, form_s=search, data=data, head=data[0].keys())

    flash('No Photo Found', 'danger')
    return redirect(url_for('showcriminals'))


@app.route('/dashboard/profile', methods=['GET', 'POST'])
def display_profile():
    dp = ProfileForm()
    if dp.validate_on_submit():
        Name = dp.fullname.data
        sex = dp.sex.data
        personal_email = dp.personal_email.data
        phone_number = dp.phone_number.data
        old_pass = dp.old_password.data
        new_pass = dp.new_password.data

        user = Users.query.filter_by(Username=current_user.get_id()[0]).first()

        if not pbkdf2_sha256.verify(old_pass, user.Pass):
            flash("Password did not Match", "danger")
            return redirect(url_for('display_profile'))

        user.Name = Name
        user.Gender = sex[0]
        user.Personal_email = personal_email
        user.Phone_No = phone_number

        if new_pass != '':
            hashed_pass = pbkdf2_sha256.hash(new_pass)
            user.Pass = hashed_pass

        db.session.merge(user)
        db.session.commit()

        flash('Updated Successfully', 'success')

    stmt = "SELECT users.Username, users.Name, users.NID_No, users.Gender, users.Phone_No, users.Personal_email, users.Department_email, police_officers.Officer_id, police_officers.Rank, police_officers.Station, users.privilege FROM users, police_officers where users.Username=police_officers.Username AND users.Username= \'"+current_user.get_id()[0] + \
        "'"
    data = db.session.execute(stmt).fetchone()
    db.session.close()

    return render_template('dashboard-profile.html', form_dp=dp, data=data)


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    clr_form = SecurityForm()
    if clr_form.validate_on_submit():
        Officer_id = clr_form.Officer_id.data
        Clearance = clr_form.Clearance.data
        security_obj = police_officers.query.filter_by(Officer_id=Officer_id).first()
        if security_obj:
            security_obj.Clearance = Clearance
            db.session.merge(security_obj)
            db.session.commit()
            stmt = 'Select * from police_officers'
            crims = db.session.execute(stmt).fetchall()
            return redirect(url_for('validate'))

    stmt1 = 'SELECT * from police_officers'
    stmt2 = 'select * from crime'
    pol = db.session.execute(stmt1).fetchall()
    crim = db.session.execute(stmt2).fetchall()
    Off = clr_form.Off.data
    Cas = clr_form.Cas.data
    o1_obj = police_officers.query.filter_by(Officer_id=Off).first()
    p1_obj = crime.query.filter_by(Case_No=Cas).first()
    if o1_obj or p1_obj:
        if o1_obj:
            return redirect(url_for('Search', keys1=Off))
        elif p1_obj:
            return redirect(url_for('Search', keys1=Cas))

    return render_template("admin_security_clearance.html", flag=True, form=clr_form, data1=pol, head1=pol[0].keys(), data2=crim, head2=crim[0].keys())


@app.route('/search/<keys1>', methods=['GET', 'POST'])
def Search(keys1):
    clr_form = SecurityForm()
    o1_obj = police_officers.query.filter_by(Officer_id=keys1).first()
    p1_obj = crime.query.filter_by(Case_No=keys1).first()
    if o1_obj:
        stmt1 = 'Select o.Username,o.Officer_id,o.Station,o.Rank,o.Clearance from Users u, police_officers o where o.Username = u.Username and o.officer_id = "'+keys1+'"'
        pol1 = db.session.execute(stmt1).fetchall()
        return render_template('admin_security_clearance.html', form=clr_form, data=pol1, head=pol1[0].keys(), flag=False)
    elif p1_obj:
        stmt2 = 'Select c.Case_No,i.Officer_id  AS Investigated_By , co.Criminal_id,cr.Name AS Criminal_Name,c.Crime_date,c.End_date,c.Address,c.Clearance from  investigate_by i ,crime c, criminal cr, Committed_by co where c.Case_No = co.Case_No AND cr.Criminal_id = co.Criminal_id AND i.Case_No = co.Case_No AND c.Case_No = "'+keys1+'"'
        crim2 = db.session.execute(stmt2).fetchall()
        return render_template('admin_security_clearance.html', form=clr_form, data=crim2, head=crim2[0].keys(), flag=False)
    return render_template("admin_security_clearance.html", form=clr_form)


@app.route('/show1', methods=['GET', 'POST'])
def Table():
    tb_form = InformationForm()
    if tb_form.validate_on_submit():
        s = tb_form.T_name.data
        if s == 'Officer Information':
            # return render_template("present.html", query=Users.query.all(),form=tb_form,c=1)
            stmt = 'Select o.Username,u.Name,o.Officer_id,u.NID_No,u.Gender,u.Phone_No,u.Personal_email,u.Department_email,o.Station,o.Rank,o.Clearance from Users u, police_officers o where u.username = o.username'
            crims = db.session.execute(stmt).fetchall()
            return render_template('admin_any_table.html', tn=s, data=crims, head=crims[0].keys(), c=2)
        elif s == 'Crime Report':
            stmt = 'Select c.Case_No,i.Officer_id  AS Investigated_By , co.Criminal_id,cr.Name AS Criminal_Name,c.Crime_date,c.End_date,c.Address,c.Clearance from  investigate_by i ,crime c, criminal cr, Committed_by co where c.Case_No = co.Case_No AND cr.Criminal_id = co.Criminal_id AND i.Case_No = co.Case_No'
            crims = db.session.execute(stmt).fetchall()
            return render_template('admin_any_table.html', tn=s, data=crims, head=crims[0].keys(), c=2)
        elif s == "Criminal Report":
            stmt = 'Select c.Photo, c.Criminal_id,c.Name,c.Age,c.Nationality,c.Nid_No,c.Motive,c.Phone_No,c.Address,cr.Remark from criminal c left join Criminal_Remarks cr on c.Criminal_id = cr.Criminal_id'
            crims = db.session.execute(stmt).fetchall()
            return render_template('admin_any_table.html', tn=s, data=crims, head=crims[0].keys(), c=2)
        elif s == 'Medical Team':
            stmt = 'Select * from medical_history'
            crims = db.session.execute(stmt).fetchall()
            return render_template('admin_any_table.html', tn=s, data=crims, head=crims[0].keys(), c=2)

    return render_template('admin_any_table.html', c=1, form=tb_form)


@app.route('/Attr', methods=['GET', 'POST'])
def Attr():
    at_form = AttributeForm()

    return render_template('admin_create_table.html', c=1, form=at_form)


@app.route('/CreateTable', methods=['GET', 'POST'])
def CreateTable():
    at_form = AttributeForm()

    num = at_form.Attr.data
    p = db.engine.table_names()

    if request.method == "POST":
        name = request.form.get('name')
        column_names = request.form.getlist('at')
        column_types = request.form.getlist('op')
        column_len = request.form.getlist('ta')
        if name and name.lower() in p:
            flash("Table Already Exists", 'danger')
            return render_template('admin_create_table.html', c=1, form=at_form)

        if num is None:
            """table create"""

            stmt = f'Create Table {name} ( Case_No INT, '
            for index, (name, type, length) in enumerate(zip(column_names, column_types, column_len)):
                if type == 'VARCHAR':
                    stmt += name + ' ' + type + \
                        f'({length}),' if index < len(column_names) - \
                        1 else name + ' ' + type + f'({length})'
                else:
                    stmt += name + ' ' + type + \
                        ',' if index < len(column_names) - 1 else name + ' ' + type
            stmt += " , FOREIGN KEY(Case_No) REFERENCES Crime(Case_No) ON UPDATE CASCADE ON DELETE CASCADE" + ');'

            db.session.execute(stmt)
            db.session.commit()
            flash("Table Created", "success")
            return redirect(url_for('Attr'))

        return render_template('admin_create_table.html', num=num, c=2, form=at_form)
    return redirect(url_for('Attr'))


@app.route('/AddColumn', methods=['GET', 'POST'])
def AddColumn():
    all_table = db.engine.table_names()
    if request.method == 'POST':
        Tname = request.form.get('name')
        column_name = request.form.get('at')
        column_type = request.form.get('op')
        column_len = request.form.get('ta')

        if Tname in all_table:
            # findimg all meta data of a table
            stmt2 = "Select * from "+Tname
            crim2 = db.session.execute(stmt2).fetchall()
            column = (crim2[0].keys())
            all_column = [item.lower() for item in column]

            if (column_name.lower()) in all_column:
                flash("Column Exists. Try Again", 'danger')
            else:
                stmt = "ALTER TABLE " + Tname + " ADD " + column_name + \
                    " " + column_type + "(" + column_len + ");"
                add_column = DDL(stmt)
                db.engine.execute(add_column)
                flash("Column Added.", 'success')
        else:
            flash("Table does not Exist. Try Again", 'danger')
            return redirect(url_for('AddColumn'))
    return render_template('admin_addcolumn.html')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    db.engine.dispose()


if __name__ == "__main__":
    app.run(debug=True)   # Running the server with Debug mode on
