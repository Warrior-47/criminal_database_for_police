from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    """ Registration Form """
    choice = ['Male', 'Female']

    fullname = StringField('fullname_label' , validators=[InputRequired(message="Input required")])
    password = PasswordField('password_label',validators=[InputRequired(message="Input required")])
    confirm_pswd = PasswordField('confirm_pswd_label',validators=[InputRequired(message="Input required"), EqualTo('password', message='Password doesn\'t match.')])
    personal_email = StringField('personal_email_label',validators=[InputRequired(message="Input required")])
    department_email = StringField('department_email_label',validators=[InputRequired(message="Input required")])
    sex = SelectField(u'Choose',choices=choice)
    phone_number = StringField('phone_number_label',validators=[InputRequired(message="Input required")])
    national_id_card_number = IntegerField('national_id_card_number_label',validators=[InputRequired(message="Input required")])
    username = StringField('username_label',validators=[InputRequired(message="Input required")])
    rank = StringField('rank_label',validators=[InputRequired(message="Input required")])
    station = StringField('station_label',validators=[InputRequired(message="Input required")])
    officer_id = StringField('officer_id_label',validators=[InputRequired(message="Input required")])
    submit_button = SubmitField('Register')

class LoginForm(FlaskForm):

    username = StringField('username_label',validators=[InputRequired(message="Input required")])
    password = PasswordField('password_label',validators=[InputRequired(message="Input required")])
    submit_button = SubmitField('Login')
