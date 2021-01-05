from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Email, NumberRange
from passlib.hash import pbkdf2_sha256
from models import Users, police_officers, criminal


def validate_credentials(form, field):
    """
    This is checking the login info given by using, and checking
    if the database contains the user and if the password provided
    is the correct password.

    """
    username_e = form.username.data
    pswd = field.data
    user_obj = Users.query.filter_by(Username=username_e).first()
    if user_obj is None:
        raise ValidationError("Username or Password do not match.")
    elif not pbkdf2_sha256.verify(pswd, user_obj.Pass):
        raise ValidationError("Username or Password do not match.")


class ProfileForm(FlaskForm):

    choice = [(0,'Male'), (1,'Female')]

    fullname = StringField('fullname_label', validators=[
                           Length(max=128, message='Name is too long')])

    sex = SelectField(u'Choose', choices=choice)

    personal_email = StringField('personal_email_label', validators=[
                                 Email('Not a Valid Email'), Length(max=128, message='Email is too long')])

    department_email = StringField('department_email_label')

    phone_number = StringField('phone_number_label')

    national_id_card_number = IntegerField('national_id_card_number_label')

    rank = StringField('rank_label')

    station = StringField('station_label')

    officer_id = StringField('officer_id_label')

    old_password = PasswordField('password_label', validators=[
                                 InputRequired()])

    new_password = PasswordField('password_label')

    confirm_pswd = PasswordField('confirm_pswd_label', validators=[
                                 EqualTo('new_password', message='Password does not match.')])

    update_button = SubmitField('Update')


class RegistrationForm(FlaskForm):
    """
    This the where all the info from the Registration_Page gets store in.
    All the different attributes are each a input field in Registration_Page
    See the Registration_Page.html file to see how they are connected

    """
    sex_choice = ['Sex:', 'Male', 'Female']
    rank_choice = ['Rank:', 'Inspector General of Police','Additional Inspector General of Police','Deputy Inspector General of Police','Additional Deputy Inspector General of Police','Superintendent of Police','Additional Superintendent of Police','Senior Assistant Superintendent of Police','Assistant Superintendent of Police','Inspector','Sub Inspector','Sergent','Assisteant Sub Inspector','Nayek','Constable']

    fullname = StringField('fullname_label', validators=[
                           InputRequired(), Length(max=128, message='Name is too long')])

    password = PasswordField('password_label', validators=[InputRequired(), Length(
        min=3, max=25, message='Password should be between 3 and 25 characters long.')])

    confirm_pswd = PasswordField('confirm_pswd_label', validators=[
                                 InputRequired(), EqualTo('password', message='Password doesn\'t match.')])

    personal_email = StringField('personal_email_label', validators=[
                                 InputRequired(), Email('Not a Valid Email Address.'), Length(max=128, message='Email is too long')])

    department_email = StringField('department_email_label', validators=[
                                   InputRequired(), Email('Not a Valid Email Address.'), Length(max=128, message='Email is too long')])

    sex = SelectField(u'Choose', choices=sex_choice)

    phone_number = StringField('phone_number_label', validators=[
                               InputRequired(), Length(max=11, message='No need for "+88". Phone number can only be 11 characters long.')])

    national_id_card_number = StringField(
        'national_id_card_number_label', validators=[InputRequired(), Length(max=10, message='Invalid NID number.')])

    username = StringField('username_label', validators=[
                           InputRequired(), Length(max=128, message='Username too long.')])

    rank = SelectField(u'Choose', choices=rank_choice)

    station = StringField('station_label', validators=[
                          InputRequired(), Length(max=32, message='Invalid Station.')])

    officer_id = StringField('officer_id_label', validators=[
                             InputRequired(), Length(max=8, message='Invalid Officer ID.')])

    submit_button = SubmitField('Register')

    def validate_officer_id(self, officer_id):
        user_obj = police_officers.query.filter_by(
            Officer_id=officer_id.data).first()
        if user_obj:
            raise ValidationError("Officer ID Already Exists.")

    def validate_national_id_card_number(self, national_id_card_number):
        if not national_id_card_number.data.isnumeric():
            raise ValidationError("NID number is numeric only.")

        user_obj = Users.query.filter_by(
            NID_No=national_id_card_number.data).first()
        if user_obj:
            raise ValidationError("NID Already in Use.")

    def validate_personal_email(self, personal_email):
        user_obj = Users.query.filter_by(
            Personal_email=personal_email.data).first()
        if user_obj:
            raise ValidationError("Account Already Registered.")

    def validate_department_email(self, department_email):
        if department_email.data == self.personal_email.data:
            raise ValidationError(
                "Personal and Department Email cannot be same.")
        user_obj = Users.query.filter_by(
            Department_email=department_email.data).first()
        if user_obj:
            raise ValidationError("Account Already Registered.")

    def validate_username(self, username):
        """
        This is validating if the username already exists in the database. If so, raises an ValidationError
        and form is not submitted.

        """
        user_obj = Users.query.filter_by(Username=username.data).first()
        if user_obj:
            raise ValidationError("Username Already Exists. Choose Another.")

    def validate_sex(self, sex):
        if sex.data == 'Sex:':
            raise ValidationError("You must choose")

    def validate_rank(self, rank):
        if rank.data == 'Rank:':
            raise ValidationError("You must choose")


class LoginForm(FlaskForm):
    """
    This the where all the info from the login page gets store in.
    All the different attributes are each a input field in login page.
    See the login.html file to see how they are connected

    """
    username = StringField('username_label', validators=[InputRequired()])
    password = PasswordField('password_label', validators=[
        InputRequired(), validate_credentials])
    submit_button = SubmitField('Sign in')


class CriminalForm(FlaskForm):
    """
    This the where all the info to store a criminal in database is first store in.

    """
    name = StringField('name_label', validators=[
                       InputRequired(), Length(max=128,  message='Name too Long.')])

    age = IntegerField('age_label', validators=[InputRequired(), NumberRange(
        min=10, max=130, message='Criminal too Young or too Old')])

    nationality = StringField('nationality_label', validators=[
                              Length(max=32, message='Invalid Nationality')])

    nid_no = StringField('nid_label', validators=[
                         Length(max=10, message='Invalid NID number.')])

    motive = StringField('motive_label', validators=[
                         Length(max=64, message='Motive too Long.')])

    phone_number = StringField('phone_number_label', validators=[Length(
        max=11, message='No need for "+88". Phone number can only be 11 characters long.')])

    address = StringField('address_label', validators=[
                          Length(max=128, message='Address too Long.')])

    remark = StringField('remark_label', validators=[
                         Length(max=64, message='Remark is too Long.')])

    photo = FileField('photo_label')

    submit_button = SubmitField('Submit')

    def validate_nid_no(self, nid_no):
        if not nid_no.data.isnumeric():
            flash('Insert Failed', category='danger')
            raise ValidationError("NID number is numeric only.")

        user_obj = criminal.query.filter_by(
            NID_No=nid_no.data).first()
        if user_obj:
            flash('Insert Failed', category='danger')
            raise ValidationError("NID Already in Use.")


class SearchForm(FlaskForm):
    """
    Used for search queries

    """
    query = StringField('query_label', validators=[InputRequired()])
    search = SubmitField('Search')


class SecurityForm(FlaskForm):
    choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    Off = StringField('Offier_id_label')
    Cas = StringField('Case_No_label')
    Officer_id = StringField('Offier_id_label')
    Clearance = SelectField(u'Choose', choices=choice)
    submit_button = SubmitField()


class InformationForm(FlaskForm):
    choice = ['Choose One', 'Officer Information',
              'Crime Report', 'Criminal Report', 'Medical Team']

    T_name = SelectField(u'Choose', choices=choice)
    submit_button = SubmitField('Click Here')


class AttributeForm(FlaskForm):
    Attr = IntegerField('Attr_label', validators=[InputRequired()])
    submit_button = SubmitField('Click Here')


class LookIntoForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired()])
    submit_button = SubmitField('Submit')


class UpdateForm(FlaskForm):

    choice = ['Male', 'Female']

    fullname = StringField('fullname_label')
    sex = SelectField(u'Choose', choices=choice)
    personal_email = StringField('personal_email_label', validators=[
                                 Email('Not a valid email')])
    department_email = StringField('department_email_label', validators=[
                                   Email('Not a valid email')])
    phone_number = StringField('phone_number_label')
    national_id_card_number = IntegerField('national_id_card_number_label')
    rank = StringField('rank_label')
    station = StringField('station_label')
    officer_id = StringField('officer_id_label')
    update_button = SubmitField('Update')
