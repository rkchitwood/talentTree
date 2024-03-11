from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Optional, URL, Email, DataRequired, Length, EqualTo, ValidationError

def validate_functions(form, field):
    if not field.data or len(field.data) == 0:
        raise ValidationError('At least one function must be selected.')
    
def validate_end_date(form, field):
    is_current = form.is_current.data
    end_date = field.data
    if is_current:
        if not end_date:
            raise ValidationError('End date required for current roles')

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

    #profile fields

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    linkedin_url = StringField('LinkedIn URL', validators=[InputRequired(), URL()])    
    headline = StringField('Headline (Optional)', validators=[Optional()])

    #role fields

    function_choices = [('Executive', 'Executive'), 
                    ('Finance', 'Finance'), 
                    ('Operations', 'Operations'), 
                    ('Engineering', 'Engineering'), 
                    ('Product','Product'), 
                    ('Sales', 'Sales'), 
                    ('Security', 'Security'), 
                    ('Marketing', 'Marketing'), 
                    ('Human Resources', 'Human Resources'), 
                    ('Customer Services', 'Customer Services'),
                    ('Founder', 'Founder')
                    ]
    level_choices = [('Chief', 'Chief'), 
                ('President', 'President'), 
                ('Executive Vice President', 'Executive Vice President'), 
                ('Senior Vice President', 'Senior Vice President'),
                ('Vice President', 'Vice President'),
                ('Associate Vice President', 'Associate Vice President'),
                ('Head', 'Head'),
                ('Partner', 'Partner'),
                ('Senior Director', 'Senior Director'),
                ('Director', 'Director'),
                ('Associate Director', 'Associate Director'),
                ('Senior Manager', 'Senior Manager'),
                ('Manager', 'Manager'),
                ('Senior Associate', 'Senior Associate'),
                ('Associate', 'Associate'),
                ('Senior Analyst', 'Senior Analyst'),
                ('Junior', 'Junior')
                ]
    us_state_codes = [
    (None, "Select State (optional)"), ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"), ("CA", "California"),
    ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"), ("FL", "Florida"), ("GA", "Georgia"),
    ("HI", "Hawaii"), ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
    ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"), ("MA", "Massachusetts"),
    ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"),
    ("NE", "Nebraska"), ("NV", "Nevada"), ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"),
    ("NY", "New York"), ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"),
    ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"), ("SD", "South Dakota"),
    ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
    ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming")
]
    country_codes = [('', 'Select Country'), ('USA', 'United States'), ('GBR', 'United Kingdom')]
    
    level = SelectField('Primary Level', choices=level_choices, validators=[InputRequired()])
    functions = SelectMultipleField('Primary Functions', choices=function_choices, validators=[validate_functions])
    start_date = DateField('Primary Start Date', validators=[InputRequired()])
    company = StringField('Primary Company Domain', validators=[URL(), InputRequired()])
    city = StringField('City (optional)', validators=[Optional()])
    state = SelectField('State', choices=us_state_codes, validators=[Optional()])
    country = SelectField('Country', choices=country_codes, validators=[InputRequired()])

class MapForm(FlaskForm):
    '''defines fields to create or edit a contact map'''
#name, level, functions, companies
    
    level_choices = [('Chief', 'Chief'), 
            ('President', 'President'), 
            ('Executive Vice President', 'Executive Vice President'), 
            ('Senior Vice President', 'Senior Vice President'),
            ('Vice President', 'Vice President'),
            ('Associate Vice President', 'Associate Vice President'),
            ('Head', 'Head'),
            ('Partner', 'Partner'),
            ('Senior Director', 'Senior Director'),
            ('Director', 'Director'),
            ('Associate Director', 'Associate Director'),
            ('Senior Manager', 'Senior Manager'),
            ('Manager', 'Manager'),
            ('Senior Associate', 'Senior Associate'),
            ('Associate', 'Associate'),
            ('Senior Analyst', 'Senior Analyst'),
            ('Junior', 'Junior')
            ]
    function_choices = [('Executive', 'Executive'), 
                ('Finance', 'Finance'), 
                ('Operations', 'Operations'), 
                ('Engineering', 'Engineering'), 
                ('Product','Product'), 
                ('Sales', 'Sales'), 
                ('Security', 'Security'), 
                ('Marketing', 'Marketing'), 
                ('Human Resources', 'Human Resources'), 
                ('Customer Services', 'Customer Services'),
                ('Founder', 'Founder')
                ]

    name = StringField('Contact Map Name', validators=[InputRequired()])
    level = SelectField('Level', choices=level_choices, validators=[InputRequired()])
    functions = SelectMultipleField('Functions', choices=function_choices, validators=[validate_functions])
    companies = StringField('Companies', validators=[InputRequired()])