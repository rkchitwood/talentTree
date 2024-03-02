from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField
from wtforms.validators import InputRequired, Optional, URL, NumberRange, Email, DataRequired, Length, EqualTo

class FirstAdminForm(FlaskForm):
    '''defines fields to allow creation of 1st admin and their organization'''

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=8), EqualTo('password', message='Passwords must match')])
    organization = StringField('Organization', validators=[InputRequired()])

class InviteUserForm(FlaskForm):
    '''defines fields to invite organization members to app'''

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    is_admin = BooleanField("Admin", default = False)

class RegisterUserForm(FlaskForm):
    '''defines fields to allow a user to complete registration and create a full account'''

    password = PasswordField('Password', validators=[Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=8), EqualTo('password', message='Passwords must match')])

class LoginForm(FlaskForm):
    '''defines fields to allow a user to log in'''

    email = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class CompanyForm(FlaskForm):
    '''definees fields to create or edit a company'''
    
    name = StringField('Company Name', validators=[InputRequired()])
    domain = StringField('Domain', validators=[InputRequired(), URL()])

class ProfileForm(FlaskForm):
    '''defines fields to create or edit a profile'''

    #li url, fname, lname, comp-id(domain name unique)